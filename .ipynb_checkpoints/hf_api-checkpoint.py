import time
import requests

class HFAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat"

    def analyze_data(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"inputs": prompt}

        # Retry up to 3 times if the model is still loading
        for attempt in range(3):
            response = requests.post(self.base_url, headers=headers, json=data)
            result = response.json()

            # Check if model is ready, otherwise wait and retry
            if "error" in result and "currently loading" in result["error"]:
                print("Model is loading, retrying in 20 seconds...")
                time.sleep(20)  # Wait for 20 seconds before retrying
            else:
                return result  # Return the result if no error is found

        return {"error": "Model could not be loaded after multiple attempts"}
