# Troubleshooting Guide

This guide helps you resolve common issues with the AI Product Mockup Generator.

## Installation Issues

### Issue: pip install fails

**Symptoms:**
- Error installing torch or other dependencies
- Package version conflicts

**Solutions:**
1. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```

2. Install dependencies one at a time:
   ```bash
   pip install torch torchvision
   pip install diffusers transformers
   pip install -r requirements.txt
   ```

3. Use Python 3.10 specifically:
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Issue: CUDA not found

**Symptoms:**
- Error: "CUDA not available"
- Models running on CPU

**Solutions:**
1. Check CUDA installation:
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. Install CUDA-compatible PyTorch:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. Verify NVIDIA driver:
   ```bash
   nvidia-smi
   ```

## Memory Issues

### Issue: CUDA Out of Memory

**Symptoms:**
- RuntimeError: CUDA out of memory
- Generation crashes mid-process

**Solutions:**

1. **Reduce image size** in `config.yaml`:
   ```yaml
   IMAGE_SIZE: 768  # or 512 instead of 1024
   ```

2. **Reduce inference steps**:
   ```yaml
   DEFAULT_NUM_INFERENCE_STEPS: 20  # instead of 30
   ```

3. **Enable CPU offloading** (already enabled by default):
   ```python
   pipeline.enable_model_cpu_offload()
   pipeline.enable_vae_slicing()
   ```

4. **Clear CUDA cache** between generations:
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

5. **Use CPU instead** by editing generator initialization:
   ```python
   generator = MockupGenerator(device="cpu")
   ```

### Issue: System RAM exhausted

**Symptoms:**
- System becomes unresponsive
- Out of memory errors

**Solutions:**
1. Close other applications
2. Generate fewer variations at once
3. Restart the application between generations
4. Increase system swap space

## Model Loading Issues

### Issue: Model download fails

**Symptoms:**
- Network errors during download
- Incomplete model files

**Solutions:**

1. **Check internet connection**

2. **Set HuggingFace cache directory**:
   ```bash
   export HF_HOME=/path/to/cache
   ```

3. **Download models manually**:
   ```python
   from diffusers import StableDiffusionXLPipeline
   
   # This will download and cache the model
   pipeline = StableDiffusionXLPipeline.from_pretrained(
       "stabilityai/stable-diffusion-xl-base-1.0"
   )
   ```

4. **Use HuggingFace token for private models**:
   ```python
   from huggingface_hub import login
   login(token="your_token_here")
   ```

### Issue: Model loading takes too long

**Symptoms:**
- First generation takes 5+ minutes
- Models re-download every time

**Solutions:**

1. Models are cached after first download
2. Preload models using API endpoint:
   ```bash
   curl -X POST http://localhost:8000/load-models
   ```
3. Keep models in cache (don't delete `~/.cache/huggingface`)

## Generation Quality Issues

### Issue: Poor quality mockups

**Symptoms:**
- Blurry images
- Distorted logos
- Unrealistic results

**Solutions:**

1. **Increase inference steps**:
   ```python
   num_inference_steps=50  # instead of 30
   ```

2. **Adjust guidance scale**:
   ```python
   guidance_scale=8.0  # try values between 7.0-10.0
   ```

3. **Use high-resolution logo**:
   - Minimum 512x512 pixels
   - PNG format with transparent background

4. **Adjust ControlNet strength**:
   ```python
   controlnet_conditioning_scale=0.6  # try 0.5-0.8
   ```

### Issue: Logo placement is inaccurate

**Symptoms:**
- Logo not centered
- Logo distorted or cut off

**Solutions:**

1. **Increase ControlNet conditioning scale**:
   ```python
   controlnet_conditioning_scale=0.8  # instead of 0.5
   ```

2. **Preprocess logo** to center it:
   ```python
   from src.utils.image_utils import preprocess_logo
   processed = preprocess_logo(logo, (512, 512))
   ```

3. **Try inpainting mode** for better blending

## Streamlit Issues

### Issue: Streamlit app won't start

**Symptoms:**
- Port already in use
- Module not found errors

**Solutions:**

1. **Change port**:
   ```bash
   streamlit run app.py --server.port 8502
   ```

2. **Check Python path**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/project"
   ```

3. **Reinstall Streamlit**:
   ```bash
   pip uninstall streamlit
   pip install streamlit
   ```

### Issue: File upload fails

**Symptoms:**
- Cannot upload images
- File size errors

**Solutions:**

1. **Increase max upload size** in `.streamlit/config.toml`:
   ```toml
   [server]
   maxUploadSize = 200
   ```

2. **Check file format** - use PNG, JPG, JPEG, or WEBP

3. **Reduce image size** before uploading

## API Issues

### Issue: FastAPI server won't start

**Symptoms:**
- Port 8000 already in use
- Import errors

**Solutions:**

1. **Change port**:
   ```bash
   uvicorn src.api.server:app --port 8001
   ```

2. **Kill existing process**:
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

3. **Check imports**:
   ```bash
   python -c "from src.api.server import app"
   ```

### Issue: API requests timeout

**Symptoms:**
- 504 Gateway Timeout
- Long wait times

**Solutions:**

1. **Increase timeout** in client:
   ```python
   response = requests.post(url, files=files, timeout=300)
   ```

2. **Reduce generation complexity**:
   - Fewer inference steps
   - Fewer variations

3. **Preload models** before first request

## Performance Issues

### Issue: Generation is very slow

**Symptoms:**
- Takes 5+ minutes per mockup
- CPU usage at 100%

**Solutions:**

1. **Use GPU**:
   - Check CUDA availability
   - Ensure NVIDIA drivers installed

2. **Optimize settings**:
   ```yaml
   DEFAULT_NUM_INFERENCE_STEPS: 20
   IMAGE_SIZE: 768
   ```

3. **Enable all optimizations** (already default):
   ```python
   pipeline.enable_model_cpu_offload()
   pipeline.enable_vae_slicing()
   pipeline.enable_attention_slicing()
   ```

4. **Use smaller model** (optional):
   ```yaml
   MODEL_ID: "stabilityai/stable-diffusion-2-1"
   ```

## Docker Issues

### Issue: Docker build fails

**Symptoms:**
- Build errors
- Missing dependencies

**Solutions:**

1. **Build with no cache**:
   ```bash
   docker build --no-cache -t mockup-generator .
   ```

2. **Check Docker version**:
   ```bash
   docker --version
   ```

3. **Increase Docker memory** in Docker Desktop settings

### Issue: GPU not accessible in Docker

**Symptoms:**
- CUDA not available in container
- Running on CPU

**Solutions:**

1. **Install NVIDIA Container Toolkit**:
   ```bash
   sudo apt-get install nvidia-container-toolkit
   ```

2. **Run with GPU**:
   ```bash
   docker run --gpus all -p 8501:8501 mockup-generator
   ```

3. **Verify GPU in container**:
   ```bash
   docker run --gpus all mockup-generator nvidia-smi
   ```

## Common Error Messages

### "No module named 'src'"

**Solution:**
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
python app.py
```

### "Pipeline expects a torch.FloatTensor"

**Solution:**
Ensure input image is properly converted:
```python
logo_image = logo_image.convert('RGB')
```

### "Connection refused"

**Solution:**
1. Check if server is running
2. Verify correct port
3. Check firewall settings

## Getting Help

If you're still experiencing issues:

1. **Check logs** for detailed error messages
2. **Search issues** on [GitHub](https://github.com/yadavanujkumar/Product-Mockup-Generator-for-E-commerce/issues)
3. **Create new issue** with:
   - Error message
   - System information
   - Steps to reproduce
   - Python version and installed packages

## System Requirements Check

Run this script to check your system:

```python
import sys
import torch

print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

Minimum requirements:
- Python 3.8+
- 16GB RAM (32GB recommended)
- 10GB+ free disk space
- NVIDIA GPU with 8GB+ VRAM (recommended)
