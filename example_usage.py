"""
Example script demonstrating how to use the MockupGenerator programmatically.
"""
from PIL import Image
from src.mockup_generator import MockupGenerator
from src.utils.config_utils import load_config, ensure_directories


def main():
    """Example usage of the MockupGenerator."""
    
    # Load configuration
    config = load_config()
    ensure_directories(config)
    
    # Initialize generator
    print("Initializing MockupGenerator...")
    generator = MockupGenerator()
    
    # Load models
    print("Loading AI models (this may take a few minutes on first run)...")
    generator.load_models()
    
    # Load your logo/design
    logo_path = "path/to/your/logo.png"  # Change this to your logo path
    print(f"Loading logo from {logo_path}...")
    logo = Image.open(logo_path)
    
    # Generate mockups
    print("Generating mockups...")
    mockups = generator.generate_mockup(
        logo_image=logo,
        product_type="tshirt",  # Options: tshirt, mug, phone_case, packaging
        style="studio",          # Options: studio, reallife, flatlay
        num_variations=2,        # Generate 2 variations
        guidance_scale=7.5,
        num_inference_steps=30,
        seed=42                  # For reproducibility
    )
    
    # Save generated mockups
    output_dir = config['OUTPUT_DIR']
    print(f"\nSaving {len(mockups)} mockup(s) to {output_dir}/")
    
    for idx, mockup in enumerate(mockups):
        output_path = f"{output_dir}/example_mockup_{idx+1}.png"
        mockup.save(output_path)
        print(f"Saved: {output_path}")
    
    print("\nDone! Your mockups are ready.")
    
    # Optional: Unload models to free memory
    # generator.unload_models()


if __name__ == "__main__":
    main()
