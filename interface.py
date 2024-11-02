import ipywidgets as widgets
from IPython.display import display, clear_output
from eia_api import EIAAPI
from dotenv import load_dotenv
import os
import requests

# Load environment variables from api.env
load_dotenv("api.env")
EIA_API_KEY = os.getenv("EIA_API_KEY")

class EnergyCostOptimizationInterface:
    def __init__(self):
        self.output = widgets.Output()
        self.api = EIAAPI(api_key=EIA_API_KEY)

        # Main interface elements
        self.route_buttons_container = widgets.VBox()
        self.frequency_dropdown = widgets.Dropdown(description='Frequency:', options=[], disabled=True)
        self.state_dropdown = widgets.Dropdown(description='State:', options=[], disabled=True)
        self.sector_dropdown = widgets.Dropdown(description='Sector:', options=[], disabled=True)
        
        # Data selection checkboxes
        self.data_checkboxes = {
            "revenue": widgets.Checkbox(description="Revenue (million dollars)", value=False),
            "sales": widgets.Checkbox(description="Sales (million kWh)", value=False),
            "price": widgets.Checkbox(description="Price (cents/kWh)", value=False),
            "customers": widgets.Checkbox(description="Customers (number)", value=False)
        }

        # Fetch button
        self.fetch_data_button = widgets.Button(description="Fetch Data", button_style="info", disabled=True)
        self.fetch_data_button.on_click(self.fetch_data)

        # Load routes
        self.fetch_routes()
        self.display_interface()

    def display_interface(self):
        display(self.route_buttons_container, self.output)

    def fetch_routes(self):
        routes = self.api.fetch_routes()
        route_buttons = []
        for route in routes:
            button = widgets.Button(description=route["name"], layout=widgets.Layout(width='90%', margin='2px'), button_style="info")
            button.on_click(lambda b, r=route: self.on_route_selected(r))
            route_buttons.append(button)
        self.route_buttons_container.children = route_buttons

    def on_route_selected(self, route):
        with self.output:
            print(f"Selected route: {route['name']}")

        # Display data selection elements for `retail-sales` route below the main buttons
        if route["id"] == "retail-sales":
            self.setup_retail_sales_ui()

    def setup_retail_sales_ui(self):
        with self.output:
            clear_output(wait=True)
            print("Configuring Retail Sales Options...")

        # Configure frequency options
        self.frequency_dropdown.options = ["Monthly", "Quarterly", "Annual"]
        self.frequency_dropdown.value = "Monthly"
        self.frequency_dropdown.disabled = False

        # Populate state and sector dropdowns
        self.state_dropdown.options = self.api.fetch_state_options()
        self.sector_dropdown.options = self.api.fetch_sector_options()
        self.state_dropdown.disabled = False
        self.sector_dropdown.disabled = False

        # Enable data checkboxes and fetch button
        for checkbox in self.data_checkboxes.values():
            checkbox.disabled = False
        self.fetch_data_button.disabled = False

        # Display configuration UI below main buttons without clearing them
        display(self.frequency_dropdown, self.state_dropdown, self.sector_dropdown)
        display(*self.data_checkboxes.values())
        display(self.fetch_data_button)

    def fetch_data(self, b):
        # Collect the necessary parameters from UI components
        frequency = self.frequency_dropdown.value.lower()  # Convert frequency to lowercase to match the API parameter format
        state = self.state_dropdown.value
        sector = self.sector_dropdown.value
        data_fields = [key for key, checkbox in self.data_checkboxes.items() if checkbox.value]

        # Fetch and display the data
        try:
            # Print the full URL for debugging
            full_url = f"{self.api.base_url}retail-sales/data/"
            params = {
                "api_key": self.api.api_key,
                "frequency": frequency,
                "facets[stateid][]": state,
                "facets[sectorid][]": sector,
                "data[]": data_fields,
            }
            print(f"Full Data Fetch URL: {full_url}?{requests.compat.urlencode(params, doseq=True)}")

            data = self.api.fetch_data("retail-sales", frequency, state, sector, data_fields)
            with self.output:
                clear_output(wait=True)
                if not data.empty:
                    display(data)
                else:
                    print("No data returned.")
        except Exception as e:
            with self.output:
                print(f"Error fetching data for retail-sales: {e}")
