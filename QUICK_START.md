# Quick Start Guide

## For Developers

### Option 1: Local Development (Fastest Start)

#### 1. Prerequisites
- Docker Desktop installed
- 8GB+ RAM available
- Port 3000, 5000, 5432, 6379 available

#### 2. Clone Repository
```bash
cd bunkerbuster
git clone https://github.com/yourusername/bunkerbuster.git
cd bunkerbuster
```

#### 3. Start Stack
```bash
docker-compose up -d
```

Wait 30 seconds for services to initialize, then:

#### 4. Access Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:5000/api/health
- Database UI: http://localhost:5050
- Redis UI: http://localhost:8081

#### 5. Real-time Data
Open browser console and test WebSocket:
```javascript
const socket = io('http://localhost:5000');
socket.emit('aircraft:subscribe');
socket.on('aircraft:update', (data) => console.log(data));
```

### Option 2: Without Docker

#### Frontend
```bash
cd frontend
npm install
npm start  # Runs on http://localhost:3000
```

#### Backend
```bash
cd backend
npm install
npm run dev  # Runs on http://localhost:5000
```

#### Database (Manual)
```bash
# Install PostgreSQL locally, then:
createdb bunkerbuster
psql -d bunkerbuster -f backend/migrations/init.sql

# Install Redis locally
redis-server
```

#### AI Agents
```bash
cd ai-agents
pip install -r requirements.txt
python main.py
```

## For System Operators

### Monitoring the System

```bash
# Check service health
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f worker

# Database stats
docker exec bunkerbuster-postgres psql -U postgres -d bunkerbuster \
  -c "SELECT count(*) FROM aircraft_positions;"

# Redis memory
docker exec bunkerbuster-redis redis-cli INFO memory
```

### Common Operations

**Restart all services:**
```bash
docker-compose restart
```

**Stop everything:**
```bash
docker-compose down
```

**Wipe data and start fresh:**
```bash
docker-compose down -v  # -v removes volumes
docker-compose up -d
```

**View database:**
```bash
docker exec -it bunkerbuster-postgres psql -U postgres -d bunkerbuster
```

### Backup Data

```bash
# Backup database
docker exec bunkerbuster-postgres pg_dump -U postgres bunkerbuster | gzip > db_backup.sql.gz

# Restore
gunzip < db_backup.sql.gz | docker exec -i bunkerbuster-postgres psql -U postgres bunkerbuster
```

## Understanding the Data Flow

```
1. RAW DATA INGESTION (Python)
   ↓
   AI Agents continuously poll:
   - ADS-B Exchange API (aircraft)
   - CelesTrak (satellites)
   - News feeds / Twitter
   ↓
   
2. REDIS PUB/SUB (Real-time)
   ↓
   Data published to channels:
   - bunkerbuster:aircraft:updates
   - bunkerbuster:satellites:updates
   - bunkerbuster:events:new
   ↓
   
3. BACKEND PROCESSING (Node.js)
   ↓
   - Subscribes to Redis channels
   - Stores in PostgreSQL (history)
   - Broadcasts via WebSocket
   ↓
   
4. FRONTEND VISUALIZATION (React + Cesium)
   ↓
   - Receives real-time updates
   - Renders on 3D globe
   - Updates statistics panels
   ↓
   
5. USER SEES LIVE UPDATES
```

## File Structure Quick Reference

```
bunkerbuster/
├── frontend/               React + Cesium.js UI
│   ├── src/App.tsx        Main 3D globe component
│   └── src/components/    UI panels
├── backend/               Express.js API
│   ├── src/index.ts       Server entry point
│   └── src/services/      Database, Redis, WebSocket
├── ai-agents/             Python intelligence agents
│   ├── agents/            Individual agent implementations
│   └── main.py            Agent swarm coordinator
├── data-pipelines/        Data collection orchestration
├── docs/                  Documentation
├── docker-compose.yml     Container stack definition
└── README.md              This file
```

## Troubleshooting

**Frontend shows blank globe:**
- Check browser console for errors
- Verify backend is running: `curl http://localhost:5000/api/health`
- Check that Cesium Ion token is valid

**No aircraft/ship data appearing:**
- Start Docker Desktop if not running (daemon error)
- `docker-compose up -d`
- Check logs: `docker logs bunkerbuster-backend` (should see ⛴️ Ships: X ships updated)
- Backend now includes mock AIS ships (12 vessels in Gibraltar Strait, realistic movement)
- Verify API: `curl http://localhost:5000/api/ships`
- Check PostgreSQL: `docker exec bunkerbuster-postgres psql -U postgres -d bunkerbuster -c "SELECT COUNT(*) FROM ship_positions;"`
- Frontend: `cd frontend && npm install && npm start` then http://localhost:3000

**High memory usage:**
- Check TimescaleDB compression: `docker exec bunkerbuster-postgres psql -U postgres -c "SELECT * FROM timescaledb_information.hypertables;"`
- Reduce data retention: Update background job to delete data older than X days
- Scale Redis: Use Redis cluster mode

**API returning 500 errors:**
- Check database connection: `docker exec bunkerbuster-backend npm run migra...`
- Check connection string: `env $(cat .env | xargs) npm run --prefix backend dev`
- View detailed logs: `docker logs -f bunkerbuster-backend`

## Performance Tips

### Development
- Use Chrome DevTools Performance tab to profile Cesium rendering
- Mock data from files instead of live APIs during testing
- Run only the services you need: `docker-compose up backend postgres redis`

### Production
- Enable PostgreSQL query logging to identify slow queries
- Use Redis for caching frequent API queries
- Implement Cesium entity clustering for 10k+ objects
- Use CDN for frontend static assets

## Next Steps

1. **Add Custom AOI**: Use API to create Areas of Interest
2. **Configure Alerts**: Set up email/Slack notifications for events
3. **Connect Premium APIs**: Link Maxar or FlightAware accounts
4. **Deploy to Cloud**: See DEPLOYMENT.md for AWS/GCP setup
5. **Customize Agents**: Modify Python agents to add your own logic

---

Need help? Check ARCHITECTURE.md for design details or see docs/ folder for full documentation.
