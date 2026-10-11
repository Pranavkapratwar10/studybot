#!/bin/bash
# Setup script for AI Study Assistant

echo "🚀 Setting up AI Study Assistant..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/uploads data/chroma_db

echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment:"
echo "   - Windows: venv\\Scripts\\activate"
echo "   - Linux/Mac: source venv/bin/activate"
echo "2. Run: streamlit run app.py"
