"""
Test API endpoints with example requests.
"""
import requests
import json
from pathlib import Path


API_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_generate_mockup(logo_path: str):
    """Test mockup generation endpoint."""
    print(f"Testing mockup generation with {logo_path}...")
    
    with open(logo_path, "rb") as f:
        files = {"logo": f}
        data = {
            "product_type": "tshirt",
            "style": "studio",
            "num_variations": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 30
        }
        
        response = requests.post(f"{API_URL}/generate", files=files, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print(f"✅ Successfully generated {result['num_generated']} mockup(s)")
                for url in result["mockup_urls"]:
                    print(f"   Mockup URL: {API_URL}{url}")
            else:
                print(f"❌ Generation failed: {result['message']}")


def test_load_models():
    """Test model loading endpoint."""
    print("Testing model loading endpoint...")
    response = requests.post(f"{API_URL}/load-models")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def main():
    """Run API tests."""
    print("=" * 50)
    print("AI Product Mockup Generator - API Test Suite")
    print("=" * 50 + "\n")
    
    # Test health check
    try:
        test_health()
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")
    
    # Test model loading
    try:
        test_load_models()
    except Exception as e:
        print(f"❌ Model loading failed: {e}\n")
    
    # Test mockup generation
    logo_path = "path/to/your/logo.png"  # Change this to your logo path
    
    if Path(logo_path).exists():
        try:
            test_generate_mockup(logo_path)
        except Exception as e:
            print(f"❌ Mockup generation failed: {e}\n")
    else:
        print(f"⚠️ Logo file not found: {logo_path}")
        print("Please update the logo_path variable in the script\n")
    
    print("=" * 50)
    print("Test suite completed")
    print("=" * 50)


if __name__ == "__main__":
    main()
