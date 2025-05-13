import asyncio
from viscribe.async_client import AsyncClient
from viscribe.logger import viscribe_logger

viscribe_logger.set_logging(level="INFO")

async def main():

    client = AsyncClient(api_key="vscrb-xxx")
    # 1. Describe Image
    describe_req = {
        "image_url": "https://img.com/cat.jpg"
    }
    describe_resp = await client.describe_image(describe_req)
    print("Describe Image:", describe_resp)

    # 2. Extract Structured Data
    extract_req = {
        "image_url": "https://img.com/prod.jpg",
        "output_schema": {"type": "object", "properties": {"product_name": {"type": "string"}}}
    }
    extract_resp = await client.extract_image(extract_req)
    print("Extract Image:", extract_resp)

    # 3. Classify Image
    classify_req = {
        "image_url": "https://img.com/cat.jpg",
        "classes": ["cat", "dog"]
    }
    classify_resp = await client.classify_image(classify_req)
    print("Classify Image:", classify_resp)

    # 4. Ask a Question
    ask_req = {
        "image_url": "https://img.com/car.jpg",
        "question": "What color is the car?"
    }
    ask_resp = await client.ask_image(ask_req)
    print("Ask Image:", ask_resp)

    # 5. Compare Images
    compare_req = {
        "image1_url": "https://img.com/cat1.jpg",
        "image2_url": "https://img.com/cat2.jpg"
    }
    compare_resp = await client.compare_images(compare_req)
    print("Compare Images:", compare_resp)
    

if __name__ == "__main__":
    asyncio.run(main()) 