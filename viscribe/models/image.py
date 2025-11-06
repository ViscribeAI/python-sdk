from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from viscribe.utils.helpers import validate_base64_image, validate_url_format

# 1. Image Endpoints


class ImageSourceBase(BaseModel):
    image_url: Optional[str] = Field(default=None, description="URL of the image.")
    image_base64: Optional[str] = Field(
        default=None, description="Base64 encoded string of the image."
    )

    @model_validator(mode="before")
    @classmethod
    def check_image_source(cls, values):
        """Ensure exactly one image source is provided and validate formats."""
        url = values.get("image_url")
        b64 = values.get("image_base64")

        if not url and not b64:
            raise ValueError("Either image_url or image_base64 must be provided.")
        if url and b64:
            raise ValueError("Provide either image_url or image_base64, not both.")

        # Validate URL format if provided
        if url:
            try:
                validate_url_format(url)
            except ValueError as e:
                raise ValueError(f"Invalid image_url: {str(e)}")

        # Validate base64 format if provided
        if b64:
            try:
                validate_base64_image(b64)
            except ValueError as e:
                raise ValueError(f"Invalid image_base64: {str(e)}")

        return values


class ImageDescribeRequest(ImageSourceBase):
    instruction: Optional[str] = None
    generate_tags: bool = True


class ImageDescribeResponse(BaseModel):
    request_id: str
    credits_used: int
    image_description: str
    tags: Optional[List[str]] = None


class ExtractField(BaseModel):
    """Simple field definition for extraction."""

    name: str = Field(..., description="Field name")
    type: str = Field(
        ..., description="Field type: 'text', 'number', 'array_text', or 'array_number'"
    )
    description: Optional[str] = Field(
        None, description="Optional description to guide extraction"
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        valid_types = ["text", "number", "array_text", "array_number"]
        if v not in valid_types:
            raise ValueError(f"type must be one of {valid_types}")
        return v


class ImageExtractRequest(ImageSourceBase):
    fields: Optional[List[ExtractField]] = Field(
        default=None,
        description="Simple list of fields to extract (max 10). Each field can be text, number, array_text (max 5), or array_number (max 5).",
        max_length=10,
    )
    advanced_schema: Optional[dict] = Field(
        default=None,
        description="Advanced: Full JSON schema for complex extraction. Use this for nested structures.",
    )
    instruction: Optional[str] = Field(
        default=None,
        description="Optional instruction to guide the extraction process.",
    )

    @model_validator(mode="after")
    def check_schema_or_fields(self):
        """Ensure either fields or advanced_schema is provided, not both."""
        if not self.fields and not self.advanced_schema:
            raise ValueError("Either 'fields' or 'advanced_schema' must be provided")
        if self.fields and self.advanced_schema:
            raise ValueError("Provide either 'fields' or 'advanced_schema', not both")

        # Validate advanced_schema if provided
        if self.advanced_schema:
            if (
                not isinstance(self.advanced_schema, dict)
                or self.advanced_schema.get("type") != "object"
                or not self.advanced_schema.get("properties")
            ):
                raise ValueError(
                    "advanced_schema must be a valid JSON object schema with 'type': 'object' and a 'properties' field."
                )
        return self


class ImageExtractResponse(BaseModel):
    request_id: str
    credits_used: int
    extracted_data: Dict[str, Any]


class ImageClassifyRequest(ImageSourceBase):
    classes: Optional[List[str]] = None
    class_descriptions: Optional[Dict[str, str]] = None
    instruction: Optional[str] = None
    multi_label: bool = False


class ImageClassifyResponse(BaseModel):
    request_id: str
    credits_used: int
    classification: List[str]


class ImageAskRequest(ImageSourceBase):
    question: str


class ImageAskResponse(BaseModel):
    request_id: str
    credits_used: int
    answer: str


class ImageCompareRequest(BaseModel):
    image1_url: Optional[str] = None
    image1_base64: Optional[str] = None
    image2_url: Optional[str] = None
    image2_base64: Optional[str] = None
    instruction: Optional[str] = Field(
        default="Describe the similarities and differences between these two images."
    )


class ImageCompareResponse(BaseModel):
    request_id: str
    credits_used: int
    comparison_result: str


# 2. User Endpoints


class CreditsResponse(BaseModel):
    remaining_credits: int
    total_credits_used: int


class FeedbackRequest(BaseModel):
    """Request model for feedback endpoint"""

    request_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    rating: int = Field(..., ge=1, le=5, example=5)
    feedback_text: Optional[str] = Field(None, example="Great results!")

    @model_validator(mode="after")
    def validate_request_id(self) -> "FeedbackRequest":
        try:
            UUID(self.request_id)
        except ValueError:
            raise ValueError("request_id must be a valid UUID")
        return self


class FeedbackResponse(BaseModel):
    feedback_id: UUID
    request_id: UUID
    message: str
    feedback_timestamp: datetime
