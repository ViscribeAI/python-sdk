from viscribe import Client
from viscribe.logger import viscribe_logger

viscribe_logger.set_logging(level="INFO")

# Initialize the client
viscribe_client = Client(api_key="your-api-key-here")

# Example request_id (replace with an actual request_id from a previous request)
request_id = "your-request-id-here"

# Check remaining credits
credits = viscribe_client.get_credits()
print(f"Credits Info: {credits}")

# Submit feedback for a previous request
feedback_response = viscribe_client.submit_feedback(
    request_id=request_id,
    rating=5,  # Rating from 1-5
    feedback_text="Perfect image description!",
)
print(f"\nFeedback Response: {feedback_response}")

# Get previous results using get_describe_image
previous_result = viscribe_client.get_describe_image(request_id=request_id)
print(f"\nRetrieved Previous Result: {previous_result}")

viscribe_client.close()
