# BunkerBuster Windows Setup

@echo off
setlocal enabledelayedexpansion

echo ╔════════════════════════════════════════════════╗
echo ║   🌍 BunkerBuster Automated Setup Script       ║
echo ╚════════════════════════════════════════════════╝
echo.

REM Check prerequisites
echo 📋 Checking prerequisites...

docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed
    exit /b 1
)

echo ✅ Docker and Docker Compose found
echo.

REM Create .env if it doesn't exist
echo ⚙️  Setting up environment...
if not exist "backend\.env" (
    copy backend\.env.example backend\.env
    echo ✅ Created backend\.env from template
) else (
    echo ℹ️  backend\.env already exists
)

REM Create directories
echo 📁 Creating required directories...
if not exist "backend\logs" mkdir backend\logs
if not exist "data\postgres" mkdir data\postgres
if not exist "data\redis" mkdir data\redis
echo ✅ Directories created
echo.

REM Start services
echo 🚀 Starting services...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    exit /b 1
)

echo.
echo ⏳ Waiting for services to be healthy...
timeout /t 10 /nobreak

echo 🏥 Checking service health...
timeout /t 10 /nobreak

echo.
echo ╔════════════════════════════════════════════════╗
echo ║   ✅ BunkerBuster is Ready!                   ║
echo ╚════════════════════════════════════════════════╝
echo.
echo 🌐 Frontend:        http://localhost:3000
echo 📡 Backend API:     http://localhost:5000
echo 🔧 API Health:      http://localhost:5000/api/health
echo 🗄️  Database UI:     http://localhost:5050
echo    Email: admin@bunkerbuster.local
echo    Password: admin
echo 🔴 Redis Explorer:  http://localhost:8081
echo.
echo 📚 Documentation:   See docs\ folder
echo 🚀 Quick Start:     See QUICK_START.md
echo.
echo 📋 Showing logs...
docker-compose logs -f backend

endlocal
