"""
Utility functions for image processing and manipulation.
"""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple


def preprocess_logo(image: Image.Image, target_size: Tuple[int, int] = (512, 512)) -> Image.Image:
    """
    Preprocess uploaded logo/design for mockup generation.
    
    Args:
        image: Input PIL Image
        target_size: Target size for the processed image
        
    Returns:
        Processed PIL Image
    """
    # Convert to RGBA if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Resize while maintaining aspect ratio
    image.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    # Create a new image with transparent background
    new_image = Image.new('RGBA', target_size, (255, 255, 255, 0))
    
    # Paste the resized image in the center
    offset = ((target_size[0] - image.size[0]) // 2, (target_size[1] - image.size[1]) // 2)
    new_image.paste(image, offset, image if image.mode == 'RGBA' else None)
    
    return new_image


def extract_edges(image: Image.Image, low_threshold: int = 100, high_threshold: int = 200) -> np.ndarray:
    """
    Extract edges from an image using Canny edge detection.
    
    Args:
        image: Input PIL Image
        low_threshold: Lower threshold for Canny edge detection
        high_threshold: Upper threshold for Canny edge detection
        
    Returns:
        Edge map as numpy array
    """
    # Convert PIL Image to numpy array
    img_array = np.array(image.convert('RGB'))
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Apply Canny edge detection
    edges = cv2.Canny(gray, low_threshold, high_threshold)
    
    # Convert to 3-channel image for compatibility
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    
    return edges_rgb


def create_control_image(product_template: Image.Image, logo: Image.Image) -> Image.Image:
    """
    Create a control image by combining product template with logo placement.
    
    Args:
        product_template: Base product template image
        logo: Logo/design to overlay
        
    Returns:
        Control image for ControlNet
    """
    # Create a copy of the template
    control_img = product_template.copy()
    
    # Calculate placement position (center by default)
    position = (
        (control_img.width - logo.width) // 2,
        (control_img.height - logo.height) // 2
    )
    
    # Paste logo with transparency
    if logo.mode == 'RGBA':
        control_img.paste(logo, position, logo)
    else:
        control_img.paste(logo, position)
    
    return control_img


def blend_with_texture(base_image: Image.Image, overlay: Image.Image, alpha: float = 0.7) -> Image.Image:
    """
    Blend an overlay image with a base image to create realistic texture blending.
    
    Args:
        base_image: Base product image
        overlay: Logo/design overlay
        alpha: Blending factor (0-1)
        
    Returns:
        Blended PIL Image
    """
    # Ensure both images are the same size
    if base_image.size != overlay.size:
        overlay = overlay.resize(base_image.size, Image.Resampling.LANCZOS)
    
    # Convert to numpy arrays
    base_array = np.array(base_image.convert('RGB')).astype(np.float32)
    overlay_array = np.array(overlay.convert('RGB')).astype(np.float32)
    
    # Blend images
    blended = (alpha * overlay_array + (1 - alpha) * base_array).astype(np.uint8)
    
    return Image.fromarray(blended)


def create_mask_from_alpha(image: Image.Image) -> Image.Image:
    """
    Create a mask from the alpha channel of an image.
    
    Args:
        image: Input PIL Image with alpha channel
        
    Returns:
        Mask as PIL Image
    """
    if image.mode != 'RGBA':
        # If no alpha channel, create a full mask
        return Image.new('L', image.size, 255)
    
    # Extract alpha channel
    alpha = image.split()[-1]
    
    return alpha


def post_process_mockup(image: Image.Image, enhance: bool = True) -> Image.Image:
    """
    Post-process generated mockup for better quality.
    
    Args:
        image: Generated mockup image
        enhance: Whether to apply enhancement
        
    Returns:
        Post-processed PIL Image
    """
    if not enhance:
        return image
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Apply slight sharpening
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(img_array, -1, kernel * 0.1)
    
    # Ensure values are in valid range
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    
    return Image.fromarray(sharpened)
