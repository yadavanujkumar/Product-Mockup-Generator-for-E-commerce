#!/bin/bash

# Setup script for AI Product Mockup Generator

echo "🎨 Setting up AI Product Mockup Generator..."
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if Python 3.8+
if ! python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "❌ Error: Python 3.8 or higher is required"
    exit 1
fi
echo "✅ Python version OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install requirements
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "Creating required directories..."
mkdir -p generated_mockups
mkdir -p temp_uploads
echo "✅ Directories created"
echo ""

# Check for CUDA
echo "Checking for CUDA..."
if python -c "import torch; print(torch.cuda.is_available())" | grep -q "True"; then
    echo "✅ CUDA available - GPU acceleration enabled"
else
    echo "⚠️ CUDA not available - will use CPU (slower)"
fi
echo ""

echo "================================================"
echo "✅ Setup complete!"
echo "================================================"
echo ""
echo "To start using the application:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the Streamlit app:"
echo "   streamlit run app.py"
echo ""
echo "3. Or run the API server:"
echo "   python src/api/server.py"
echo ""
echo "Note: Models will be downloaded automatically on first run (several GB)"
echo "================================================"
