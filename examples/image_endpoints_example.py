from viscribe.client import Client
from viscribe.logger import viscribe_logger

viscribe_logger.set_logging(level="INFO")

def main():
    client = Client(api_key="vscrb-415ffd78-187f-4ed3-b295-c02c43a6f79f")

    # 1. Describe Image
    describe_resp = client.describe_image(
        image_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
        generate_tags=False
    )
    print("Describe Image:", describe_resp)

    # 2. Extract Structured Data
    # extract_resp = client.extract_image(
    #     image_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
    #     output_schema={"type": "object", "properties": {"product_name": {"type": "string"}}}
    # )
    # print("Extract Image:", extract_resp)

    # 3. Classify Image
    classify_resp = client.classify_image(
        image_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
        classes=["cat", "dog"]
    )
    print("Classify Image:", classify_resp)

    # 4. Ask a Question
    ask_resp = client.ask_image(
        image_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
        question="What is the name of the city in the image?"
    )
    print("Ask Image:", ask_resp)

    # 5. Compare Images
    compare_resp = client.compare_images(
        image1_url="https://media.istockphoto.com/id/1388018793/photo/grand-canal-in-venice.jpg?s=612x612&w=0&k=20&c=uDUrctquPNUPzlpNLwTkJIkc1Gig0aUWJknF6FrqxJE=",
        image2_url="https://upload.wikimedia.org/wikipedia/commons/2/27/Chioggia2.jpg"
    )
    print("Compare Images:", compare_resp)

if __name__ == "__main__":
    main() 