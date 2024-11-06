# interface.py

import ipywidgets as widgets
from IPython.display import display, clear_output
import os
import requests
import pandas as pd
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)

# Suppress debug messages from urllib3, Jupyter, traitlets, and Comm
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("traitlets").setLevel(logging.WARNING)
logging.getLogger("ipykernel.comm").setLevel(logging.WARNING)
logging.getLogger("Comm").setLevel(logging.WARNING)

# Load environment variables from api.env
load_dotenv("api.env")

class EnergyCostOptimizationInterface:
    def __init__(self):
        # Initialize output widgets
        self.output = widgets.Output()
        self.url_output = widgets.Output()

        # Store API keys from the environment if available
        self.eia_api_key = os.getenv("EIA_API_KEY")
        self.chat_gpt_api_key = os.getenv("CHAT_GPT_API_KEY")

        # Initialize placeholders for API and data
        self.api = None
        self.chat_gpt_api = None
        self.data = None

        # Main route buttons
        self.route_buttons_header = widgets.HTML("<h3>Select a Data Route:</h3>")
        self.route_buttons_container = widgets.VBox()

        # UI elements for route-specific options
        self.frequency_dropdown = widgets.Dropdown(description='Frequency:', options=[], disabled=True)
        self.facet_dropdowns = {}  # Dynamic facets
        self.data_field_checkboxes = {}  # Dynamic data fields

        # Date range widgets
        self.start_date_dropdown = None
        self.end_date_dropdown = None

        # Buttons for fetching data and running analysis
        self.fetch_data_button = widgets.Button(description="Fetch Data", button_style="info", disabled=True)
        self.run_analysis_button = widgets.Button(description="Run Analysis", button_style="success", disabled=True)

        # Bind button actions
        self.fetch_data_button.on_click(self.fetch_data)
        self.run_analysis_button.on_click(self.run_analysis)

        # Determine whether to display the form or proceed with API initialization
        if self.eia_api_key and self.chat_gpt_api_key:
            # Initialize APIs if keys are present
            self.initialize_apis()
            self.fetch_routes()
            self.display_interface()
        else:
            # Display form for API key inputs
            self.display_api_key_form()

    def display_api_key_form(self):
        # Create input fields for EIA and ChatGPT API keys
        eia_api_key_input = widgets.Text(description='EIA API Key:', placeholder='Enter your EIA API Key')
        chat_gpt_api_key_input = widgets.Text(description='ChatGPT API Key:', placeholder='Enter your ChatGPT API Key')
        submit_button = widgets.Button(description='Submit', button_style='primary')

        # Display the input form
        form = widgets.VBox([eia_api_key_input, chat_gpt_api_key_input, submit_button])
        display(form)

        # Define submit button action
        def on_submit(b):
            self.eia_api_key = eia_api_key_input.value
            self.chat_gpt_api_key = chat_gpt_api_key_input.value

            # Check if both API keys are provided
            if not self.eia_api_key or not self.chat_gpt_api_key:
                with self.output:
                    clear_output(wait=True)
                    print("Please provide both API keys.")
            else:
                # Initialize APIs
                self.initialize_apis()
                # Clear form and proceed
                with self.output:
                    clear_output(wait=True)
                form.close()
                self.fetch_routes()
                self.display_interface()

        submit_button.on_click(on_submit)

    def initialize_apis(self):
        # Import the API classes
        from eia_api import EIAAPI
        from chat_gpt_api import ChatGPTAPI
        
        # Initialize the APIs with the provided keys
        self.api = EIAAPI(api_key=self.eia_api_key)
        self.chat_gpt_api = ChatGPTAPI(api_key=self.chat_gpt_api_key)

    def display_interface(self):
        # Display main UI components and URL output below
        clear_output(wait=True)  # Clear previous outputs to avoid duplicates
        display(self.route_buttons_header, self.route_buttons_container, self.output)
        display(self.url_output)  # Ensure this displays as a separate cell

    def fetch_routes(self):
        routes = self.api.fetch_routes()

        # Only use the first two routes to create buttons
        routes = routes[:2]

        route_buttons = []
        max_button_width = '350px'  # Set a fixed width that looks consistent

        for route in routes:
            button = widgets.Button(
                description=route["name"],
                layout=widgets.Layout(
                    width=max_button_width,  # Set the width explicitly to ensure uniformity
                    max_width=max_button_width,
                    min_width=max_button_width,
                    margin='10px auto'  # Add some space for the visual appeal and center alignment
                ),
                button_style="info"
            )
            button.on_click(lambda b, r=route: self.on_route_selected(r))
            route_buttons.append(button)

        # Set the buttons in a VBox for a vertically aligned group with centered buttons
        self.route_buttons_container.children = route_buttons
        self.route_buttons_container.layout = widgets.Layout(justify_content='center', align_items='center')

    def on_route_selected(self, route):
        with self.output:
            clear_output(wait=True)
            print(f"Loading selected route: {route['name']}\n\nPlease wait...")

        self.selected_route = route  # Store selected route

        # Setup UI options based on the selected route
        self.setup_route_ui(route)

    def setup_route_ui(self, route):
        # Unobserve frequency dropdown to prevent triggering on reset
        try:
            self.frequency_dropdown.unobserve(self.on_frequency_change, names='value')
        except ValueError:
            pass  # The handler was not registered, so we can ignore this error

        # Reset UI elements
        self.frequency_dropdown.options = []
        self.frequency_dropdown.value = None  # Explicitly set value to None
        self.frequency_dropdown.disabled = True
        self.facet_dropdowns = {}
        self.data_field_checkboxes = {}

        # Fetch route details
        route_details = self.api.fetch_route_details(route["id"])

        if not route_details:
            with self.output:
                clear_output(wait=True)
                print("Failed to fetch route details.")
            return

        # Configure frequency options
        frequencies = [freq["id"].capitalize() for freq in route_details.get("frequency", [])]
        if frequencies:
            self.frequency_dropdown.options = frequencies
            default_frequency = route_details.get("defaultFrequency", frequencies[0]).capitalize()
            self.frequency_dropdown.value = default_frequency
            self.frequency_dropdown.disabled = False

        # Re-observe changes to frequency dropdown
        self.frequency_dropdown.observe(self.on_frequency_change, names='value')

        # Configure facet dropdowns
        facets = route_details.get("facets", [])
        for facet in facets:
            options = self.api.fetch_facet_options(route["id"], facet["id"])
            if options:
                dropdown = widgets.Dropdown(description=f'{facet["description"]}:', options=options, disabled=False)

                # Set "all sectors (ALL)" as the default for the Sector dropdown
                if facet["id"] == "sectorid":
                    # Set the default to "ALL" if available
                    for option in options:
                        if option[1] == "ALL":  # Accessing the id part of the tuple
                            dropdown.value = option[1]  # Set the dropdown to use the value ID part of the tuple
                            break

                self.facet_dropdowns[facet["id"]] = dropdown

        # Configure data fields
        data_fields = self.api.fetch_data_fields(route["id"])
        if data_fields:
            # Adjust width of checkboxes for readability
            self.data_field_checkboxes = {
                field_id: widgets.Checkbox(
                    description=alias, value=False,
                    layout=widgets.Layout(width='90%')  # Wider layout for readability
                )
                for alias, field_id in data_fields
            }

        # Initial setup of date range
        self.update_date_range(route)

        # Enable fetch data button
        self.fetch_data_button.disabled = False
        self.run_analysis_button.disabled = True  # Disable until data is fetched

        # Clear previous output and display the UI elements individually
        with self.output:
            clear_output(wait=True)
            
            # Display frequency dropdown
            display(self.frequency_dropdown)
            
            # Display all facet dropdowns
            for dropdown in self.facet_dropdowns.values():
                display(dropdown)
            
            # Display start and end date dropdowns if they exist
            if self.start_date_dropdown and self.end_date_dropdown:
                display(self.start_date_dropdown)
                display(self.end_date_dropdown)
            
            # Display all data field checkboxes
            for checkbox in self.data_field_checkboxes.values():
                display(checkbox)
            
            # Display the buttons for fetching data and running analysis
            display(self.fetch_data_button)
            display(self.run_analysis_button)

    def on_frequency_change(self, change):
        # Update date range when frequency changes
        self.update_date_range(self.selected_route)

    def update_date_range(self, route):
        # Collect selected facets
        facets = {}
        for facet_id, dropdown in self.facet_dropdowns.items():
            selected_value = dropdown.value
            facets[facet_id] = selected_value

        frequency = self.frequency_dropdown.value
        if frequency is None:
            # Commented out to clear the screen
            # logging.warning("Frequency is None. Skipping update_date_range.")
            return

        available_periods = self.fetch_available_periods(route["id"], frequency, facets)

        if available_periods:
            default_end_date = available_periods[-1]
            default_start_date = available_periods[-12] if len(available_periods) >= 12 else available_periods[0]

            if not self.start_date_dropdown:
                self.start_date_dropdown = widgets.Dropdown(description='Start Date:', options=available_periods)
            else:
                self.start_date_dropdown.options = available_periods
            self.start_date_dropdown.value = default_start_date

            if not self.end_date_dropdown:
                self.end_date_dropdown = widgets.Dropdown(description='End Date:', options=available_periods)
            else:
                self.end_date_dropdown.options = available_periods
            self.end_date_dropdown.value = default_end_date
        else:
            self.start_date_dropdown = None
            self.end_date_dropdown = None

    def fetch_available_periods(self, route_id, frequency, facets):
        url = f"{self.api.base_url}{route_id}/data/"
        params = {
            "api_key": self.api.api_key,
            "frequency": frequency.lower(),
            "offset": 0,
            "length": 1  # Initial request to get total number of records
        }

        # Add facets to params
        for facet_id, value in facets.items():
            params[f"facets[{facet_id}][]"] = value

        # Add a minimal data field to get data back (choose an appropriate data field if necessary)
        params["data[]"] = "price"

        try:
            # Commented out debug logging to clear the screen
            # full_url = requests.Request('GET', url, params=params).prepare().url
            # logging.debug(f"Full URL for fetching available periods: {full_url}")

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "response" in data and "total" in data["response"]:
                total_records = data["response"]["total"]
                # Commented out debug logging
                # logging.debug(f"Total records available: {total_records}")
            else:
                # Commented out error logging
                # logging.error("Unexpected data structure in API response.")
                return []

            # Now fetch all periods using the total_records as length
            params["length"] = total_records
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "response" in data and "data" in data["response"]:
                periods = [item["period"] for item in data["response"]["data"]]
                unique_periods = sorted(set(periods))
                return unique_periods
            else:
                # Commented out error logging
                # logging.error("Unexpected data structure in API response.")
                return []
        except requests.RequestException as e:
            # Commented out error logging
            # logging.error(f"Error fetching periods for {route_id}: {e}")
            return []

    def fetch_data(self, b):
        # Gather parameters from UI
        frequency = self.frequency_dropdown.value.lower()

        # Collect selected facets
        facets = {}
        for facet_id, dropdown in self.facet_dropdowns.items():
            selected_value = dropdown.value
            facets[facet_id] = selected_value

        # Collect selected data fields
        data_fields = [field_id for field_id, checkbox in self.data_field_checkboxes.items() if checkbox.value]

        if not data_fields:
            with self.output:
                clear_output(wait=True)
                print("Please select at least one data field.")
            return

        # Collect start and end dates
        start_date = self.start_date_dropdown.value if self.start_date_dropdown else None
        end_date = self.end_date_dropdown.value if self.end_date_dropdown else None

        if start_date and end_date:
            if start_date > end_date:
                with self.output:
                    clear_output(wait=True)
                    print("Start Date must be earlier than End Date.")
                return

        # API call to fetch data with max_rows=10
        try:
            full_data = self.api.fetch_data(
                self.selected_route["id"],
                frequency,
                facets,
                data_fields,
                start_date=start_date,
                end_date=end_date,
                max_rows=10  # Limit to 10 rows
            )

            if not full_data.empty:
                sorted_data = full_data.sort_values(by="period", ascending=False)
                self.data = sorted_data
                with self.output:
                    clear_output(wait=True)
                    print("Data fetched (limited to a maximum of 10 rows):")
                    display(self.data)

                    # Add margin to the top of "Run Analysis" button
                    self.run_analysis_button.layout = widgets.Layout(
                        margin='20px 0 0 0'  # Add 20px margin to the top
                    )
                    
                    self.run_analysis_button.disabled = False
                    display(self.run_analysis_button)
            else:
                with self.output:
                    clear_output(wait=True)
                    print("No data returned.")

        except Exception as e:
            with self.output:
                print(f"Error fetching data for {self.selected_route['id']}: {e}")

    def display_analysis_result(self, result_text):
        # Adding a title above the analysis text
        title_html = widgets.HTML(
            value="<h4 style='text-align: center;'>AI Analysis Result:</h4>",  # Added inline CSS to center the title text
            layout=widgets.Layout(
                margin='0 0 10px 0',  # Add margin to separate the title from the text area
            )
        )

        # Adding custom styles using HTML and CSS for better control
        text_area_html = widgets.HTML(
            value=f"""
            <div style="
                border: 2px solid black;  /* Border around the text area */
                padding: 10px;  /* Padding for better readability */
                background-color: #ffffff;  /* White background for better contrast */
                color: #000000;  /* Black text for maximum readability */
                font-size: 14px;  /* Larger font for better readability */
                width: calc(100% - 20px);  /* Make it full width with padding adjustment to avoid overflow */
                max-width: 800px;  /* Set a max-width to avoid exceeding viewport */
                height: 300px;  /* Fixed height */
                overflow-y: auto;  /* Enable scrolling for overflow content */
                box-sizing: border-box;  /* Ensure padding and border are included in width calculation */
                margin: 0 auto;  /* Center the element horizontally */
            ">
                {result_text}
            </div>
            """
        )

        # Display the title and the styled text HTML element
        display(title_html, text_area_html)

    def run_analysis(self, b):
        with self.output:
            clear_output(wait=True)
            print("Starting analysis. This may take a few moments...")

        # Generate prompt from the data
        data_str = self.data.to_string()

        prompt = f"""Analyze the following dataset to suggest ways for cost optimization in energy usage using the services by LŌD.
    Don't complain about any lack of data, just use what you have. Try to use numbers from the dataset as much as you can, using examples when possible.
    Make it as if it were a marketing pitch for LŌD's services.
    Take into account the following data about LōD (there's no need to cite everything, just use what you think is relevant):

    1. LŌD’s platform is designed for mission-critical environments where availability comes first. With built-in redundancy, failover mechanisms, and the ability to scale across multiple sites and devices, LōD ensures reliability and high availability for industries that demand consistent, uninterrupted operations.
    2. LōD is evolving with AI at its core, leveraging the strengths of LLMs for real-time monitoring, anomaly detection, and predictive maintenance. This allows customers to proactively optimize operations and reduce downtime by making smarter, data-driven decisions.
    3. Created by a team of experts with deep knowledge of energy markets and industrial operations, LōD is designed to meet the unique needs of industries that require precise energy management. This expertise allows LōD to offer tailored solutions for managing operations based on grid conditions, optimizing energy costs, and maintaining peak operational performance.
    4. LōD provides 24/7 customer support with a dedicated team of experts ensuring smooth operations and minimal downtime. The platform’s rapid response to issues, combined with tailored onboarding and training, allows clients to integrate LōD seamlessly into their operations while receiving continuous guidance and troubleshooting assistance.
    5. LŌD Integrates with major DCIM platforms to implement advanced temperature management strategies to maintain quality of service and decrease carbon emissions based on RAILS no-code programming language.
    6. Mission-Critical datacenters rely on multiple energy sources to ensure availability and quality of service. LŌD optimizes orchestration of energy resources to maximize profits, minimize carbon emissions and improve economics for datacenters.
    7. Participate in demand response programs and avoid peaks by designing your multi-layer energy strategy based on real-time data from over 20,000 grid nodes.
    8. Trade energy and ancillaries in the Day-Ahead-Market and lock-in opportunities based on your unique advantages.

    {data_str}
    """

        # Fetch AI analysis result from ChatGPTAPI
        result = self.chat_gpt_api.analyze_data(prompt)

        with self.output:
            clear_output(wait=True)
            if "error" in result:
                print(result["error"])
            else:
                # Extract the generated text before passing it to display_analysis_result
                generated_text = result["generated_text"]
                self.display_analysis_result(generated_text)