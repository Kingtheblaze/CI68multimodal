# Setup script for Multimodal Graph RAG (API Key Version)
Write-Host "Checking Docker status..." -ForegroundColor Cyan
docker version >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker is not running. Please start Docker Desktop and try again."
    exit
}

Write-Host "Starting E-Commerce Intelligence services..." -ForegroundColor Cyan
docker-compose up -d --build

Write-Host "Waiting for services to initialize (Weaviate & Neo4j)..." -ForegroundColor Green
# Give it enough time to start schemas
Start-Sleep -Seconds 15

Write-Host "Seeding Multimodal E-Commerce Data..." -ForegroundColor Cyan
python backend/ingest_data.py

Write-Host "------------------------------------------------" -ForegroundColor White
Write-Host "System is ready!" -ForegroundColor Green
Write-Host "Frontend Dashboard: http://localhost:3000"
Write-Host "Backend API Docs:   http://localhost:8000/docs"
Write-Host "Neo4j Explorer:     http://localhost:7474 (Login: neo4j/password)"
Write-Host "------------------------------------------------" -ForegroundColor White
