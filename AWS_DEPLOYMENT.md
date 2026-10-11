# ☁️ AWS Deployment Guide for StudyBot

## 🎯 AWS Deployment Options

You can deploy StudyBot to AWS in several ways:

1. **AWS EC2** - Virtual machine (Most control)
2. **AWS Elastic Beanstalk** - Platform as a Service (Easiest)
3. **AWS ECS/Fargate** - Container service (Docker)
4. **AWS App Runner** - Fully managed containers (New & Simple)
5. **AWS Lightsail** - Simplified EC2 (Budget-friendly)

---

## 🚀 Option 1: AWS Elastic Beanstalk (RECOMMENDED - Easiest)

**Perfect for:** Quick deployment, no Docker knowledge needed

### **Prerequisites**
- AWS Account with admin access
- EB CLI installed

### **Step 1: Install EB CLI**

**Windows:**
```bash
pip install awsebcli
```

**Verify:**
```bash
eb --version
```

### **Step 2: Configure AWS Credentials**

```bash
# Configure AWS CLI
aws configure

# Enter when prompted:
# AWS Access Key ID: [Your key]
# AWS Secret Access Key: [Your secret]
# Default region: us-east-1
# Default output format: json
```

### **Step 3: Create Required Files**

**Create `.ebextensions/python.config`:**
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    STREAMLIT_SERVER_PORT: 8501
    STREAMLIT_SERVER_ADDRESS: 0.0.0.0
```

**Create `Procfile`:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### **Step 4: Initialize Elastic Beanstalk**

```bash
# Navigate to project
cd d:\pranav__all_projects\rag_chatbot

# Initialize EB
eb init

# Answer prompts:
# Select region: [Your preferred region]
# Application name: studybot
# Platform: Python
# Python version: 3.11
# Setup SSH: yes (optional)
```

### **Step 5: Create Environment Variables File**

Create `.env.yaml`:
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    GROQ_API_KEY: "your_groq_api_key_here"
    ADMIN_PASSWORD: "admin123"
```

### **Step 6: Create Environment and Deploy**

```bash
# Create environment
eb create studybot-env --instance-type t2.medium --envvars GROQ_API_KEY=your_key,ADMIN_PASSWORD=admin123

# This will:
# - Create environment
# - Upload your code
# - Install dependencies
# - Start application

# Check status
eb status

# Open in browser
eb open
```

### **Step 7: Update Application**

```bash
# After making changes
eb deploy

# View logs
eb logs

# SSH into instance (if needed)
eb ssh
```

### **Costs:**
- t2.micro (free tier): Free for 1 year
- t2.medium: ~$35/month (recommended for your app)

---

## 🖥️ Option 2: AWS EC2 (Full Control)

**Perfect for:** Learning AWS, full customization

### **Step 1: Launch EC2 Instance**

**A. Go to AWS Console → EC2 → Launch Instance**

**B. Configure:**
- Name: `studybot-server`
- AMI: **Ubuntu Server 22.04 LTS**
- Instance type: **t2.medium** (or t2.micro for testing)
- Key pair: Create new or use existing
- Network settings:
  - Create security group
  - Allow SSH (22) from your IP
  - Allow Custom TCP (8501) from anywhere (0.0.0.0/0)

**C. Storage:** 20 GB (default is fine)

**D. Click "Launch Instance"**

### **Step 2: Connect to EC2 Instance**

**Get instance IP from AWS Console**

**Connect via SSH:**
```bash
# Windows (PowerShell with OpenSSH)
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip

# Example:
ssh -i "studybot-key.pem" ubuntu@3.85.123.45
```

**If permission error on Windows:**
```powershell
# Fix key permissions
icacls "studybot-key.pem" /inheritance:r
icacls "studybot-key.pem" /grant:r "$($env:USERNAME):(R)"
```

### **Step 3: Install Dependencies on EC2**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3-pip python3.11-venv git

# Install additional packages
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# Verify
python3.11 --version
```

### **Step 4: Clone Your Repository**

```bash
# Clone from GitHub
git clone https://github.com/Pranavkapratwar10/studybot.git

# Navigate to project
cd studybot
```

### **Step 5: Set Up Python Virtual Environment**

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### **Step 6: Configure Secrets**

```bash
# Create secrets directory
mkdir -p .streamlit

# Create secrets file
nano .streamlit/secrets.toml

# Add content:
GROQ_API_KEY = "your_groq_api_key_here"
ADMIN_PASSWORD = "admin123"

# Save: Ctrl+O, Enter, Ctrl+X
```

### **Step 7: Run Application**

**Test run:**
```bash
streamlit run app.py
```

**For production, use tmux/screen:**
```bash
# Install tmux
sudo apt install -y tmux

# Start tmux session
tmux new -s studybot

# Run app
streamlit run app.py --server.port=8501 --server.address=0.0.0.0

# Detach: Ctrl+B then D
# Reattach: tmux attach -t studybot
```

**Better: Use systemd service (recommended):**

```bash
# Create service file
sudo nano /etc/systemd/system/studybot.service
```

**Add content:**
```ini
[Unit]
Description=StudyBot Streamlit Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/studybot
Environment="PATH=/home/ubuntu/studybot/venv/bin"
ExecStart=/home/ubuntu/studybot/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable studybot

# Start service
sudo systemctl start studybot

# Check status
sudo systemctl status studybot

# View logs
sudo journalctl -u studybot -f
```

### **Step 8: Access Your Application**

Open browser: `http://your-ec2-public-ip:8501`

### **Step 9: Set Up Domain (Optional)**

**A. Get domain from Route 53 or external provider**

**B. Create A record pointing to EC2 IP**

**C. Install Nginx as reverse proxy:**

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/studybot
```

**Add content:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

**Enable site:**
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/studybot /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

**D. Install SSL with Let's Encrypt:**

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

**Now access:** `https://your-domain.com`

### **Costs:**
- t2.micro: Free tier (750 hours/month for 1 year)
- t2.medium: ~$35/month
- Data transfer: First 100GB free/month

---

## 🐳 Option 3: AWS ECS with Fargate (Docker)

**Perfect for:** Docker experience, scalability

### **Step 1: Push Docker Image to ECR**

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name studybot --region us-east-1

# Build image
docker build -t studybot .

# Tag for ECR
docker tag studybot:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/studybot:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/studybot:latest
```

### **Step 2: Create ECS Cluster**

**Via AWS Console:**
1. Go to ECS → Clusters → Create Cluster
2. Name: `studybot-cluster`
3. Infrastructure: AWS Fargate
4. Create

### **Step 3: Create Task Definition**

**Create `task-definition.json`:**
```json
{
  "family": "studybot-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "studybot",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/studybot:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GROQ_API_KEY",
          "value": "your_key_here"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/studybot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Register task:**
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### **Step 4: Create Service**

1. Go to Cluster → Create Service
2. Task Definition: studybot-task
3. Service name: studybot-service
4. Desired tasks: 1
5. Networking: Default VPC, public subnets
6. Security group: Allow port 8501
7. Create

### **Step 5: Access Application**

Get public IP from ECS task and access: `http://task-ip:8501`

### **Costs:**
- Fargate: ~$15-30/month (0.5 vCPU, 1GB RAM)

---

## 💡 Option 4: AWS App Runner (Simplest Docker)

**Perfect for:** Easiest Docker deployment

### **Step 1: Create apprunner.yaml**

```yaml
version: 1.0
runtime: python3.11
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: streamlit run app.py --server.port=8501 --server.address=0.0.0.0
  network:
    port: 8501
```

### **Step 2: Deploy via Console**

1. Go to App Runner → Create Service
2. Source: GitHub repository
3. Connect to GitHub
4. Select repository: studybot
5. Branch: main
6. Build settings: Automatic
7. Instance: 1 vCPU, 2GB RAM
8. Environment variables:
   - GROQ_API_KEY
   - ADMIN_PASSWORD
9. Create & Deploy

**App Runner automatically:**
- Builds your app
- Deploys to managed infrastructure
- Provides HTTPS URL
- Auto-scales

### **Costs:**
- ~$25/month (1 vCPU, 2GB RAM)

---

## 🏝️ Option 5: AWS Lightsail (Budget-Friendly)

**Perfect for:** Learning, small budget

### **Step 1: Create Lightsail Instance**

1. Go to Lightsail → Create Instance
2. Location: Choose nearest
3. Platform: Linux/Unix
4. Blueprint: OS Only → Ubuntu 22.04
5. Plan: $5/month (1GB RAM) or $10/month (2GB RAM)
6. Name: studybot
7. Create

### **Step 2: Configure and Deploy**

**Same as EC2 steps 2-8** (SSH, install, run)

**Advantage:** Fixed pricing, includes data transfer

### **Costs:**
- $5/month: 1GB RAM, 1 vCPU, 40GB SSD, 2TB transfer
- $10/month: 2GB RAM, 1 vCPU, 60GB SSD, 3TB transfer

---

## 📊 AWS Options Comparison

| Option | Difficulty | Setup Time | Monthly Cost | Best For |
|--------|-----------|------------|--------------|----------|
| **Elastic Beanstalk** | ⭐⭐ | 30 min | $35 | Quick deploy |
| **EC2** | ⭐⭐⭐⭐ | 1-2 hrs | Free-$35 | Full control |
| **ECS Fargate** | ⭐⭐⭐⭐ | 2 hrs | $15-30 | Docker + scale |
| **App Runner** | ⭐⭐ | 20 min | $25 | Easiest Docker |
| **Lightsail** | ⭐⭐⭐ | 1 hr | $5-10 | Budget |

---

## 🎯 My Recommendation for AWS

### **For Quick Start:**
1. **AWS Elastic Beanstalk** - Deploy in 30 minutes
2. **AWS Lightsail** - $5/month budget option

### **For Learning:**
1. **AWS EC2** - Learn Linux, Nginx, systemd
2. Full DevOps experience

### **For Production:**
1. **AWS ECS Fargate** - Scalable, managed
2. Professional setup

---

## 🚀 Quick Start Commands (EC2)

```bash
# 1. Launch EC2 instance from AWS Console
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. One-command setup script
curl -o- https://raw.githubusercontent.com/Pranavkapratwar10/studybot/main/setup.sh | bash

# Or manual:
sudo apt update && sudo apt install -y python3-pip git
git clone https://github.com/Pranavkapratwar10/studybot.git
cd studybot
pip3 install -r requirements.txt
mkdir -p .streamlit
echo 'GROQ_API_KEY = "your_key"' > .streamlit/secrets.toml
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

---

## 🔒 Security Best Practices

### **1. Use IAM Roles (not hardcoded keys)**
### **2. Store secrets in AWS Secrets Manager**
### **3. Enable CloudWatch logging**
### **4. Use Security Groups properly**
### **5. Enable AWS WAF for production**
### **6. Regular backups with AWS Backup**

---

## 📈 Monitoring

### **CloudWatch Metrics:**
```bash
# Install CloudWatch agent
sudo apt install -y amazon-cloudwatch-agent

# Monitor CPU, Memory, Disk
```

### **Application Logs:**
```bash
# View systemd logs
sudo journalctl -u studybot -f

# Or check Streamlit logs
tail -f ~/.streamlit/logs/streamlit.log
```

---

## 🆘 Troubleshooting

### **Can't connect to EC2:**
- Check Security Group allows port 8501
- Verify instance is running
- Check public IP address

### **Application won't start:**
```bash
# Check logs
sudo systemctl status studybot
sudo journalctl -u studybot -n 100

# Test manually
source venv/bin/activate
streamlit run app.py
```

### **Out of memory:**
- Upgrade to larger instance
- Add swap space:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 💰 Cost Optimization

1. **Use Reserved Instances** (save 40-60%)
2. **Stop instances when not in use**
3. **Use Spot Instances** for testing
4. **Monitor with Cost Explorer**
5. **Set billing alerts**

---

## 📚 Next Steps

1. **Choose deployment method**
2. **Follow the specific guide above**
3. **Test thoroughly**
4. **Set up monitoring**
5. **Configure backups**
6. **Add custom domain**
7. **Enable HTTPS**

---

## 🎓 Interview Points

*"I deployed my application to AWS using [EC2/ECS/Beanstalk]. I configured security groups, set up systemd services, implemented logging with CloudWatch, and used Nginx as a reverse proxy with SSL. The application is scalable and production-ready."*

---

**Ready to deploy? Pick your AWS option and start! 🚀**
