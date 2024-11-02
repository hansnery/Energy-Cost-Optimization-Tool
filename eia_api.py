import requests
import pandas as pd

class EIAAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.eia.gov/v2/electricity/"

    def fetch_routes(self):
        url = f"{self.base_url}?api_key={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data["response"]["routes"]
        except requests.RequestException as e:
            print(f"Error fetching routes: {e}")
            return []

    def fetch_data(self, route_id, frequency, state, sector, data_fields):
        # Construct the URL and parameters in the correct format
        url = f"{self.base_url}{route_id}/data/"
        
        params = {
            "api_key": self.api_key,
            "frequency": frequency,
            "facets[stateid][]": state,
            "facets[sectorid][]": sector
        }
        
        # Correctly add each data field as a separate entry in `params`
        for i, field in enumerate(data_fields):
            params[f"data[{i}]"] = field  # Creates multiple `data[]` entries

        try:
            # Construct the full URL for debugging
            full_url = requests.Request('GET', url, params=params).prepare().url
            print("Full Data Fetch URL:", full_url)

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if "response" in data and "data" in data["response"]:
                return pd.DataFrame(data["response"]["data"])
            else:
                print("Unexpected data structure in API response.")
                return pd.DataFrame()
        except requests.RequestException as e:
            print(f"Error fetching data for {route_id}: {e}")
            return pd.DataFrame()

    def fetch_state_options(self):
        url = f"{self.base_url}retail-sales/facet/stateid"
        params = {"api_key": self.api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            states = [(item["name"], item["id"]) for item in data["response"]["facets"]]
            return states
        except requests.RequestException as e:
            print(f"Error fetching state options: {e}")
            return []

    def fetch_sector_options(self):
        url = f"{self.base_url}retail-sales/facet/sectorid"
        params = {"api_key": self.api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            sectors = [(item["name"], item["id"]) for item in data["response"]["facets"]]
            return sectors
        except requests.RequestException as e:
            print(f"Error fetching sector options: {e}")
            return []
