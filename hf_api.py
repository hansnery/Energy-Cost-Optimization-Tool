import time
import requests

class HFAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        # Updated to LLaMA-2 endpoint
        self.base_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-11B-Vision-Instruct"

    def analyze_data(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"inputs": prompt}

        # Retry up to 3 times if the model is still loading
        for attempt in range(3):
            print(f"Attempt {attempt + 1} to send data to model...")
            print(f"Prompt being sent: {prompt[:500]}...")  # Show truncated prompt for debugging

            response = requests.post(self.base_url, headers=headers, json=data)
            print(f"HTTP Status Code: {response.status_code}")  # Print HTTP status code for debugging
            result = response.json()

            # Debug print of the response JSON
            print(f"Response JSON received: {result}")

            # Check if model is ready, otherwise wait and retry
            if "error" in result and "currently loading" in result["error"]:
                print("Model is loading, retrying in 20 seconds...")
                time.sleep(20)  # Wait for 20 seconds before retrying
            else:
                print("Model response successfully received.")
                return result  # Return the result if no error is found

        return {"error": "Model could not be loaded after multiple attempts"}
