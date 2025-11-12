# 🎨 AI Product Mockup Generator for E-commerce

An AI-powered product mockup generator that uses **Stable Diffusion XL** and **ControlNet** to create high-quality, photorealistic product mockups. Perfect for e-commerce businesses, designers, and marketers who need professional product visuals quickly.

## ✨ Features

- 🤖 **AI-Powered Generation**: Uses Stable Diffusion XL (SDXL) for high-quality image generation
- 🎯 **Precise Control**: ControlNet ensures accurate logo placement and composition
- 🖼️ **Natural Blending**: Inpainting technology for realistic texture integration
- 📦 **Multiple Product Types**: T-shirts, mugs, phone cases, and packaging
- 🎨 **Various Styles**: Studio shots, real-life scenes, and flat lay compositions
- 🖥️ **User-Friendly Interface**: Clean Streamlit web application
- 🔌 **API Integration**: FastAPI backend for e-commerce platform integration
- ⚙️ **Customizable**: Adjustable prompt strength, variations, and generation parameters

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (recommended for faster generation)
- At least 16GB RAM
- 10GB+ free disk space

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yadavanujkumar/Product-Mockup-Generator-for-E-commerce.git
cd Product-Mockup-Generator-for-E-commerce
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Streamlit App

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Running the FastAPI Server

```bash
python src/api/server.py
```

Or using uvicorn:
```bash
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
```

API documentation will be available at `http://localhost:8000/docs`

## 📖 Usage

### Web Interface (Streamlit)

1. **Upload Your Design**: Upload a logo or design image (PNG, JPG, JPEG, WEBP)
2. **Select Product Type**: Choose from T-shirt, Mug, Phone Case, or Packaging
3. **Choose Style**: Pick Studio, Real Life, or Flat Lay mockup style
4. **Adjust Settings** (Optional):
   - Number of variations (1-4)
   - Guidance scale (1.0-20.0)
   - Inference steps (10-100)
   - ControlNet strength (0.0-2.0)
   - Random seed for reproducibility
5. **Generate**: Click "Generate Mockups" and wait for AI to create your mockups
6. **Download**: Download your generated mockups in PNG format

### API Usage

#### Generate Mockup

**Endpoint**: `POST /generate`

**Request**:
```bash
curl -X POST "http://localhost:8000/generate" \
  -F "logo=@/path/to/your/logo.png" \
  -F "product_type=tshirt" \
  -F "style=studio" \
  -F "num_variations=2"
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully generated 2 mockup(s)",
  "mockup_urls": [
    "/mockups/mockup_tshirt_studio_20231112_143000_0.png",
    "/mockups/mockup_tshirt_studio_20231112_143000_1.png"
  ],
  "num_generated": 2
}
```

#### Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

## 🏗️ Project Structure

```
Product-Mockup-Generator-for-E-commerce/
├── app.py                          # Streamlit web application
├── config.yaml                     # Configuration file
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── src/
│   ├── mockup_generator/
│   │   ├── __init__.py
│   │   └── generator.py           # Core mockup generation logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── server.py              # FastAPI server
│   │   └── models.py              # Pydantic models
│   └── utils/
│       ├── __init__.py
│       ├── image_utils.py         # Image processing utilities
│       └── config_utils.py        # Configuration utilities
├── generated_mockups/             # Output directory (created automatically)
└── temp_uploads/                  # Temporary upload directory
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

- **Model Settings**: Change AI models or add LoRA fine-tuning
- **Generation Parameters**: Adjust default inference steps, guidance scale
- **Product Types**: Add new product categories
- **Mockup Styles**: Define custom mockup styles
- **Prompts**: Customize generation prompts

Example configuration:
```yaml
MODEL_ID: "stabilityai/stable-diffusion-xl-base-1.0"
CONTROLNET_MODEL: "diffusers/controlnet-canny-sdxl-1.0"
DEFAULT_NUM_INFERENCE_STEPS: 30
DEFAULT_GUIDANCE_SCALE: 7.5
IMAGE_SIZE: 1024
```

## 🎯 Supported Products

| Product Type | Description |
|--------------|-------------|
| **T-Shirt** | Custom apparel mockups with fabric texture |
| **Mug** | Ceramic mug mockups with realistic reflections |
| **Phone Case** | Mobile phone case mockups |
| **Packaging** | Product packaging and box mockups |

## 🎨 Mockup Styles

| Style | Description |
|-------|-------------|
| **Studio** | Professional studio lighting, white background |
| **Real Life** | Lifestyle photography in natural settings |
| **Flat Lay** | Top-down view, organized composition |

## 🔧 Advanced Features

### LoRA Fine-Tuning (Optional)

To add LoRA models for specific product domains:

```python
from diffusers import StableDiffusionXLPipeline

# Load with LoRA
pipeline.load_lora_weights("path/to/lora/weights")
```

### E-commerce Platform Integration

#### Shopify Integration
Use the FastAPI endpoints to integrate with Shopify:

```javascript
// Example Shopify integration
const response = await fetch('http://your-api-url/generate', {
  method: 'POST',
  body: formData
});
```

#### Etsy Integration
Similar approach using the REST API endpoints.

## 🐛 Troubleshooting

### CUDA Out of Memory
- Reduce `IMAGE_SIZE` in config.yaml
- Enable model offloading (already enabled by default)
- Reduce `num_inference_steps`

### Slow Generation
- Ensure you're using a CUDA-capable GPU
- Reduce number of variations
- Use fewer inference steps

### Model Download Issues
- Ensure you have sufficient disk space (10GB+)
- Check your internet connection
- Models are downloaded automatically on first run

## 📝 Requirements

**Core Dependencies:**
- torch >= 2.0.0
- diffusers >= 0.25.0
- transformers >= 4.35.0
- controlnet-aux >= 0.0.7
- streamlit >= 1.28.0
- fastapi >= 0.104.0

See `requirements.txt` for complete list.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

**Note**: This tool requires downloading large AI models (several GB) on first run. Ensure you have sufficient disk space and a stable internet connection.
