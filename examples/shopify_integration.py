"""
Example integration script for Shopify.
Demonstrates how to use the API for e-commerce platform integration.
"""
import requests
import os
from typing import Dict, Any


class ShopifyMockupIntegration:
    """
    Integration layer for Shopify product mockup generation.
    """
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Initialize the integration.
        
        Args:
            api_url: Base URL of the mockup generator API
        """
        self.api_url = api_url
    
    def check_api_health(self) -> Dict[str, Any]:
        """Check if the API is available."""
        response = requests.get(f"{self.api_url}/health")
        return response.json()
    
    def generate_product_mockup(
        self,
        logo_path: str,
        product_type: str = "tshirt",
        style: str = "studio",
        num_variations: int = 1
    ) -> Dict[str, Any]:
        """
        Generate product mockup for Shopify product.
        
        Args:
            logo_path: Path to logo/design file
            product_type: Type of product (tshirt, mug, phone_case, packaging)
            style: Mockup style (studio, reallife, flatlay)
            num_variations: Number of variations to generate
            
        Returns:
            Dictionary with generation results
        """
        with open(logo_path, "rb") as f:
            files = {"logo": f}
            data = {
                "product_type": product_type,
                "style": style,
                "num_variations": num_variations
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                files=files,
                data=data
            )
            
            return response.json()
    
    def download_mockup(self, mockup_url: str, save_path: str) -> bool:
        """
        Download generated mockup.
        
        Args:
            mockup_url: URL of the mockup (from generation response)
            save_path: Local path to save the mockup
            
        Returns:
            True if successful, False otherwise
        """
        try:
            full_url = f"{self.api_url}{mockup_url}"
            response = requests.get(full_url)
            
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
            return False
        except Exception as e:
            print(f"Error downloading mockup: {e}")
            return False
    
    def process_shopify_product(
        self,
        product_id: str,
        logo_path: str,
        product_type: str = "tshirt"
    ) -> Dict[str, Any]:
        """
        Complete workflow for processing a Shopify product.
        
        Args:
            product_id: Shopify product ID
            logo_path: Path to logo file
            product_type: Type of product
            
        Returns:
            Dictionary with processing results
        """
        print(f"Processing Shopify product {product_id}...")
        
        # Generate mockups
        result = self.generate_product_mockup(
            logo_path=logo_path,
            product_type=product_type,
            style="studio",
            num_variations=3  # Generate 3 variations for the product
        )
        
        if not result.get("success"):
            return {
                "success": False,
                "message": "Mockup generation failed",
                "product_id": product_id
            }
        
        # Download mockups
        downloaded_files = []
        for idx, mockup_url in enumerate(result["mockup_urls"]):
            save_path = f"shopify_mockups/{product_id}_{idx+1}.png"
            os.makedirs("shopify_mockups", exist_ok=True)
            
            if self.download_mockup(mockup_url, save_path):
                downloaded_files.append(save_path)
                print(f"Downloaded: {save_path}")
        
        # In a real integration, you would now upload these to Shopify
        # using the Shopify API
        
        return {
            "success": True,
            "message": f"Generated {len(downloaded_files)} mockups",
            "product_id": product_id,
            "mockup_files": downloaded_files
        }


def example_usage():
    """Example usage of the integration."""
    
    # Initialize integration
    integration = ShopifyMockupIntegration(api_url="http://localhost:8000")
    
    # Check API health
    health = integration.check_api_health()
    print(f"API Status: {health['status']}")
    print(f"Models Loaded: {health['model_loaded']}\n")
    
    # Example: Process a product
    result = integration.process_shopify_product(
        product_id="SHOP_12345",
        logo_path="path/to/your/logo.png",
        product_type="tshirt"
    )
    
    print(f"\nResult: {result}")
    
    # In a real Shopify integration, you would:
    # 1. Listen for new product events from Shopify
    # 2. Generate mockups using this API
    # 3. Upload mockups back to Shopify product images
    # 4. Update product with mockup URLs


if __name__ == "__main__":
    example_usage()
