@echo off
REM Production deployment script for UAV Service Management Tool (Windows)

echo 🚀 Starting UAV Service Management Tool deployment...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Build and start the application
echo 📦 Building Docker image...
docker-compose build

echo 🏃 Starting services...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check if services are healthy
echo 🔍 Checking service health...
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ Services are running!
    echo.
    echo 🌐 Your UAV Service Management Tool is available at:
    echo    - http://localhost:5000 ^(Direct app access^)
    echo    - http://localhost:80 ^(With Nginx - if using production profile^)
    echo.
    echo 📊 To view logs:
    echo    docker-compose logs -f
    echo.
    echo 🛑 To stop services:
    echo    docker-compose down
) else (
    echo ❌ Services failed to start. Check logs:
    docker-compose logs
    pause
    exit /b 1
)

pause
