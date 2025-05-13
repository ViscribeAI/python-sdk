import pytest
import responses
from viscribe.client import Client
from viscribe.models.image import (
    ImageDescribeRequest, ImageExtractRequest, ImageClassifyRequest, ImageAskRequest, ImageCompareRequest
)
from tests.utils import generate_mock_api_key

@pytest.fixture
def mock_api_key():
    return generate_mock_api_key()

@responses.activate
def test_describe_image(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.viscribe.ai/v1/images/describe",
        json={
            "request_id": "req-1",
            "credits_used": 1,
            "image_description": "A cat on a mat.",
            "tags": ["cat", "mat"]
        },
    )
    req = ImageDescribeRequest(image_url="https://img.com/cat.jpg")
    with Client(api_key=mock_api_key) as client:
        resp = client.describe_image(
            image_url=req.image_url,
            image_base64=req.image_base64,
            instruction=req.instruction,
            generate_tags=req.generate_tags,
        )
        assert resp.request_id == "req-1"
        assert resp.image_description == "A cat on a mat."
        assert resp.tags == ["cat", "mat"]

@responses.activate
def test_extract_image(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.viscribe.ai/v1/images/extract",
        json={
            "request_id": "req-2",
            "credits_used": 2,
            "extracted_data": {"product_name": "Widget", "price": 9.99}
        },
    )
    req = ImageExtractRequest(image_url="https://img.com/prod.jpg", output_schema={"type": "object"})
    with Client(api_key=mock_api_key) as client:
        resp = client.extract_image(
            image_url=req.image_url,
            image_base64=req.image_base64,
            output_schema=req.output_schema,
            instruction=req.instruction,
        )
        assert resp.request_id == "req-2"
        assert resp.extracted_data["product_name"] == "Widget"
        assert resp.extracted_data["price"] == 9.99

@responses.activate
def test_classify_image(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.viscribe.ai/v1/images/classify",
        json={
            "request_id": "req-3",
            "credits_used": 1,
            "classification": ["cat"]
        },
    )
    req = ImageClassifyRequest(image_url="https://img.com/cat.jpg", classes=["cat", "dog"])
    with Client(api_key=mock_api_key) as client:
        resp = client.classify_image(
            image_url=req.image_url,
            image_base64=req.image_base64,
            classes=req.classes,
            class_descriptions=req.class_descriptions,
            instruction=req.instruction,
            multi_label=req.multi_label,
        )
        assert resp.request_id == "req-3"
        assert resp.classification == ["cat"]

@responses.activate
def test_ask_image(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.viscribe.ai/v1/images/ask",
        json={
            "request_id": "req-4",
            "credits_used": 1,
            "answer": "Blue"
        },
    )
    req = ImageAskRequest(image_url="https://img.com/car.jpg", question="What color is the car?")
    with Client(api_key=mock_api_key) as client:
        resp = client.ask_image(
            image_url=req.image_url,
            image_base64=req.image_base64,
            question=req.question,
        )
        assert resp.request_id == "req-4"
        assert resp.answer == "Blue"

@responses.activate
def test_compare_images(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.viscribe.ai/v1/images/compare",
        json={
            "request_id": "req-5",
            "credits_used": 2,
            "comparison_result": "Both images show cats, but one is black and one is white."
        },
    )
    req = ImageCompareRequest(image1_url="https://img.com/cat1.jpg", image2_url="https://img.com/cat2.jpg")
    with Client(api_key=mock_api_key) as client:
        resp = client.compare_images(
            image1_url=req.image1_url,
            image1_base64=req.image1_base64,
            image2_url=req.image2_url,
            image2_base64=req.image2_base64,
            instruction=req.instruction,
        )
        assert resp.request_id == "req-5"
        assert "cats" in resp.comparison_result
