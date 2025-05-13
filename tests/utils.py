from uuid import uuid4


def generate_mock_api_key():
    """Generate a valid mock API key in the format 'vscrb-{uuid}'"""
    return f"vscrb-{uuid4()}"
