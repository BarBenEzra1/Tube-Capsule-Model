# 🐳 Docker Setup for Tube Capsule Model API

This guide will help you run the Tube Capsule Model API using Docker and Docker Compose, without needing to install Python or PostgreSQL locally.

## 📋 Prerequisites

You only need to have Docker and Docker Compose installed on your system:

- **Docker Desktop** (includes Docker Compose): [Download here](https://www.docker.com/products/docker-desktop/)
- Or install **Docker** and **Docker Compose** separately on Linux

## 🚀 Quick Start

1. **Clone or download this project** to your local machine

2. **Navigate to the project directory:**
   ```bash
   cd tube-capsule-model
   ```

3. **Start the application:**
   ```bash
   docker-compose up --build
   ```

4. **Wait for the services to start** (first time may take a few minutes to download images and build)

5. **Access the Swagger UI** in your browser:
   ```
   http://localhost:8000/docs
   ```

That's it! 🎉

## 🌐 Available Endpoints

Once running, you can access:

- **Swagger UI (Interactive API docs)**: http://localhost:8000/docs
- **ReDoc (Alternative docs)**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

## 🛠️ Docker Commands

### Start the application (detached mode):
```bash
docker-compose up -d
```

### Stop the application:
```bash
docker-compose down
```

### View logs:
```bash
# All services
docker-compose logs

# Just the API
docker-compose logs app

# Just PostgreSQL
docker-compose logs postgres
```

### Restart the application:
```bash
docker-compose restart
```

### Rebuild and start (after code changes):
```bash
docker-compose up --build
```

### Stop and remove everything (including database data):
```bash
docker-compose down -v
```

## 🗄️ Database Access

The PostgreSQL database runs in a Docker container and is accessible at:
- **Host**: localhost
- **Port**: 5432
- **Database**: tube_capsule_db
- **Username**: postgres
- **Password**: password

You can connect using any PostgreSQL client (pgAdmin, DBeaver, etc.) or command line:
```bash
docker exec -it tube-capsule-postgres psql -U postgres -d tube_capsule_db
```