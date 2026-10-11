#!/bin/bash
# AWS EC2 Setup Script for StudyBot
# Run this on your EC2 instance after SSH

echo "=========================================="
echo "  StudyBot AWS EC2 Setup Script"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and dependencies
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3-pip python3.11-venv git build-essential

# Clone repository
echo "📥 Cloning StudyBot repository..."
cd ~
git clone https://github.com/Pranavkapratwar10/studybot.git
cd studybot

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install requirements
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating data directories..."
mkdir -p data/uploads data/chroma_db .streamlit

# Create secrets file
echo "🔐 Setting up secrets..."
echo "Enter your Groq API Key:"
read -r GROQ_KEY

cat > .streamlit/secrets.toml << EOF
GROQ_API_KEY = "$GROQ_KEY"
ADMIN_PASSWORD = "admin123"
EOF

echo "✅ Secrets configured!"

# Create systemd service
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/studybot.service > /dev/null << EOF
[Unit]
Description=StudyBot Streamlit Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/studybot
Environment="PATH=$HOME/studybot/venv/bin"
ExecStart=$HOME/studybot/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Starting StudyBot service..."
sudo systemctl daemon-reload
sudo systemctl enable studybot
sudo systemctl start studybot

# Check status
sleep 3
sudo systemctl status studybot --no-pager

echo ""
echo "=========================================="
echo "  ✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Your StudyBot is now running!"
echo ""
echo "📍 Access your app at:"
echo "   http://$(curl -s ifconfig.me):8501"
echo ""
echo "📊 Check status:"
echo "   sudo systemctl status studybot"
echo ""
echo "📜 View logs:"
echo "   sudo journalctl -u studybot -f"
echo ""
echo "🔄 Restart service:"
echo "   sudo systemctl restart studybot"
echo ""
echo "🛑 Stop service:"
echo "   sudo systemctl stop studybot"
echo ""
echo "=========================================="
