# 🚀 Jenkins + Docker Deployment Guide for StudyBot

## 📋 Overview

This guide explains how to deploy StudyBot using:
- **Docker**: Containerization
- **Jenkins**: CI/CD automation
- **Cloud Platform**: AWS/GCP/Azure/DigitalOcean (NOT Netlify)

---

## ⚠️ Why NOT Netlify?

**Netlify is for static sites only** (HTML/CSS/JS). Your app needs:
- ❌ Python backend server
- ❌ Database (SQLite)
- ❌ File uploads
- ❌ Real-time WebSocket connections
- ❌ Persistent storage

**✅ Use Instead:** AWS, Google Cloud, DigitalOcean, Railway, Render, or Streamlit Cloud

---

## 🎯 Deployment Architecture

```
GitHub Repository
      ↓
Jenkins (Webhook trigger)
      ↓
Build Docker Image
      ↓
Run Tests
      ↓
Push to Docker Hub
      ↓
Deploy to Cloud Server
      ↓
Application Running on http://your-server:8501
```

---

## 📦 Prerequisites

### **1. Install Docker**

**Windows:**
- Download Docker Desktop: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Verify:**
```bash
docker --version
docker-compose --version
```

### **2. Install Jenkins**

**Option A: Docker (Easiest)**
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

**Option B: Windows**
- Download: https://www.jenkins.io/download/
- Install as Windows service

**Access Jenkins:**
- Open: http://localhost:8080
- Get initial password:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### **3. Docker Hub Account**
- Sign up: https://hub.docker.com
- Create repository: `your-username/studybot`

---

## 🔧 Step 1: Test Docker Locally

### **Build Docker Image**

```bash
cd d:\pranav__all_projects\rag_chatbot

# Build image
docker build -t studybot:latest .

# Check image
docker images
```

### **Run Container Locally**

```bash
# Run with environment variables
docker run -d \
  --name studybot \
  -p 8501:8501 \
  -e GROQ_API_KEY="your_groq_api_key_here" \
  -e ADMIN_PASSWORD="admin123" \
  -v ${PWD}/data:/app/data \
  studybot:latest

# Check logs
docker logs studybot

# Check running containers
docker ps
```

### **Access Application**
Open: http://localhost:8501

### **Stop Container**
```bash
docker stop studybot
docker rm studybot
```

### **Using Docker Compose (Alternative)**

```bash
# Create .env file first
echo "GROQ_API_KEY=your_key_here" > .env
echo "ADMIN_PASSWORD=admin123" >> .env

# Start with compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🤖 Step 2: Configure Jenkins

### **1. Install Jenkins Plugins**

Go to: **Manage Jenkins → Manage Plugins → Available**

Install:
- Docker Pipeline
- GitHub Integration
- Docker Commons
- Git Plugin
- Pipeline

### **2. Add Credentials**

Go to: **Manage Jenkins → Manage Credentials → Global → Add Credentials**

**A. Docker Hub Credentials**
- Kind: Username with password
- ID: `docker-hub-credentials`
- Username: Your Docker Hub username
- Password: Your Docker Hub password

**B. Groq API Key**
- Kind: Secret text
- ID: `groq-api-key`
- Secret: Your Groq API key

**C. Admin Password**
- Kind: Secret text
- ID: `admin-password`
- Secret: `admin123`

### **3. Create Jenkins Pipeline**

**A. New Item**
- Click "New Item"
- Name: `StudyBot-Pipeline`
- Type: Pipeline
- Click OK

**B. Configure Pipeline**

**General:**
- ✅ GitHub project
- Project URL: `https://github.com/Pranavkapratwar10/studybot`

**Build Triggers:**
- ✅ GitHub hook trigger for GITScm polling

**Pipeline:**
- Definition: Pipeline script from SCM
- SCM: Git
- Repository URL: `https://github.com/Pranavkapratwar10/studybot.git`
- Branch: `*/main`
- Script Path: `Jenkinsfile`

**Save**

### **4. Configure GitHub Webhook**

**A. Go to GitHub Repository**
- Settings → Webhooks → Add webhook

**B. Configure:**
- Payload URL: `http://your-jenkins-server:8080/github-webhook/`
- Content type: `application/json`
- Events: Just the push event
- Active: ✅

---

## 🚀 Step 3: Deploy to Cloud

### **Option A: AWS EC2**

**1. Launch EC2 Instance**
- AMI: Ubuntu 22.04
- Instance Type: t2.medium (recommended)
- Security Group:
  * Port 22 (SSH)
  * Port 8501 (Streamlit)
  * Port 8080 (Jenkins - optional)

**2. Connect to Instance**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

**3. Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

**4. Run Container**
```bash
docker run -d \
  --name studybot \
  -p 8501:8501 \
  -e GROQ_API_KEY="your_key" \
  -e ADMIN_PASSWORD="admin123" \
  -v /home/ubuntu/studybot-data:/app/data \
  --restart unless-stopped \
  pranavkapratwar10/studybot:latest
```

**5. Access**
- http://your-ec2-ip:8501

### **Option B: Google Cloud Run**

**1. Build and Push**
```bash
# Tag for GCR
docker tag studybot:latest gcr.io/your-project/studybot:latest

# Push to GCR
docker push gcr.io/your-project/studybot:latest
```

**2. Deploy**
```bash
gcloud run deploy studybot \
  --image gcr.io/your-project/studybot:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=your_key
```

### **Option C: DigitalOcean**

**1. Create Droplet**
- Image: Docker on Ubuntu
- Plan: Basic ($12/month)
- Region: Nearest to you

**2. Access Droplet**
```bash
ssh root@your-droplet-ip
```

**3. Deploy**
```bash
docker run -d \
  --name studybot \
  -p 8501:8501 \
  -e GROQ_API_KEY="your_key" \
  -v /root/studybot-data:/app/data \
  --restart unless-stopped \
  pranavkapratwar10/studybot:latest
```

**4. Setup Domain (Optional)**
- Point domain to droplet IP
- Use Nginx as reverse proxy

### **Option D: Railway (Easiest)**

**1. Go to Railway.app**
- Sign in with GitHub

**2. New Project**
- Deploy from GitHub repo
- Select: `Pranavkapratwar10/studybot`

**3. Add Environment Variables**
```
GROQ_API_KEY=your_key_here
ADMIN_PASSWORD=admin123
```

**4. Deploy**
- Railway auto-detects Dockerfile
- Builds and deploys automatically
- Provides public URL

---

## 🔄 Step 4: Complete CI/CD Flow

### **Workflow:**

1. **Developer pushes code to GitHub**
```bash
git add .
git commit -m "Update feature"
git push origin main
```

2. **GitHub webhook triggers Jenkins**
- Jenkins receives push notification

3. **Jenkins Pipeline runs:**
- ✅ Checkout code
- ✅ Build Docker image
- ✅ Run tests
- ✅ Push to Docker Hub
- ✅ Deploy to server
- ✅ Health check

4. **Application auto-updates**
- New version running
- Zero downtime (with proper setup)

### **Manual Trigger:**
- Go to Jenkins
- Click "Build Now"

---

## 📊 Monitoring & Management

### **Check Container Status**
```bash
# Running containers
docker ps

# Container logs
docker logs studybot -f

# Container resource usage
docker stats studybot

# Access container shell
docker exec -it studybot /bin/bash
```

### **Update Application**
```bash
# Pull latest image
docker pull pranavkapratwar10/studybot:latest

# Restart container
docker-compose down
docker-compose up -d
```

### **Backup Data**
```bash
# Backup database and uploads
tar -czf studybot-backup-$(date +%Y%m%d).tar.gz data/
```

---

## 🐛 Troubleshooting

### **Container Won't Start**
```bash
# Check logs
docker logs studybot

# Common issues:
# - Missing environment variables
# - Port already in use
# - Insufficient memory
```

### **Build Fails**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t studybot:latest .
```

### **App Not Accessible**
```bash
# Check if container is running
docker ps

# Check port mapping
docker port studybot

# Check firewall
sudo ufw status
sudo ufw allow 8501
```

### **Jenkins Can't Connect to Docker**
```bash
# Add Jenkins user to docker group
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

---

## 💰 Cost Comparison

| Platform | Monthly Cost | Free Tier |
|----------|-------------|-----------|
| **Streamlit Cloud** | Free / $20 | 1 private app free |
| **Railway** | ~$5-10 | $5 credit/month |
| **DigitalOcean** | $12 | $200 credit (60 days) |
| **AWS EC2 t2.micro** | Free-$10 | 750 hrs/month (1 year) |
| **Google Cloud Run** | Pay-per-use | $0-5 typically |
| **Render** | Free-$7 | Free tier available |

---

## ✅ Recommended Deployment Path

**For Beginners:**
1. **Streamlit Cloud** (Easiest, no Docker/Jenkins needed)
2. **Railway** (Simple, good for learning)

**For Learning DevOps:**
1. **Docker + Railway** (Docker practice, easy deploy)
2. **Jenkins + DigitalOcean** (Full CI/CD experience)

**For Production:**
1. **Jenkins + AWS/GCP** (Scalable, professional)
2. **Docker + Kubernetes** (Advanced, enterprise-grade)

---

## 📚 Next Steps

**After Deployment:**

1. **Set up monitoring**
   - Application logs
   - Error tracking (Sentry)
   - Uptime monitoring (UptimeRobot)

2. **Configure domain**
   - Buy domain (Namecheap, GoDaddy)
   - Point to server IP
   - Setup HTTPS (Let's Encrypt)

3. **Implement backups**
   - Database backups
   - Automated backup scripts
   - Cloud storage (S3, GCS)

4. **Security hardening**
   - Environment variables
   - Rate limiting
   - Regular updates

---

## 🎓 Interview Points

When discussing this deployment:

**"I implemented a complete CI/CD pipeline using Jenkins and Docker. The workflow includes:**

1. **Containerization**: Dockerized the Streamlit app for consistency
2. **Automation**: Jenkins pipeline triggered by GitHub webhooks
3. **Testing**: Automated health checks before deployment
4. **Registry**: Published images to Docker Hub
5. **Deployment**: Automated deployment to cloud servers
6. **Monitoring**: Implemented logging and health checks"

**Key concepts you learned:**
- Docker containerization
- Jenkins pipeline configuration
- CI/CD best practices
- Cloud deployment
- Infrastructure as Code

---

## 📞 Support

- Docker Docs: https://docs.docker.com
- Jenkins Docs: https://www.jenkins.io/doc/
- Streamlit Cloud: https://streamlit.io/cloud

---

**Good luck with your deployment! 🚀**
