import requests
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile

def generate_image_from_text(carpool_name):
    """
    Generates an image from text using the Hugging Face API and returns the binary data.
    """
    try:
        # API Endpoint and Authorization
        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large-turbo"
        headers = {
            "Authorization": f"Bearer {settings.HUGGING_FACE_API_KEY}"
        }
        data = {
            "inputs": carpool_name,  # The carpool name as the prompt
        }

        # Send the API request
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # Parse the API response to get the image URL or binary data
            response_data = response.json()
            image_url = response_data[0].get("generated_image")  # Ensure this matches your API's response format

            # Fetch the image content
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                print(f"Image successfully generated for: {carpool_name}")
                return image_response.content
            else:
                print(f"Failed to fetch the image content for: {carpool_name}. "
                      f"Image URL response status: {image_response.status_code}")
        else:
            print(f"Image generation failed for: {carpool_name}. "
                  f"API response status: {response.status_code}, Message: {response.text}")

    except Exception as e:
        print(f"An error occurred while generating the image for {carpool_name}: {str(e)}")

    # Return None if the operation failed
    return None
