"""
Core mockup generator using Stable Diffusion XL and ControlNet.
"""
import torch
from diffusers import (
    StableDiffusionXLControlNetPipeline,
    StableDiffusionXLInpaintPipeline,
    ControlNetModel,
    AutoencoderKL
)
from PIL import Image
import numpy as np
from typing import List, Optional, Dict, Any
import logging

from ..utils.image_utils import (
    preprocess_logo,
    extract_edges,
    post_process_mockup,
    create_mask_from_alpha
)
from ..utils.config_utils import load_config, get_product_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockupGenerator:
    """
    AI-powered mockup generator using Stable Diffusion XL and ControlNet.
    """
    
    def __init__(self, config_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize the mockup generator.
        
        Args:
            config_path: Path to configuration file
            device: Device to run models on ('cuda', 'cpu', or None for auto-detect)
        """
        self.config = load_config(config_path)
        
        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Using device: {self.device}")
        
        self.controlnet_pipeline = None
        self.inpaint_pipeline = None
        
    def load_models(self):
        """Load Stable Diffusion XL and ControlNet models."""
        try:
            logger.info("Loading ControlNet model...")
            controlnet = ControlNetModel.from_pretrained(
                self.config['CONTROLNET_MODEL'],
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            logger.info("Loading Stable Diffusion XL pipeline...")
            self.controlnet_pipeline = StableDiffusionXLControlNetPipeline.from_pretrained(
                self.config['MODEL_ID'],
                controlnet=controlnet,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None
            )
            
            self.controlnet_pipeline.to(self.device)
            
            # Enable memory optimizations
            if self.device == "cuda":
                self.controlnet_pipeline.enable_model_cpu_offload()
                self.controlnet_pipeline.enable_vae_slicing()
            
            logger.info("Loading inpainting pipeline...")
            self.inpaint_pipeline = StableDiffusionXLInpaintPipeline.from_pretrained(
                self.config['MODEL_ID'],
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None
            )
            
            self.inpaint_pipeline.to(self.device)
            
            if self.device == "cuda":
                self.inpaint_pipeline.enable_model_cpu_offload()
                self.inpaint_pipeline.enable_vae_slicing()
            
            logger.info("Models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def generate_mockup(
        self,
        logo_image: Image.Image,
        product_type: str,
        style: str = "studio",
        num_variations: int = 1,
        guidance_scale: float = None,
        num_inference_steps: int = None,
        controlnet_conditioning_scale: float = None,
        seed: Optional[int] = None
    ) -> List[Image.Image]:
        """
        Generate product mockup with logo placement.
        
        Args:
            logo_image: Input logo/design as PIL Image
            product_type: Type of product ('tshirt', 'mug', 'phone_case', 'packaging')
            style: Mockup style ('studio', 'reallife', 'flatlay')
            num_variations: Number of mockup variations to generate
            guidance_scale: Guidance scale for generation
            num_inference_steps: Number of inference steps
            controlnet_conditioning_scale: ControlNet conditioning scale
            seed: Random seed for reproducibility
            
        Returns:
            List of generated mockup images
        """
        if self.controlnet_pipeline is None:
            self.load_models()
        
        # Use config defaults if not provided
        if guidance_scale is None:
            guidance_scale = self.config['DEFAULT_GUIDANCE_SCALE']
        if num_inference_steps is None:
            num_inference_steps = self.config['DEFAULT_NUM_INFERENCE_STEPS']
        if controlnet_conditioning_scale is None:
            controlnet_conditioning_scale = self.config['DEFAULT_CONTROLNET_CONDITIONING_SCALE']
        
        # Preprocess logo
        logger.info("Preprocessing logo...")
        processed_logo = preprocess_logo(logo_image, (self.config['IMAGE_SIZE'], self.config['IMAGE_SIZE']))
        
        # Extract edges for ControlNet guidance
        logger.info("Extracting edge map...")
        control_image = extract_edges(processed_logo)
        control_image = Image.fromarray(control_image)
        
        # Generate prompt
        prompt = get_product_prompt(product_type, style, self.config)
        negative_prompt = self.config['NEGATIVE_PROMPT']
        
        logger.info(f"Generating {num_variations} mockup(s)...")
        logger.info(f"Prompt: {prompt}")
        
        generated_images = []
        
        for i in range(num_variations):
            # Set seed for reproducibility
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed + i)
            
            try:
                # Generate with ControlNet
                output = self.controlnet_pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image=control_image,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    controlnet_conditioning_scale=controlnet_conditioning_scale,
                    generator=generator,
                    height=self.config['IMAGE_SIZE'],
                    width=self.config['IMAGE_SIZE']
                )
                
                generated_image = output.images[0]
                
                # Post-process
                generated_image = post_process_mockup(generated_image, enhance=True)
                
                generated_images.append(generated_image)
                logger.info(f"Generated mockup {i+1}/{num_variations}")
                
            except Exception as e:
                logger.error(f"Error generating mockup {i+1}: {e}")
                continue
        
        return generated_images
    
    def generate_with_inpainting(
        self,
        base_image: Image.Image,
        logo_image: Image.Image,
        mask_image: Optional[Image.Image] = None,
        product_type: str = "tshirt",
        style: str = "studio",
        guidance_scale: float = None,
        num_inference_steps: int = None,
        seed: Optional[int] = None
    ) -> Image.Image:
        """
        Generate mockup using inpainting for more natural blending.
        
        Args:
            base_image: Base product image
            logo_image: Logo/design to blend
            mask_image: Mask indicating where to apply logo (white = inpaint area)
            product_type: Type of product
            style: Mockup style
            guidance_scale: Guidance scale
            num_inference_steps: Number of inference steps
            seed: Random seed
            
        Returns:
            Generated mockup image
        """
        if self.inpaint_pipeline is None:
            self.load_models()
        
        # Use config defaults if not provided
        if guidance_scale is None:
            guidance_scale = self.config['DEFAULT_GUIDANCE_SCALE']
        if num_inference_steps is None:
            num_inference_steps = self.config['DEFAULT_NUM_INFERENCE_STEPS']
        
        # Create mask if not provided
        if mask_image is None:
            mask_image = create_mask_from_alpha(logo_image)
        
        # Resize images to match
        target_size = (self.config['IMAGE_SIZE'], self.config['IMAGE_SIZE'])
        base_image = base_image.resize(target_size, Image.Resampling.LANCZOS)
        mask_image = mask_image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Generate prompt
        prompt = get_product_prompt(product_type, style, self.config)
        prompt += ", with custom logo design blended naturally on the surface"
        negative_prompt = self.config['NEGATIVE_PROMPT']
        
        logger.info("Generating mockup with inpainting...")
        
        # Set seed
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        
        try:
            output = self.inpaint_pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=base_image,
                mask_image=mask_image,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
                height=self.config['IMAGE_SIZE'],
                width=self.config['IMAGE_SIZE']
            )
            
            generated_image = output.images[0]
            generated_image = post_process_mockup(generated_image, enhance=True)
            
            return generated_image
            
        except Exception as e:
            logger.error(f"Error in inpainting: {e}")
            raise
    
    def unload_models(self):
        """Unload models to free memory."""
        if self.controlnet_pipeline is not None:
            del self.controlnet_pipeline
            self.controlnet_pipeline = None
        
        if self.inpaint_pipeline is not None:
            del self.inpaint_pipeline
            self.inpaint_pipeline = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Models unloaded")
