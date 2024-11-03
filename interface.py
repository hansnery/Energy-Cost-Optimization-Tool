import ipywidgets as widgets
from IPython.display import display, clear_output
from eia_api import EIAAPI
from hf_api import HFAPI
from dotenv import load_dotenv
from ipywidgets import Textarea
import os

# Load environment variables from api.env
load_dotenv("api.env")
EIA_API_KEY = os.getenv("EIA_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

class EnergyCostOptimizationInterface:
    def __init__(self):
        # Initialize API and output widgets
        self.output = widgets.Output()
        self.url_output = widgets.Output()  # Separate output for URL
        self.api = EIAAPI(api_key=EIA_API_KEY)
        self.hf_api = HFAPI(api_key=HF_API_KEY)
        self.data = None  # Initialize data attribute to store fetched data

        # Main route buttons
        self.route_buttons_container = widgets.VBox()
        
        # UI elements for route-specific options
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

        # Buttons for fetching data and running analysis
        self.fetch_data_button = widgets.Button(description="Fetch Data", button_style="info", disabled=True)
        self.run_analysis_button = widgets.Button(description="Run Analysis", button_style="success", disabled=True)
        
        # Bind button actions
        self.fetch_data_button.on_click(self.fetch_data)
        self.run_analysis_button.on_click(self.run_analysis)

        # Load routes and display interface
        self.fetch_routes()
        self.display_interface()

    def display_interface(self):
        # Display main UI components and URL output below
        display(self.route_buttons_container, self.output)
        display(self.url_output)  # Ensure this displays as a separate cell

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
            clear_output(wait=True)
            print(f"Selected route: {route['name']}")

        # Setup UI options for retail-sales route
        if route["id"] == "retail-sales":
            self.setup_retail_sales_ui()

    def setup_retail_sales_ui(self):
        # Configure dropdowns and checkboxes for retail-sales route
        self.frequency_dropdown.options = ["Monthly", "Quarterly", "Annual"]
        self.frequency_dropdown.value = "Monthly"
        self.frequency_dropdown.disabled = False

        # Populate state and sector dropdowns
        self.state_dropdown.options = self.api.fetch_state_options()
        self.sector_dropdown.options = self.api.fetch_sector_options()
        self.state_dropdown.disabled = False
        self.sector_dropdown.disabled = False

        # Enable checkboxes and fetch data button
        for checkbox in self.data_checkboxes.values():
            checkbox.disabled = False
        self.fetch_data_button.disabled = False
        self.run_analysis_button.disabled = True  # Disable analysis button until data is fetched

        # Display configuration UI below main buttons without clearing them
        with self.output:
            clear_output(wait=True)
            display(self.frequency_dropdown, self.state_dropdown, self.sector_dropdown)
            display(*self.data_checkboxes.values())
            display(self.fetch_data_button)  # Display Fetch Data button
            display(self.run_analysis_button)  # Display Run Analysis button separately

    def fetch_data(self, b):
        # Gather parameters from UI
        frequency = self.frequency_dropdown.value.lower()
        state = self.state_dropdown.value
        sector = self.sector_dropdown.value
        data_fields = [k for k, v in self.data_checkboxes.items() if v.value]

        if not data_fields:
            with self.output:
                clear_output(wait=True)
                print("Please select at least one data field.")
            return

        # API call to fetch data
        try:
            # Fetch the full dataset
            full_data = self.api.fetch_data("retail-sales", frequency, state, sector, data_fields)
            
            # Check if the dataset is not empty
            if not full_data.empty:
                # Sort data by 'period' column in descending order
                sorted_data = full_data.sort_values(by="period", ascending=False)
                
                # Define columns to keep based on available columns and selected data fields
                mandatory_columns = ["period", "stateid", "stateDescription", "sectorid"]
                selected_columns = mandatory_columns + [col for col in data_fields if col in sorted_data.columns]
                
                # Select the latest 5 rows with the chosen columns
                self.data = sorted_data.head(5)[selected_columns]
                
                # Display the limited dataset in the output
                with self.output:
                    clear_output(wait=True)
                    display(self.data)
                    
                    # Enable and display the Run Analysis button after data is fetched
                    self.run_analysis_button.disabled = False
                    display(self.run_analysis_button)
                    
            else:
                with self.output:
                    clear_output(wait=True)
                    print("No data returned.")
                    
        except Exception as e:
            with self.output:
                print(f"Error fetching data for retail-sales: {e}")


    def display_analysis_result(self, result_text):
        # Displaying the AI result in a TextArea for proper wrapping
        text_area = Textarea(
            value=result_text,
            disabled=True,
            layout=widgets.Layout(width='100%', height='300px')
        )
        display(text_area)

    def run_analysis(self, b):
        with self.output:
            clear_output(wait=True)
            print("Starting analysis. This may take a few moments...")

        # Simple prompt for testing
        # prompt = "Analyze the following limited dataset to suggest ways for cost optimization in energy usage:\n" + self.data.to_string()
        prompt = self.data.to_string()

        # Fetch AI analysis result from HFAPI
        result = self.hf_api.analyze_data(prompt)

        with self.output:
            clear_output(wait=True)

            if 'error' in result:
                print(f"Error during analysis: {result['error']}")
            else:
                # Check if the result contains generated_text and extract it
                if isinstance(result, list) and len(result) > 0:
                    analysis_text = result[0].get('generated_text', "No text generated.")
                else:
                    analysis_text = result.get('generated_text', "No text generated.")

                # Display the analysis result with text wrapping for readability
                self.display_analysis_result(analysis_text)

