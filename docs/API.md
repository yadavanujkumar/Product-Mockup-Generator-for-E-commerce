# API Documentation

## AI Product Mockup Generator API

This document describes the REST API endpoints for the AI Product Mockup Generator.

### Base URL

```
http://localhost:8000
```

### Authentication

Currently, no authentication is required. For production use, implement appropriate authentication mechanisms.

---

## Endpoints

### 1. Health Check

Check the API status and model loading state.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Generate Mockup

Generate product mockup from an uploaded logo/design.

**Endpoint:** `POST /generate`

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description | Values |
|-----------|------|----------|-------------|--------|
| logo | File | Yes | Logo/design image file | PNG, JPG, JPEG, WEBP |
| product_type | String | Yes | Type of product | tshirt, mug, phone_case, packaging |
| style | String | No | Mockup style (default: studio) | studio, reallife, flatlay |
| num_variations | Integer | No | Number of variations (default: 1) | 1-4 |
| guidance_scale | Float | No | Guidance scale | 1.0-20.0 |
| num_inference_steps | Integer | No | Inference steps | 10-100 |
| controlnet_conditioning_scale | Float | No | ControlNet strength | 0.0-2.0 |
| seed | Integer | No | Random seed | Any integer >= 0 |

**Response:**
```json
{
  "success": true,
  "message": "Successfully generated 2 mockup(s)",
  "mockup_urls": [
    "/mockups/mockup_tshirt_studio_20231112_143000_0.png",
    "/mockups/mockup_tshirt_studio_20231112_143000_1.png"
  ],
  "num_generated": 2
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -F "logo=@/path/to/logo.png" \
  -F "product_type=tshirt" \
  -F "style=studio" \
  -F "num_variations=2" \
  -F "guidance_scale=7.5" \
  -F "num_inference_steps=30"
```

**Example (Python):**
```python
import requests

with open("logo.png", "rb") as f:
    files = {"logo": f}
    data = {
        "product_type": "tshirt",
        "style": "studio",
        "num_variations": 2
    }
    response = requests.post("http://localhost:8000/generate", 
                           files=files, data=data)
    result = response.json()
    print(result)
```

---

### 3. Get Mockup Image

Retrieve a generated mockup image.

**Endpoint:** `GET /mockups/{filename}`

**Parameters:**
- `filename`: Name of the mockup file (from generate response)

**Response:** Image file (PNG)

**Example:**
```bash
curl http://localhost:8000/mockups/mockup_tshirt_studio_20231112_143000_0.png \
  -o downloaded_mockup.png
```

---

### 4. Load Models

Preload AI models into memory for faster generation.

**Endpoint:** `POST /load-models`

**Response:**
```json
{
  "success": true,
  "message": "Models loaded successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/load-models
```

**Note:** Models are automatically loaded on first generation request, but this endpoint allows preloading.

---

### 5. Unload Models

Unload models from memory to free resources.

**Endpoint:** `POST /unload-models`

**Response:**
```json
{
  "success": true,
  "message": "Models unloaded successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/unload-models
```

---

## Product Types

| Value | Description |
|-------|-------------|
| `tshirt` | T-shirt mockups |
| `mug` | Ceramic mug mockups |
| `phone_case` | Phone case mockups |
| `packaging` | Product packaging mockups |

## Mockup Styles

| Value | Description |
|-------|-------------|
| `studio` | Professional studio lighting with white background |
| `reallife` | Lifestyle photography in natural environment |
| `flatlay` | Top-down flat lay composition |

## Error Responses

**400 Bad Request:**
```json
{
  "detail": "File must be an image"
}
```

**404 Not Found:**
```json
{
  "detail": "Mockup not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error message describing the issue"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding rate limiting based on your needs.

## Best Practices

1. **Preload Models:** Use `/load-models` endpoint before generating mockups to reduce first-generation latency
2. **Optimal Settings:**
   - `guidance_scale`: 7.0-8.0 for balanced results
   - `num_inference_steps`: 30-50 for good quality/speed trade-off
   - `controlnet_conditioning_scale`: 0.5-0.7 for accurate logo placement
3. **Image Upload:** 
   - Use PNG format with transparent background for best results
   - Minimum resolution: 512x512 pixels
   - Maximum file size: 10MB
4. **Batch Processing:** Generate multiple variations in a single request for efficiency

## Interactive Documentation

FastAPI provides interactive API documentation at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## E-commerce Integration Examples

### Shopify Integration

```javascript
// Shopify app webhook handler
app.post('/webhooks/products/create', async (req, res) => {
  const product = req.body;
  const logoUrl = product.images[0].src;
  
  // Download logo
  const logoBuffer = await downloadImage(logoUrl);
  
  // Generate mockup
  const formData = new FormData();
  formData.append('logo', logoBuffer, 'logo.png');
  formData.append('product_type', 'tshirt');
  formData.append('style', 'studio');
  formData.append('num_variations', '3');
  
  const response = await fetch('http://localhost:8000/generate', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  // Upload mockups back to Shopify
  for (const mockupUrl of result.mockup_urls) {
    await uploadToShopify(product.id, mockupUrl);
  }
});
```

### Etsy Integration

Similar approach using Etsy's API to fetch product images and upload generated mockups.

---

## Support

For issues or questions:
1. Check the [GitHub Issues](https://github.com/yadavanujkumar/Product-Mockup-Generator-for-E-commerce/issues)
2. Review the main [README](../README.md)
3. Consult the interactive API docs at `/docs`
