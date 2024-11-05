#chat_gpt_api.py

import time
import os
import requests

class ChatGPTAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def analyze_data(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare data in ChatGPT's required format
        data = {
            "model": "gpt-4",  # or "gpt-3.5-turbo" depending on your preference and access
            "messages": [
                {"role": "system", "content": "You are an AI that helps analyze datasets for cost optimization."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        # Retry up to 3 times if the request fails
        for attempt in range(3):
            # Commented out debugging prints to make output clearer
            # print(f"Attempt {attempt + 1} to send data to ChatGPT model...")
            # print(f"Prompt being sent: {prompt[:500]}...")  # Show truncated prompt for debugging

            response = requests.post(self.base_url, headers=headers, json=data)
            
            # Commented out debugging prints
            # print(f"HTTP Status Code: {response.status_code}")  # Print HTTP status code for debugging
            result = response.json()

            # Commented out response JSON debugging print
            # print(f"Response JSON received: {result}")

            # Check for error or if response is ready
            if "error" in result:
                error_message = result["error"].get("message", "Unknown error")
                
                # Commented out error handling debug prints
                # print(f"Error: {error_message}")
                
                if "Rate limit" in error_message or response.status_code == 429:
                    # Commented out rate limit hit debug print
                    # print("Rate limit hit, retrying in 20 seconds...")
                    time.sleep(20)
                else:
                    return {"error": error_message}
            else:
                # Commented out success debug print
                # print("Model response successfully received.")
                
                # Extract the generated response from ChatGPT
                response_text = result['choices'][0]['message']['content']
                return {"generated_text": response_text}

        return {"error": "Model could not be loaded after multiple attempts"}
