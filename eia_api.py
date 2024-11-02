import requests
import pandas as pd

class EIAAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.eia.gov/v2/electricity/"
    
    def fetch_routes(self):
        """Fetches metadata about available routes under the electricity API."""
        url = f"{self.base_url}"
        params = {
            'api_key': self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract and print route metadata for inspection
            routes = data.get("response", {}).get("routes", [])
            for route in routes:
                print(f"ID: {route['id']}, Name: {route['name']}, Description: {route['description']}")

            # Return the route metadata
            return routes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching routes from EIA API: {e}")
            return []

    def fetch_data(self, route_id, start_date, end_date):
        """Fetches data for a specific route using start and end dates."""
        url = f"{self.base_url}{route_id}/data/"
        params = {
            'api_key': self.api_key,
            'data[]': ['price', 'revenue', 'sales'],
            'frequency': 'monthly',
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Print the full API response data to inspect its structure
            print("Full Retrieved Data:", data)

            # Convert to DataFrame if data is in expected format
            if "response" in data and "data" in data["response"]:
                df = pd.DataFrame(data["response"]["data"])
                print("Converted DataFrame:", df.head())  # Print the first few rows of the DataFrame
                return df
            else:
                print("Unexpected data structure in API response.")
                return pd.DataFrame()
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from EIA API for route '{route_id}': {e}")
            return pd.DataFrame()
