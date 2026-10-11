# 🐳 Docker Commands Quick Reference for StudyBot

## 📦 Build & Run

### **Build Docker Image**
```bash
# Navigate to project directory
cd d:\pranav__all_projects\rag_chatbot

# Build image
docker build -t studybot:latest .

# Build with custom tag
docker build -t studybot:v1.0 .
```

### **Run Container**
```bash
# Basic run
docker run -d --name studybot -p 8501:8501 studybot:latest

# With environment variables
docker run -d \
  --name studybot \
  -p 8501:8501 \
  -e GROQ_API_KEY="gsk_your_key_here" \
  -e ADMIN_PASSWORD="admin123" \
  studybot:latest

# With volume mount (persist data)
docker run -d \
  --name studybot \
  -p 8501:8501 \
  -e GROQ_API_KEY="gsk_your_key_here" \
  -v ${PWD}/data:/app/data \
  studybot:latest
```

### **Using Docker Compose**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build
```

---

## 🔍 Inspect & Debug

### **Check Running Containers**
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Show container details
docker inspect studybot
```

### **View Logs**
```bash
# View logs
docker logs studybot

# Follow logs (real-time)
docker logs -f studybot

# Last 100 lines
docker logs --tail 100 studybot
```

### **Access Container Shell**
```bash
# Access bash shell
docker exec -it studybot /bin/bash

# Run single command
docker exec studybot ls -la /app

# Check Python version
docker exec studybot python --version
```

### **Resource Usage**
```bash
# View CPU/Memory usage
docker stats studybot

# All containers
docker stats
```

---

## 🛑 Stop & Remove

### **Stop Container**
```bash
# Stop gracefully
docker stop studybot

# Force stop
docker stop -t 0 studybot

# Stop all running containers
docker stop $(docker ps -q)
```

### **Remove Container**
```bash
# Remove stopped container
docker rm studybot

# Force remove (even if running)
docker rm -f studybot

# Remove all stopped containers
docker container prune
```

### **Remove Images**
```bash
# Remove specific image
docker rmi studybot:latest

# Remove all unused images
docker image prune -a

# Remove everything
docker system prune -a
```

---

## 🔄 Update & Restart

### **Update to New Version**
```bash
# Stop old container
docker stop studybot
docker rm studybot

# Pull new image (if from registry)
docker pull pranavkapratwar10/studybot:latest

# Run new container
docker run -d \
  --name studybot \
  -p 8501:8501 \
  -e GROQ_API_KEY="your_key" \
  -v ${PWD}/data:/app/data \
  pranavkapratwar10/studybot:latest
```

### **Restart Container**
```bash
# Restart
docker restart studybot

# Restart with different restart policy
docker update --restart unless-stopped studybot
```

---

## 📤 Push to Docker Hub

### **Login to Docker Hub**
```bash
docker login
# Enter username and password
```

### **Tag Image**
```bash
# Tag with your Docker Hub username
docker tag studybot:latest pranavkapratwar10/studybot:latest
docker tag studybot:latest pranavkapratwar10/studybot:v1.0
```

### **Push Image**
```bash
# Push to Docker Hub
docker push pranavkapratwar10/studybot:latest
docker push pranavkapratwar10/studybot:v1.0
```

### **Pull Image**
```bash
# Pull from Docker Hub
docker pull pranavkapratwar10/studybot:latest
```

---

## 💾 Data Management

### **Backup Data**
```bash
# Backup volume data
docker cp studybot:/app/data ./backup/

# Create tar archive
tar -czf studybot-backup-$(date +%Y%m%d).tar.gz data/
```

### **Restore Data**
```bash
# Restore from backup
docker cp ./backup/data studybot:/app/

# Restart container
docker restart studybot
```

### **Volume Management**
```bash
# List volumes
docker volume ls

# Create volume
docker volume create studybot-data

# Inspect volume
docker volume inspect studybot-data

# Remove unused volumes
docker volume prune
```

---

## 🌐 Networking

### **Check Port Mapping**
```bash
# Show port mappings
docker port studybot

# Check if port is in use
netstat -ano | findstr :8501
```

### **Network Commands**
```bash
# List networks
docker network ls

# Create network
docker network create studybot-network

# Connect container to network
docker network connect studybot-network studybot

# Inspect network
docker network inspect studybot-network
```

---

## 🧪 Testing

### **Test Build**
```bash
# Build and test
docker build -t studybot:test .

# Run tests in container
docker run --rm studybot:test python -m pytest

# Health check
curl http://localhost:8501/_stcore/health
```

### **Interactive Testing**
```bash
# Run with shell access
docker run -it --rm studybot:latest /bin/bash

# Test Python imports
docker run --rm studybot:latest python -c "import streamlit; print(streamlit.__version__)"
```

---

## 🔧 Troubleshooting

### **Container Won't Start**
```bash
# Check logs for errors
docker logs studybot

# Check if port is already in use
docker ps | grep 8501

# Run in foreground to see errors
docker run --rm -p 8501:8501 studybot:latest
```

### **Build Fails**
```bash
# Clear build cache
docker builder prune

# Build without cache
docker build --no-cache -t studybot:latest .

# Build with verbose output
docker build --progress=plain -t studybot:latest .
```

### **Container is Slow**
```bash
# Check resource usage
docker stats studybot

# Limit resources
docker run -d \
  --name studybot \
  --memory="2g" \
  --cpus="1.5" \
  -p 8501:8501 \
  studybot:latest
```

### **Can't Access Application**
```bash
# Check if container is running
docker ps

# Check container IP
docker inspect studybot | grep IPAddress

# Test from inside container
docker exec studybot curl http://localhost:8501
```

---

## 🚀 Production Best Practices

### **Run with Restart Policy**
```bash
docker run -d \
  --name studybot \
  --restart unless-stopped \
  -p 8501:8501 \
  studybot:latest
```

### **Run with Resource Limits**
```bash
docker run -d \
  --name studybot \
  --memory="2g" \
  --cpus="2" \
  --restart unless-stopped \
  -p 8501:8501 \
  studybot:latest
```

### **Run with Health Check**
```bash
docker run -d \
  --name studybot \
  --health-cmd="curl -f http://localhost:8501/_stcore/health || exit 1" \
  --health-interval=30s \
  --health-retries=3 \
  -p 8501:8501 \
  studybot:latest
```

---

## 📋 Complete Workflow Example

```bash
# 1. Build image
docker build -t studybot:latest .

# 2. Test locally
docker run -d --name studybot-test -p 8501:8501 studybot:latest

# 3. Access and test
# Open http://localhost:8501

# 4. Stop test container
docker stop studybot-test
docker rm studybot-test

# 5. Tag for Docker Hub
docker tag studybot:latest pranavkapratwar10/studybot:latest

# 6. Push to Docker Hub
docker push pranavkapratwar10/studybot:latest

# 7. Deploy to production server (SSH to server first)
docker pull pranavkapratwar10/studybot:latest
docker run -d \
  --name studybot \
  --restart unless-stopped \
  -p 8501:8501 \
  -e GROQ_API_KEY="your_key" \
  -v /var/studybot/data:/app/data \
  pranavkapratwar10/studybot:latest

# 8. Check health
curl http://localhost:8501/_stcore/health
docker logs -f studybot
```

---

## 🎯 Quick Commands Cheat Sheet

| Task | Command |
|------|---------|
| Build | `docker build -t studybot .` |
| Run | `docker run -d -p 8501:8501 studybot` |
| Stop | `docker stop studybot` |
| Start | `docker start studybot` |
| Restart | `docker restart studybot` |
| Logs | `docker logs -f studybot` |
| Shell | `docker exec -it studybot /bin/bash` |
| Remove | `docker rm -f studybot` |
| Stats | `docker stats studybot` |
| Compose Up | `docker-compose up -d` |
| Compose Down | `docker-compose down` |

---

## 💡 Tips

1. **Always use specific tags** (not just `latest`)
2. **Mount volumes** to persist data
3. **Set restart policies** for production
4. **Monitor resource usage** regularly
5. **Keep images small** (use `.dockerignore`)
6. **Use environment variables** for secrets
7. **Implement health checks**
8. **Regular backups** of volumes

---

**Need help? Check the main deployment guide: `JENKINS_DOCKER_DEPLOYMENT.md`**
