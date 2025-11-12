"""
Streamlit web application for Product Mockup Generator.
"""
import streamlit as st
from PIL import Image
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mockup_generator import MockupGenerator
from utils.config_utils import load_config, ensure_directories

# Page configuration
st.set_page_config(
    page_title="AI Product Mockup Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_generator():
    """Initialize and cache the mockup generator."""
    config = load_config()
    ensure_directories(config)
    generator = MockupGenerator()
    return generator


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temp directory."""
    config = load_config()
    upload_dir = config.get('UPLOAD_DIR', 'temp_uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def save_generated_mockup(image: Image.Image, product_type: str, style: str) -> str:
    """Save generated mockup to output directory."""
    config = load_config()
    output_dir = config.get('OUTPUT_DIR', 'generated_mockups')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mockup_{product_type}_{style}_{timestamp}.png"
    file_path = os.path.join(output_dir, filename)
    
    image.save(file_path)
    return file_path


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🎨 AI Product Mockup Generator</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Create stunning product mockups with AI-powered Stable Diffusion</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    
    # Load configuration
    config = load_config()
    
    # Product type selection
    product_types = list(config['PRODUCT_TYPES'].keys())
    product_type = st.sidebar.selectbox(
        "Select Product Type",
        options=product_types,
        format_func=lambda x: config['PRODUCT_TYPES'][x]['name']
    )
    
    # Style selection
    mockup_styles = list(config['MOCKUP_STYLES'].keys())
    style = st.sidebar.selectbox(
        "Select Mockup Style",
        options=mockup_styles,
        format_func=lambda x: config['MOCKUP_STYLES'][x]['name']
    )
    
    st.sidebar.markdown("---")
    
    # Advanced settings
    with st.sidebar.expander("🔧 Advanced Settings"):
        num_variations = st.slider(
            "Number of Variations",
            min_value=1,
            max_value=config['MAX_VARIATIONS'],
            value=1,
            help="Number of different mockup variations to generate"
        )
        
        guidance_scale = st.slider(
            "Guidance Scale",
            min_value=1.0,
            max_value=20.0,
            value=float(config['DEFAULT_GUIDANCE_SCALE']),
            step=0.5,
            help="Higher values make the image more closely follow the prompt"
        )
        
        num_inference_steps = st.slider(
            "Inference Steps",
            min_value=10,
            max_value=100,
            value=config['DEFAULT_NUM_INFERENCE_STEPS'],
            step=5,
            help="More steps generally produce better quality but take longer"
        )
        
        controlnet_scale = st.slider(
            "ControlNet Strength",
            min_value=0.0,
            max_value=2.0,
            value=float(config['DEFAULT_CONTROLNET_CONDITIONING_SCALE']),
            step=0.1,
            help="Controls how strongly ControlNet guides the generation"
        )
        
        use_seed = st.checkbox("Use Random Seed", value=False)
        seed = None
        if use_seed:
            seed = st.number_input("Seed", min_value=0, value=42, step=1)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Your Design")
        
        uploaded_file = st.file_uploader(
            "Choose a logo or design image",
            type=["png", "jpg", "jpeg", "webp"],
            help="Upload your logo, design, or artwork to place on the product"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Design", use_column_width=True)
            
            # Show image info
            st.info(f"📐 Image size: {image.size[0]}x{image.size[1]} | Format: {image.format}")
    
    with col2:
        st.header("✨ Generated Mockups")
        
        if uploaded_file is not None:
            if st.button("🚀 Generate Mockups", type="primary"):
                with st.spinner("🎨 Generating your mockups... This may take a minute..."):
                    try:
                        # Initialize generator
                        generator = get_generator()
                        
                        # Load models if not already loaded
                        if generator.controlnet_pipeline is None:
                            with st.spinner("📦 Loading AI models (first time only)..."):
                                generator.load_models()
                        
                        # Generate mockups
                        image = Image.open(uploaded_file)
                        mockups = generator.generate_mockup(
                            logo_image=image,
                            product_type=product_type,
                            style=style,
                            num_variations=num_variations,
                            guidance_scale=guidance_scale,
                            num_inference_steps=num_inference_steps,
                            controlnet_conditioning_scale=controlnet_scale,
                            seed=seed
                        )
                        
                        # Display and save generated mockups
                        if mockups:
                            st.success(f"✅ Generated {len(mockups)} mockup(s) successfully!")
                            
                            for idx, mockup in enumerate(mockups):
                                st.image(mockup, caption=f"Mockup {idx + 1}", use_column_width=True)
                                
                                # Save and provide download button
                                file_path = save_generated_mockup(mockup, product_type, style)
                                
                                # Convert to bytes for download
                                from io import BytesIO
                                buf = BytesIO()
                                mockup.save(buf, format="PNG")
                                byte_im = buf.getvalue()
                                
                                st.download_button(
                                    label=f"⬇️ Download Mockup {idx + 1}",
                                    data=byte_im,
                                    file_name=f"mockup_{product_type}_{style}_{idx+1}.png",
                                    mime="image/png"
                                )
                        else:
                            st.error("❌ Failed to generate mockups. Please try again.")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.exception(e)
        else:
            st.info("👆 Please upload a design image to get started!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 💡 Tips for Best Results:
    - Use high-resolution logos (at least 512x512 pixels)
    - PNG format with transparent background works best
    - Simple, clear designs produce better mockups
    - Experiment with different styles and settings
    - Try multiple variations to find the perfect mockup
    """)
    
    # Information expander
    with st.expander("ℹ️ About This Tool"):
        st.markdown("""
        **AI Product Mockup Generator** uses state-of-the-art AI technology:
        
        - **Stable Diffusion XL**: Advanced text-to-image generation
        - **ControlNet**: Precise control over logo placement and composition
        - **Inpainting**: Natural blending with product textures
        
        This tool is perfect for:
        - E-commerce product listings
        - Marketing materials
        - Portfolio presentations
        - Client previews
        - Social media content
        
        **Supported Products**: T-shirts, Mugs, Phone Cases, Packaging
        
        **Mockup Styles**: Studio (white background), Real Life (lifestyle shots), Flat Lay (top-down view)
        """)


if __name__ == "__main__":
    main()
