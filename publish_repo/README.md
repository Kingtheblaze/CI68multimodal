# Multimodal Graph RAG

This project is a full-stack multimodal Graph RAG application with:

- `Frontend`: Next.js UI
- `Backend`: FastAPI API
- `Graph DB`: Neo4j
- `Vector DB`: Weaviate
- `LLM`: Gemini

It is designed to support at least these modalities:

- `Text`
- `Image`
- `Document/PDF`

## Project Structure

```text
multimodal-graph-rag/
├── backend/
├── frontend/
├── docker-compose.yml
├── .env
├── setup.sh
└── README.md
```

## Ubuntu Requirements

Install these first:

- Docker Engine
- Docker Compose plugin
- Python 3

If Docker is not installed:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin python3
```

## Important Docker Note

Use:

```bash
docker compose
```

Do not use:

```bash
docker-compose
```

The old `docker-compose` v1 tool caused `ContainerConfig` errors in this project.

## Environment Setup

Go to the project folder:

```bash
cd ~/multimodal-graph-rag
```

Create or edit `.env`:

```bash
nano .env
```

Use values like this:

```env
GOOGLE_API_KEY=your_gemini_api_key
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
WEAVIATE_URL=http://weaviate:8080
```

## Starting Docker In Ubuntu

If you are running plain Ubuntu without systemd support in the shell session, start Docker manually:

```bash
sudo dockerd
```

Keep that terminal open.

Open a second terminal and go to the project folder:

```bash
cd ~/multimodal-graph-rag
```

If Docker is already running, you can skip `dockerd`.

## Run The Project

Start everything:

```bash
sudo docker compose up -d --build
```

Check status:

```bash
sudo docker compose ps
```

## Main URLs

When the stack is up:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`
- Backend root: `http://localhost:8000/`
- Neo4j Browser: `http://localhost:7474`
- Weaviate ready endpoint: `http://localhost:8081/v1/.well-known/ready`

Neo4j login:

- Username: `neo4j`
- Password: `password`

## Seed Sample Data

To load the sample products:

```bash
python3 backend/ingest_data.py
```

Expected output:

```text
Ingested Sentinel Speed Runners
Ingested Apex Chronograph
Ingested Titanium Book Pro
```

## How To Test The App

### 1. Check Backend

```bash
curl http://localhost:8000/
curl http://localhost:8000/docs
```

### 2. Open Frontend

Open:

```text
http://localhost:3000
```

### 3. Test Text Search

In the search box, try:

- `running shoes`
- `watch`
- `laptop`

### 4. Test Image Search

Upload a product image in the image section and click the search button.

### 5. Test Document/PDF Search

Upload a PDF or supported document and search using a text query.

### 6. Test Chat

Try:

```text
Recommend the best product for daily use and explain why.
```

## Common Commands

### Start only backend

```bash
sudo docker compose up -d --build backend
```

### Start only frontend

```bash
sudo docker compose up -d --build frontend
```

### Stop everything

```bash
sudo docker compose down
```

### Full clean restart

```bash
sudo docker compose down --remove-orphans
sudo docker compose up -d --build
```

### View logs

```bash
sudo docker compose logs --tail 100 backend
sudo docker compose logs --tail 100 frontend
sudo docker compose logs --tail 100 weaviate
sudo docker compose logs --tail 100 neo4j
```

## Troubleshooting

### 1. Frontend does not open on port 3000

Check:

```bash
sudo docker compose ps
sudo docker compose logs --tail 100 frontend
```

### 2. Backend keeps restarting

Check:

```bash
sudo docker compose logs --tail 150 backend
```

### 3. Gemini chat says API key invalid or expired

Update `.env` with a valid key, then recreate backend:

```bash
sudo docker compose stop backend
sudo docker compose rm -f backend
sudo docker compose up -d --build backend
```

### 4. Weaviate fails

Check:

```bash
sudo docker compose logs --tail 150 weaviate
```

Current host port mapping in this project is:

```text
8081 -> 8080
```

That means Weaviate is exposed on host port `8081`.

### 5. Product search shows 0 items

Do these in order:

```bash
python3 backend/ingest_data.py
curl -X POST http://localhost:8000/search -H "Content-Type: application/json" -d '{"query":"running shoes","image_b64":null}'
```

### 6. Old Compose command gives `ContainerConfig` error

Always use:

```bash
sudo docker compose ...
```

Never:

```bash
sudo docker-compose ...
```

## Demo Flow

For a quick demo:

1. Open `http://localhost:3000`
2. Search `running shoes`
3. Upload a product image and search
4. Upload a PDF/document and search
5. Ask in chat:

```text
Recommend the best product for daily use and explain why.
```

## Notes

- Neo4j is used for graph context and product relations.
- Weaviate is used for vector retrieval when available.
- The backend contains a fallback path so the app can still work even if the vector service is unstable.

