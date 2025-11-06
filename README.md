<div align="center">
  <a href="https://viscribe.ai"><img src="https://raw.githubusercontent.com/ViscribeAI/python-sdk/refs/heads/main/assets/viscribe-logo.png" alt="Viscribe Logo" width="200"></a>
</div>

# 🌐 ViscribeAI -  Python SDK

[![PyPI version](https://badge.fury.io/py/viscribe.svg)](https://badge.fury.io/py/viscribe)
[![Python Support](https://img.shields.io/pypi/pyversions/viscribe.svg)](https://pypi.org/project/viscribe/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/viscribe/badge/?version=latest)](https://docs.viscribe.ai)

Official [Python SDK](https://viscribe.ai) for ViscribeAI - AI-powered image understanding and analysis.

> 🎁 **Get started with free credits!** Visit [dashboard.viscribe.ai](https://dashboard.viscribe.ai) to sign up and get your API key.

## 📦 Installation

```bash
pip install viscribe
```

## 🚀 Features

- 🖼️ AI-powered image description, extraction, classification, VQA (Visual Question Answering), and comparison
- 🔄 Both sync and async clients
- 📊 Structured output with Pydantic schemas
- 🔍 Detailed logging
- ⚡ Automatic retries
- 🔐 Secure authentication

## 🎯 Quick Start

```python
from viscribe import Client

client = Client(api_key="your-api-key-here")
```

> **Note:**
> You can set the `VISCRIBE_API_KEY` environment variable and initialize the client without parameters: `client = Client()`

## 📚 Image Endpoints

### 1. Describe Image
Generate a natural language description of an image, optionally with tags.

```python
from viscribe import Client
client = Client(api_key="your-api-key-here")

resp = client.describe_image(
    image_url="https://img.com/cat.jpg",
    generate_tags=True
)
print(resp)
```

### 2. Classify Image
Classify an image into one or more categories.

```python
resp = client.classify_image(
    image_url="https://img.com/cat.jpg",
    classes=["cat", "dog"]
)
print(resp)
```

### 3. Visual Question Answering (VQA)
Ask a question about the content of an image and get an answer.

```python
resp = client.ask_image(
    image_url="https://img.com/car.jpg",
    question="What color is the car?"
)
print(resp)
```

### 4. Extract Structured Data from Image
Extract structured data from an image using either simple fields or an advanced schema.

#### Simple Fields (Recommended for basic extraction)
Use simple fields for straightforward data extraction (max 10 fields):

```python
resp = client.extract_image(
    image_url="https://img.com/prod.jpg",
    fields=[
        {"name": "product_name", "type": "text", "description": "Name of the product"},
        {"name": "price", "type": "number", "description": "Product price"},
        {"name": "tags", "type": "array_text", "description": "Product tags"},
    ]
)
print(resp.extracted_data)
```

**Field Types:**
- `text`: Single text value
- `number`: Single numeric value
- `array_text`: Array of text values (max 5 items)
- `array_number`: Array of numeric values (max 5 items)

#### Advanced Schema (For complex/nested structures)
Use advanced schema for complex nested structures or when you need more control:

```python
from pydantic import BaseModel

class Product(BaseModel):
    product_name: str
    price: float
    specifications: dict

resp = client.extract_image(
    image_url="https://img.com/prod.jpg",
    advanced_schema=Product  # Pass the class directly
)
print(resp.extracted_data)
```

> **Note:** Either `fields` or `advanced_schema` must be provided, not both.

### 5. Compare Images
Compare two images and get a description of their similarities and differences.

```python
resp = client.compare_images(
    image1_url="https://img.com/cat1.jpg",
    image2_url="https://img.com/cat2.jpg"
)
print(resp)
```

## 👤 User Endpoints

Check credits and submit feedback.

### Get Credits
```python
credits = client.get_credits()
print(credits)
```

### Submit Feedback
```python
feedback_response = client.submit_feedback(
    request_id="your-request-id",
    rating=5,  # Rating from 1-5
    feedback_text="Perfect image description!",
)
print(feedback_response)
```

## ⚡ Async Usage

All endpoints support async operations:

```python
import asyncio
from viscribe import AsyncClient

async def main():
    client = AsyncClient(api_key="your-api-key-here")
    resp = await client.describe_image({"image_url": "https://img.com/cat.jpg"})
    print(resp)
    # ... use other endpoints as above

asyncio.run(main())
```

## 📖 Documentation

For detailed documentation, visit [docs.viscribe.ai](https://docs.viscribe.ai)

## 🛠️ Development

For information about setting up the development environment and contributing to the project, see our [Contributing Guide](CONTRIBUTING.md).

## 💬 Support & Feedback

- 📧 Email: support@viscribe.ai
- 💻 GitHub Issues: [Create an issue](https://github.com/ViscribeAI/python-sdk/issues)
- 🌟 Feature Requests: [Request a feature](https://github.com/ViscribeAI/python-sdk/issues/new)
- ⭐ API Feedback: You can also submit feedback programmatically using the feedback endpoint:
  ```python
  from viscribe import Client

  client = Client(api_key="your-api-key-here")

  client.submit_feedback(
      request_id="your-request-id",
      rating=5,
      feedback_text="Great results!"
  )
  ```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Website](https://viscribe.ai)
- [Documentation](https://docs.viscribe.ai)
- [GitHub](https://github.com/ViscribeAI/python-sdk)

---

> 🎁 **Get started with free credits!** Visit [dashboard.viscribe.ai](https://dashboard.viscribe.ai) to sign up and get your API key.

Made with ❤️ by [ViscribeAI](https://viscribe.ai)
