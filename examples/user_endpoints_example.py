from viscribe import Client
from viscribe.logger import viscribe_logger

viscribe_logger.set_logging(level="INFO")

# Initialize the client
viscribe_client = Client(api_key="vscrb-")

# Example request_id (replace with an actual request_id from a previous request)
request_id = "95ad5697-b911-46e3-bf5d-e796bf0b3a44"

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

