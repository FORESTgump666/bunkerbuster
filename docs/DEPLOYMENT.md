# BunkerBuster Deployment Guide

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (if developing without Docker)
- Python 3.10+ (if developing without Docker)

### 1. Clone and Setup
```bash
cd bunkerbuster
cp backend/.env.example backend/.env
```

### 2. Start Services with Docker Compose
```bash
docker-compose up -d
```

This starts:
- PostgreSQL + TimescaleDB (port 5432)
- Redis (port 6379)
- Backend API (port 5000)
- Frontend (port 3000)
- AI Agents (background worker)

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api/health
- **PgAdmin**: http://localhost:5050 (admin@bunkerbuster.local / admin)
- **Redis Commander**: http://localhost:8081

## Production Deployment

### Option A: Cloud (AWS EC2 + RDS)

#### 1. Create EC2 Instance
```bash
aws ec2 run-instances \
  --instance-type t3.large \
  --image-id ami-0c55b159cbfafe1f0 \
  --security-groups bunkerbuster-sg \
  --key-name your-key
```

#### 2. Install Docker
```bash
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -aG docker ec2-user
```

#### 3. Create RDS PostgreSQL
```bash
aws rds create-db-instance \
  --db-instance-identifier bunkerbuster-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password $(openssl rand -base64 32) \
  --storage-type gp3 \
  --allocated-storage 100
```

#### 4. ElastiCache for Redis
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id bunkerbuster-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --engine-version 7.0
```

#### 5. Deploy Services
```bash
# Pull docker images
docker pull bunkerbuster-backend:latest
docker pull bunkerbuster-worker:latest

# Run backend
docker run -d \
  --name bunkerbuster-backend \
  -p 5000:5000 \
  -e DB_HOST=<rds-endpoint> \
  -e REDIS_HOST=<elasticache-endpoint> \
  bunkerbuster-backend:latest
```

### Option B: Kubernetes (EKS / GKE)

#### 1. Create Cluster
```bash
# AWS EKS
eksctl create cluster --name bunkerbuster --region us-east-1 --nodes 3

# Or Google Cloud
gcloud container clusters create bunkerbuster --num-nodes 3
```

#### 2. Create Helm Chart
```yaml
# helm/values.yaml
image:
  backend: bunkerbuster-backend:1.0.0
  worker: bunkerbuster-worker:1.0.0

replicas:
  backend: 2
  worker: 3

postgres:
  enabled: true
  size: 100Gi

redis:
  enabled: true
```

#### 3. Deploy
```bash
helm install bunkerbuster ./helm
kubectl get pods --watch
```

### Option C: Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml bunkerbuster

# Check status
docker stack ps bunkerbuster
```

## Environment Configuration

### Production `.env`
```bash
NODE_ENV=production
PORT=5000
FRONTEND_URL=https://bunkerbuster.yourdomain.com

# Database (RDS)
DB_HOST=bunkerbuster-db.c9akciq32.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=bunkerbuster
DB_USER=admin
DB_PASSWORD=<STRONG_PASSWORD>
DB_POOL_SIZE=30

# Redis (ElastiCache)
REDIS_HOST=bunkerbuster.abc123.ng.0001.use1.cache.amazonaws.com
REDIS_PORT=6379

# JWT
JWT_SECRET=<GENERATE_STRONG_SECRET>
JWT_EXPIRY=7d

# SSL/TLS
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
DATADOG_API_KEY=<your-datadog-key>
```

## Monitoring & Observability

### Health Checks
```bash
# Backend health
curl http://localhost:5000/api/health

# Database
psql -h localhost -U postgres -d bunkerbuster -c "SELECT version();"

# Redis
redis-cli PING
```

### Logs
```bash
# Backend logs
docker logs -f bunkerbuster-backend

# Worker logs
docker logs -f bunkerbuster-worker

# PostgreSQL
tail -f /var/lib/pgsql/data/pg_log/postgresql.log
```

###Monitoring Tools
- **Prometheus**: Scrape metrics from `/metrics`
- **Grafana**: Visualize metrics
- **ELK Stack**: Centralized logging
- **DataDog**: APM and monitoring
- **Sentry**: Error tracking

## Backup & Disaster Recovery

### PostgreSQL Backups
```bash
# Full backup
pg_dump -h localhost -U postgres bunkerbuster | gzip > backup.sql.gz

# Automated daily backups (cron)
0 2 * * * pg_dump -h localhost -U postgres bunkerbuster | gzip > /backups/$(date +\%Y\%m\%d).sql.gz

# Restore
gunzip /backups/20260318.sql.gz | psql -h localhost -U postgres bunkerbuster
```

### Redis Persistence
```bash
# Already enabled in docker-compose
# RDB snapshots: /data/dump.rdb
# AOF: /data/appendonly.aof
```

### Database Replication
```bash
# Primary-Replica setup
# Replica reads from primary for fault tolerance
```

## Scaling

### Horizontal Scaling
```bash
# Scale backend replicas
docker-compose up -d --scale backend=3

# Load balance with Nginx
upstream backend {
    server backend:5000;
    server backend:5001;
    server backend:5002;
}
```

### Vertical Scaling
```yaml
# docker-compose.yml
backend:
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1'
```

## Security Hardening

### 1. Network Security
- Enable VPC security groups
- Restrict DB access to app subnet only
- Use VPN for admin access

### 2. Application Security
```bash
# Enable HTTPS
docker run -e SSL_ENABLED=true -v /certs:/app/certs bunkerbuster-backend

# API Rate Limiting (already in Express)
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
}));
```

### 3. Data Protection
- Enable encryption at rest: RDS, Redis, EBS
- Enable encryption in transit: TLS 1.2+
- Rotate secrets quarterly

### 4. Access Control
- IAM roles for AWS services
- RBAC for Kubernetes
- API key rotation

## Troubleshooting

### Backend won't connect to DB
```bash
# Check connection
docker exec bunkerbuster-backend nc -zv postgres 5432

# Check credentials
docker exec -it bunkerbuster-postgres psql -U postgres -c "\l"
```

### High Redis memory usage
```bash
# Check memory
redis-cli INFO memory

# Cleanup eviction
redis-cli FLUSHDB
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Slow API responses
```bash
# Check slow queries
docker exec bunkerbuster-backend npx knex migrate:rollback

# Index optimization
psql -c "REINDEX INDEX aircraft_positions_icao_idx;"
```

## Rollback Procedure

```bash
# Save current version
git tag deployment-v1.0.0

# If there's an issue, rollback
git checkout deployment-v0.9.9
docker-compose build
docker-compose up -d
```

## Cost Estimation (Monthly)

| Service | Tier | Cost |
|---------|------|------|
| AWS EC2 (t3.large) | On-demand | $70 |
| RDS PostgreSQL (db.t3.micro) | Multi-AZ | $50 |
| ElastiCache Redis | cache.t3.micro | $30 |
| Data Transfer Out | First 1GB free | $20 |
| Domain + SSL | Annual | $12 |
| **Total** | | **~$182/month** |

Free tier can support MVP with ~500 concurrent users.

---

**Last Updated**: March 2026
