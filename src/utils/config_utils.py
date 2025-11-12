"""
Configuration loader utility.
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file. If None, uses default config.yaml
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Get the root directory of the project
        root_dir = Path(__file__).parent.parent.parent
        config_path = root_dir / "config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def get_product_prompt(product_type: str, style: str, config: Dict[str, Any]) -> str:
    """
    Generate a prompt for product mockup generation.
    
    Args:
        product_type: Type of product (tshirt, mug, etc.)
        style: Mockup style (studio, reallife, flatlay)
        config: Configuration dictionary
        
    Returns:
        Generated prompt string
    """
    product_config = config['PRODUCT_TYPES'].get(product_type, {})
    style_config = config['MOCKUP_STYLES'].get(style, {})
    
    base_prompt = product_config.get('base_prompt', 'product photography')
    style_suffix = style_config.get('prompt_suffix', '')
    
    # Format the prompt
    prompt = base_prompt.format(style=style_config.get('name', style))
    prompt = f"{prompt}, {style_suffix}"
    
    return prompt


def ensure_directories(config: Dict[str, Any]) -> None:
    """
    Ensure required directories exist.
    
    Args:
        config: Configuration dictionary
    """
    output_dir = config.get('OUTPUT_DIR', 'generated_mockups')
    upload_dir = config.get('UPLOAD_DIR', 'temp_uploads')
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)
