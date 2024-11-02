# interface.py
import ipywidgets as widgets
from IPython.display import display, clear_output
from eia_api import EIAAPI
import os
from dotenv import load_dotenv

# Toggle development mode here
DEVELOPMENT = True  # Set to False for production

# Load environment variables from api.env if DEVELOPMENT is True
if DEVELOPMENT:
    load_dotenv("api.env")
    EIA_API_KEY = os.getenv("EIA_API_KEY")
else:
    EIA_API_KEY = None

# Interface class to encapsulate UI elements and logic
class EnergyCostOptimizationInterface:
    def __init__(self):
        # Output widget for displaying messages and data
        self.output = widgets.Output()

        # Check if we are in development mode to use hardcoded API keys
        if DEVELOPMENT and EIA_API_KEY:
            self.eia_api_key = EIA_API_KEY
            self.show_api_input = False
            with self.output:
                print("Development mode: Using hardcoded API key.")
        else:
            self.eia_api_key_input = widgets.Text(
                placeholder='Enter EIA API Key', description='EIA API Key:'
            )
            self.show_api_input = True
            with self.output:
                print("Production mode: Displaying API key input field.")

        # Initialize API instance and fetch routes
        self.eia_api = EIAAPI(api_key=self.eia_api_key if DEVELOPMENT else "")
        self.routes = self.eia_api.fetch_routes()

        # Create buttons for each route
        self.route_buttons = {}
        for route in self.routes:
            button = widgets.Button(description=route["name"], button_style="info")
            button.on_click(lambda b, route=route: self.display_route_info(route))
            self.route_buttons[route["id"]] = button

        # Date range selection dropdowns
        self.date_range = widgets.Dropdown(
            options=['Last Month', 'Last Quarter', 'Last Year'],
            value='Last Month',
            description='Date Range:'
        )

        # Button to fetch data based on selected route
        self.fetch_data_button = widgets.Button(
            description="Fetch Route Data", button_style='success'
        )
        self.fetch_data_button.on_click(self.fetch_data)

        # Display the UI when initialized
        self.display_interface()

    def display_interface(self):
        # Display input field for API key if needed
        if self.show_api_input:
            display(self.eia_api_key_input)
        
        # Display route buttons
        for button in self.route_buttons.values():
            display(button)

        # Display date range selector and fetch data button
        display(self.date_range, self.fetch_data_button)
        
        # Output area for route metadata and data preview
        display(self.output)

    def display_route_info(self, route):
        # Display route metadata in the output area
        with self.output:
            clear_output(wait=True)
            print(f"ID: {route['id']}")
            print(f"Name: {route['name']}")
            print(f"Description: {route['description']}")

        # Save selected route ID for later data fetching
        self.selected_route_id = route["id"]

    def fetch_data(self, b):
        # Ensure an API key is available
        eia_api_key = self.eia_api_key if DEVELOPMENT else self.eia_api_key_input.value
        if not eia_api_key:
            with self.output:
                clear_output(wait=True)
                print("Please enter a valid EIA API Key.")
            return

        # Set up date range based on selected option
        date_ranges = {
            'Last Month': ('2023-09-01', '2023-09-30'),
            'Last Quarter': ('2023-07-01', '2023-09-30'),
            'Last Year': ('2023-01-01', '2023-12-31')
        }
        start_date, end_date = date_ranges[self.date_range.value]

        # Fetch data for the selected route
        if hasattr(self, 'selected_route_id'):
            try:
                df = self.eia_api.fetch_data(self.selected_route_id, start_date, end_date)
                with self.output:
                    clear_output(wait=True)
                    print(f"Data for route: {self.selected_route_id}")
                    display(df.head())  # Display a preview of the fetched data
            except Exception as e:
                with self.output:
                    print(f"Error fetching data for route '{self.selected_route_id}': {e}")
        else:
            with self.output:
                print("Please select a route to fetch data.")
