import asyncio

from viscribe.async_client import AsyncClient
from viscribe.logger import viscribe_logger
from pydantic import BaseModel

viscribe_logger.set_logging(level="INFO")


async def main():

    client = AsyncClient(api_key="vscrb-")
    
    # 1. Describe Image
    describe_resp = await client.describe_image(
        image_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE="
    )
    print("Describe Image:", describe_resp)

    # 2. Extract Structured Data - Using simple fields
    extract_resp = await client.extract_image(
        image_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
        fields=[
            {"name": "city_name", "type": "text", "description": "Name of the city in the image"},
            {"name": "water_bodies", "type": "array_text", "description": "List of water bodies visible"},
        ],
    )
    print("Extract Image:", extract_resp)
    
    # Alternative: Using advanced_schema for complex structures
 
    class Product(BaseModel):
        product_name: str
        price: float

    extract_resp = await client.extract_image(
        image_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
        advanced_schema=Product,
    )
    print("Extract Image (Advanced):", extract_resp)

    # 3. Classify Image
    classify_resp = await client.classify_image(
        image_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
        classes=["cat", "dog"]
    )
    print("Classify Image:", classify_resp)

    # 4. Ask a Question
    ask_resp = await client.ask_image(
        image_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
        question="What color is the car?",
    )
    print("Ask Image:", ask_resp)

    # 5. Compare Images
    compare_resp = await client.compare_images(
        image1_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
        image2_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
    )
    print("Compare Images:", compare_resp)

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
