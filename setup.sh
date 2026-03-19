
#!/bin/bash
# BunkerBuster Quick Setup Script

set -e

echo "╔════════════════════════════════════════════════╗"
echo "║   🌍 BunkerBuster Automated Setup Script       ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Create .env if it doesn't exist
echo "⚙️  Setting up environment..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from template"
else
    echo "ℹ️  backend/.env already exists"
fi

# Create directories
echo "📁 Creating required directories..."
mkdir -p backend/logs
mkdir -p data/postgres
mkdir -p data/redis
echo "✅ Directories created"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

health_check() {
    local service=$1
    local cmd=$2
    if eval "$cmd" > /dev/null 2>&1; then
        echo "✅ $service is healthy"
        return 0
    else
        echo "⚠️  $service is initializing..."
        return 1
    fi
}

for i in {1..30}; do
    postgres_ok=0
    redis_ok=0
    backend_ok=0
    
    health_check "PostgreSQL" "docker exec bunkerbuster-postgres pg_isready -U postgres" || postgres_ok=1
    health_check "Redis" "docker exec bunkerbuster-redis redis-cli ping > /dev/null" || redis_ok=1
    health_check "Backend" "curl -s http://localhost:5000/api/health > /dev/null" || backend_ok=1
    
    if [ $postgres_ok -eq 0 ] && [ $redis_ok -eq 0 ] && [ $backend_ok -eq 0 ]; then
        break
    fi
    
    sleep 2
done

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║   ✅ BunkerBuster is Ready!                   ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "🌐 Frontend:        http://localhost:3000"
echo "📡 Backend API:     http://localhost:5000"
echo "🔧 API Health:      http://localhost:5000/api/health"
echo "🗄️  Database UI:     http://localhost:5050"
echo "   Email: admin@bunkerbuster.local"
echo "   Password: admin"
echo "🔴 Redis Explorer:  http://localhost:8081"
echo ""
echo "📚 Documentation:   See docs/ folder"
echo "🚀 Quick Start:     See QUICK_START.md"
echo ""

# Show logs
echo "📋 Tailing logs (Ctrl+C to exit)..."
docker-compose logs -f backend
