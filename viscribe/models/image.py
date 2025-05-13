from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

# 1. Image Endpoints


class ImageDescribeRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    instruction: Optional[str] = None
    generate_tags: bool = True


class ImageDescribeResponse(BaseModel):
    request_id: str
    credits_used: int
    image_description: str
    tags: Optional[List[str]] = None


class ImageExtractRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    output_schema: Dict[str, Any]
    instruction: Optional[str] = None


class ImageExtractResponse(BaseModel):
    request_id: str
    credits_used: int
    extracted_data: Dict[str, Any]


class ImageClassifyRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    classes: Optional[List[str]] = None
    class_descriptions: Optional[Dict[str, str]] = None
    instruction: Optional[str] = None
    multi_label: bool = False


class ImageClassifyResponse(BaseModel):
    request_id: str
    credits_used: int
    classification: List[str]


class ImageAskRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
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


class FeedbackCreate(BaseModel):
    request_id: UUID
    rating: int = Field(..., ge=0, le=5)
    feedback_text: Optional[str] = None


class FeedbackResponse(BaseModel):
    feedback_id: UUID
    request_id: UUID
    message: str
    feedback_timestamp: datetime
