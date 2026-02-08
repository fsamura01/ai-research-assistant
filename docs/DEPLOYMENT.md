# 🚀 Deployment Guide: AI Research Assistant

This guide explains how to deploy the AI Research Assistant using Docker and Docker Compose. This is the recommended method for production-like environments as it ensures a consistent setup and includes a dedicated Qdrant vector database.

## 📋 Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.
- A `.env` file with your API keys (see `.env.example`).

## 🛠️ Deployment Steps

### 1. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```
Ensure at least `GROQ_API_KEY` and `TAVILY_API_KEY` are set.

### 2. Build and Start the Containers
Run the following command from the project root:
```bash
docker-compose up -d --build
```

This will:
- Build the research assistant application.
- Pull the latest Qdrant image.
- Start both services and network them together.

### 3. Access the Application
Once the containers are running, open your browser and navigate to:
**[http://localhost:8501](http://localhost:8501)**

## 📂 Data & Persistence

The `docker-compose.yml` is configured to persist data outside the containers:
- `./qdrant_data`: Stores the vector database collections.
- `./research_notes`: All markdown notes saved by the agent will appear here.
- `./logs`: SQLite interaction logs and performance metrics.
- `./data`: Place any initial PDFs here to be picked up by the app (optional).

## 🛑 Stopping the Services

To stop the assistant and Qdrant:
```bash
docker-compose down
```

## 🔍 Troubleshooting

- **Check Logs:** `docker-compose logs -f app`
- **Database Status:** Qdrant dashboard is available at `http://localhost:6333/dashboard`
- **Port Conflicts:** If port 8501 is already in use, modify the `ports` mapping in `docker-compose.yml`.
