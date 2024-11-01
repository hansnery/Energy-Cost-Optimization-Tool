import requests
import pandas as pd

class EIAAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.eia.gov/v2/electricity/retail-sales/data/"

    def fetch_data(self, start_date, end_date):
        params = {
            'api_key': self.api_key,
            'data[]': ['price', 'revenue', 'sales'],
            'frequency': 'monthly',
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc'
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()
        return pd.DataFrame(data["response"]["data"])
