"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ProductType(str, Enum):
    """Available product types."""
    TSHIRT = "tshirt"
    MUG = "mug"
    PHONE_CASE = "phone_case"
    PACKAGING = "packaging"


class MockupStyle(str, Enum):
    """Available mockup styles."""
    STUDIO = "studio"
    REALLIFE = "reallife"
    FLATLAY = "flatlay"


class MockupRequest(BaseModel):
    """Request model for mockup generation."""
    product_type: ProductType = Field(..., description="Type of product for mockup")
    style: MockupStyle = Field(default=MockupStyle.STUDIO, description="Style of mockup")
    num_variations: int = Field(default=1, ge=1, le=4, description="Number of variations to generate")
    guidance_scale: Optional[float] = Field(default=None, ge=1.0, le=20.0, description="Guidance scale for generation")
    num_inference_steps: Optional[int] = Field(default=None, ge=10, le=100, description="Number of inference steps")
    controlnet_conditioning_scale: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="ControlNet conditioning scale")
    seed: Optional[int] = Field(default=None, ge=0, description="Random seed for reproducibility")


class MockupResponse(BaseModel):
    """Response model for mockup generation."""
    success: bool = Field(..., description="Whether generation was successful")
    message: str = Field(..., description="Response message")
    mockup_urls: List[str] = Field(default=[], description="URLs of generated mockups")
    num_generated: int = Field(default=0, description="Number of mockups generated")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="API status")
    model_loaded: bool = Field(..., description="Whether models are loaded")
    device: str = Field(..., description="Device being used (cuda/cpu)")
