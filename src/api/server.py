"""
FastAPI server for Product Mockup Generator.
Provides REST API endpoints for e-commerce integration.
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import io
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mockup_generator import MockupGenerator
from utils.config_utils import load_config, ensure_directories
from api.models import (
    MockupRequest,
    MockupResponse,
    HealthResponse,
    ProductType,
    MockupStyle
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Product Mockup Generator API",
    description="REST API for generating product mockups using Stable Diffusion and ControlNet",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global generator instance
generator = None
config = None


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global generator, config
    
    logger.info("Starting up API server...")
    config = load_config()
    ensure_directories(config)
    
    # Create output directory for API
    os.makedirs(config['OUTPUT_DIR'], exist_ok=True)
    os.makedirs(config['UPLOAD_DIR'], exist_ok=True)
    
    # Mount static files for serving generated images
    app.mount("/mockups", StaticFiles(directory=config['OUTPUT_DIR']), name="mockups")
    
    # Initialize generator
    generator = MockupGenerator()
    logger.info("API server started successfully")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "AI Product Mockup Generator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate": "/generate",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global generator
    
    model_loaded = generator is not None and generator.controlnet_pipeline is not None
    device = generator.device if generator is not None else "unknown"
    
    return HealthResponse(
        status="healthy",
        model_loaded=model_loaded,
        device=device
    )


@app.post("/generate", response_model=MockupResponse)
async def generate_mockup(
    logo: UploadFile = File(..., description="Logo or design image file"),
    product_type: ProductType = Form(..., description="Type of product"),
    style: MockupStyle = Form(MockupStyle.STUDIO, description="Mockup style"),
    num_variations: int = Form(1, ge=1, le=4, description="Number of variations"),
    guidance_scale: Optional[float] = Form(None, description="Guidance scale"),
    num_inference_steps: Optional[int] = Form(None, description="Number of inference steps"),
    controlnet_conditioning_scale: Optional[float] = Form(None, description="ControlNet scale"),
    seed: Optional[int] = Form(None, description="Random seed")
):
    """
    Generate product mockup from uploaded logo.
    
    - **logo**: Image file (PNG, JPG, JPEG, WEBP)
    - **product_type**: One of: tshirt, mug, phone_case, packaging
    - **style**: One of: studio, reallife, flatlay
    - **num_variations**: Number of mockup variations (1-4)
    - **guidance_scale**: Optional guidance scale (1.0-20.0)
    - **num_inference_steps**: Optional inference steps (10-100)
    - **controlnet_conditioning_scale**: Optional ControlNet scale (0.0-2.0)
    - **seed**: Optional random seed for reproducibility
    """
    global generator, config
    
    try:
        # Validate file type
        if not logo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        logger.info(f"Processing upload: {logo.filename}")
        image_data = await logo.read()
        logo_image = Image.open(io.BytesIO(image_data))
        
        # Load models if not already loaded
        if generator.controlnet_pipeline is None:
            logger.info("Loading models...")
            generator.load_models()
        
        # Generate mockups
        logger.info(f"Generating {num_variations} mockup(s) for {product_type.value} in {style.value} style")
        mockups = generator.generate_mockup(
            logo_image=logo_image,
            product_type=product_type.value,
            style=style.value,
            num_variations=num_variations,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            controlnet_conditioning_scale=controlnet_conditioning_scale,
            seed=seed
        )
        
        # Save generated mockups and create URLs
        mockup_urls = []
        for idx, mockup in enumerate(mockups):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mockup_{product_type.value}_{style.value}_{timestamp}_{idx}.png"
            file_path = os.path.join(config['OUTPUT_DIR'], filename)
            
            mockup.save(file_path)
            mockup_url = f"/mockups/{filename}"
            mockup_urls.append(mockup_url)
            logger.info(f"Saved mockup to {file_path}")
        
        return MockupResponse(
            success=True,
            message=f"Successfully generated {len(mockups)} mockup(s)",
            mockup_urls=mockup_urls,
            num_generated=len(mockups)
        )
        
    except Exception as e:
        logger.error(f"Error generating mockup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mockups/{filename}")
async def get_mockup(filename: str):
    """Retrieve a generated mockup image."""
    file_path = os.path.join(config['OUTPUT_DIR'], filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Mockup not found")
    
    return FileResponse(file_path, media_type="image/png")


@app.post("/load-models")
async def load_models():
    """Preload AI models to speed up first generation."""
    global generator
    
    try:
        if generator.controlnet_pipeline is None:
            logger.info("Loading models...")
            generator.load_models()
            return {"success": True, "message": "Models loaded successfully"}
        else:
            return {"success": True, "message": "Models already loaded"}
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/unload-models")
async def unload_models():
    """Unload models to free memory."""
    global generator
    
    try:
        generator.unload_models()
        return {"success": True, "message": "Models unloaded successfully"}
    except Exception as e:
        logger.error(f"Error unloading models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
