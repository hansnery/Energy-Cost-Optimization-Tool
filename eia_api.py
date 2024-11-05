# eia_api.py

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logs

# Suppress debug messages from urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)

class EIAAPI:
    def __init__(self, api_key):
        """
        Initializes the EIAAPI instance with the provided API key.

        Args:
            api_key (str): Your EIA API key.
        """
        self.api_key = api_key
        self.base_url = "https://api.eia.gov/v2/electricity/"

    def fetch_routes(self):
        """
        Fetches the list of available routes from the EIA API.

        Returns:
            list: A list of routes where each route is a dictionary with route details.
        """
        url = f"{self.base_url}?api_key={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            # Commented out to clear the screen
            # logging.info("Successfully fetched routes from the EIA API.")
            return data["response"]["routes"]
        except requests.RequestException as e:
            # Commented out to clear the screen
            # logging.error(f"Error fetching routes: {e}")
            return []

    def fetch_route_details(self, route_id):
        """
        Fetches the details of a specific route.

        Args:
            route_id (str): The ID of the route to fetch details for.

        Returns:
            dict or None: The route details if successful, None otherwise.
        """
        url = f"{self.base_url}{route_id}/"
        params = {"api_key": self.api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            # Commented out to clear the screen
            # logging.info(f"Successfully fetched details for route '{route_id}'.")
            return data["response"]
        except requests.RequestException as e:
            # Commented out to clear the screen
            # logging.error(f"Error fetching route details for '{route_id}': {e}")
            return None

    def fetch_facet_options(self, route_id, facet_id):
        """
        Fetches the available options for a specific facet of a route.

        Args:
            route_id (str): The ID of the route.
            facet_id (str): The ID of the facet.

        Returns:
            list: A list of tuples containing (option_name, option_id).
        """
        url = f"{self.base_url}{route_id}/facet/{facet_id}"
        params = {"api_key": self.api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Commented out debug logging
            # logging.debug(f"API response for facet '{facet_id}': {data}")

            # Access the facet values
            if "response" in data and "facets" in data["response"]:
                values = data["response"]["facets"]
            else:
                # Commented out error logging
                # logging.error(f"Facet '{facet_id}' not found in response.")
                return []

            # Construct options as (option_name, option_id)
            options = [(f"{item['name']} ({item['id']})", item["id"]) for item in values]

            # Commented out success logging
            # logging.info(f"Successfully fetched facet options for '{facet_id}' in route '{route_id}'.")
            return options
        except requests.RequestException as e:
            # Commented out error logging
            # logging.error(f"Error fetching facet options for '{facet_id}' in route '{route_id}': {e}")
            return []
        except KeyError as e:
            # Commented out error logging
            # logging.error(f"Key error when fetching facet options for '{facet_id}': {e}")
            return []

    def fetch_data_fields(self, route_id):
        """
        Fetches the available data fields for a specific route.

        Args:
            route_id (str): The ID of the route.

        Returns:
            list: A list of tuples containing (field_alias, field_id).
        """
        route_details = self.fetch_route_details(route_id)
        if route_details and "data" in route_details:
            data_fields = route_details["data"]
            # Commented out success logging
            # logging.info(f"Successfully fetched data fields for route '{route_id}'.")
            return [(v["alias"], k) for k, v in data_fields.items()]
        else:
            # Commented out warning logging
            # logging.warning(f"No data fields found for route '{route_id}'.")
            return []

    def fetch_data(self, route_id, frequency, facets, data_fields, start_date=None, end_date=None, max_rows=None):
        """
        Fetches data from the EIA API based on the specified parameters.

        Args:
            route_id (str): The ID of the route.
            frequency (str): The frequency of the data (e.g., 'monthly').
            facets (dict): A dictionary of facet IDs to their selected values (list or single value).
            data_fields (list): A list of data field IDs to include in the response.
            start_date (str): The start date in 'YYYY-MM' format.
            end_date (str): The end date in 'YYYY-MM' format.
            max_rows (int, optional): The maximum number of rows to return. Defaults to None.

        Returns:
            pandas.DataFrame: A DataFrame containing the fetched data.
        """
        url = f"{self.base_url}{route_id}/data/"

        params = {
            "api_key": self.api_key,
            "frequency": frequency,
            "offset": 0  # Start at the beginning
        }

        # Add facets to params
        for facet_id, values in facets.items():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                params.setdefault(f"facets[{facet_id}][]", []).append(value)

        # Add data fields
        for i, field in enumerate(data_fields):
            params[f"data[{i}]"] = field

        # Adjust start and end dates according to EIA API requirements
        if start_date:
            # For monthly data, the start date should be one day before the desired first month
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m')
                adjusted_start_dt = start_dt - timedelta(days=1)
                adjusted_start_date = adjusted_start_dt.strftime('%Y-%m-%d')
                params["start"] = adjusted_start_date
            except ValueError:
                # Commented out error logging
                # logging.error("Invalid start_date format. Expected 'YYYY-MM'.")
                return pd.DataFrame()
        if end_date:
            # For monthly data, the end date should be the first day of the desired last month
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m')
                adjusted_end_date = end_dt.strftime('%Y-%m-%d')
                params["end"] = adjusted_end_date
            except ValueError:
                # Commented out error logging
                # logging.error("Invalid end_date format. Expected 'YYYY-MM'.")
                return pd.DataFrame()

        # Add max_rows to limit the number of results
        if max_rows is not None:
            params['length'] = max_rows

        try:
            # Commented out full URL debug log
            # full_url = requests.Request('GET', url, params=params).prepare().url
            # logging.debug(f"Full Data Fetch URL: {full_url}")

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if "response" in data and "data" in data["response"]:
                # Commented out success logging
                # logging.info(f"Successfully fetched data for route '{route_id}'.")
                return pd.DataFrame(data["response"]["data"])
            else:
                # Commented out warning logging
                # logging.warning(f"Unexpected data structure in API response for route '{route_id}'.")
                return pd.DataFrame()
        except requests.RequestException as e:
            # Commented out error logging
            # logging.error(f"Error fetching data for route '{route_id}': {e}")
            return pd.DataFrame()
