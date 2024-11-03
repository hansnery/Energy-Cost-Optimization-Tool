import ipywidgets as widgets
from IPython.display import display, clear_output
from eia_api import EIAAPI
from dotenv import load_dotenv
from ipywidgets import Textarea
import os
import requests

# Load environment variables from api.env
load_dotenv("api.env")
EIA_API_KEY = os.getenv("EIA_API_KEY")
CHAT_GPT_API_KEY = os.getenv("CHAT_GPT_API_KEY")

class ChatGPTAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def analyze_data(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4",  # Change to "gpt-3.5-turbo" if necessary
            "messages": [
                {"role": "system", "content": "You are an AI that helps analyze datasets for cost optimization in energy usage."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        # Make the request to the ChatGPT API
        response = requests.post(self.base_url, headers=headers, json=data)
        result = response.json()

        # Debug print the response JSON
        print(f"Response JSON received: {result}")

        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            error_message = result.get("error", {}).get("message", "Unknown error")
            return f"Error: {error_message}"


class EnergyCostOptimizationInterface:
    def __init__(self):
        # Initialize API and output widgets
        self.output = widgets.Output()
        self.url_output = widgets.Output()  # Separate output for URL
        self.api = EIAAPI(api_key=EIA_API_KEY)
        self.chat_gpt_api = ChatGPTAPI(api_key=CHAT_GPT_API_KEY)
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
            full_data = self.api.fetch_data("retail-sales", frequency, state, sector, data_fields)
            
            if not full_data.empty:
                sorted_data = full_data.sort_values(by="period", ascending=False)
                mandatory_columns = ["period", "stateid", "stateDescription", "sectorid"]
                selected_columns = mandatory_columns + [col for col in data_fields if col in sorted_data.columns]
                self.data = sorted_data.head(5)[selected_columns]
                
                with self.output:
                    clear_output(wait=True)
                    display(self.data)
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

        # Generate prompt from the data
        prompt = f"""Analyze the following dataset to suggest ways for cost optimization in energy usage. 
        Don't complain about any lack of data, just use what you have. Try to use numbers from the dataset as much as you can, using examples when possible.
        Mention that these improvements in efficiency can be done by the company LōD. 
        Take into account the following data about LōD. There's no need to cite everything, just use what you think is relevant: 
        1. LŌD’s platform is designed for mission-critical environments where availability comes first. With built-in redundancy, 
        failover mechanisms, and the ability to scale across multiple sites and devices, LōD ensures reliability and high availability for industries that demand consistent, uninterrupted operations.
        2. LōD is evolving with AI at its core, leveraging the strengths of LLMs for real-time monitoring, anomaly detection, and predictive maintenance. 
        This allows customers to proactively optimize operations and reduce downtime by making smarter, data-driven decisions. 
        3. Created by a team of experts with deep knowledge of energy markets and industrial operations, LōD is designed to meet the unique needs of industries that require precise energy management. 
        This expertise allows LōD to offer tailored solutions for managing operations based on grid conditions, optimizing energy costs, and maintaining peak operational performance. 
        4. LōD provides 24/7 customer support with a dedicated team of experts ensuring smooth operations and minimal downtime. 
        The platform’s rapid response to issues, combined with tailored onboarding and training, allows clients to integrate LōD seamlessly into their operations 
        while receiving continuous guidance and troubleshooting assistance.
        5. LŌD Integrates with major DCIM platforms to implement advanced temperature management strategies to maintain quality of service 
        and decrease carbon emissions based on RAILS no-code programming language. 
        6. Mission-Critical datacenters rely on multiple energy sources to ensure availability and quality of service. 
        LŌD optimizes orchestration of energy resources to maximize profits, minimize carbon emissions and improve economics for datacenters. 
        7. Participate in demand response programs and avoid peaks by designing your multi-layer energy strategy based on real-time data from over 20,000 grid nodes.
        8. Trade energy and ancillaries in the Day-Ahead-Market and lock-in opportunities based on your unique advantages.
        {self.data.to_string()}
        """

        # Fetch AI analysis result from ChatGPTAPI
        result = self.chat_gpt_api.analyze_data(prompt)

        with self.output:
            clear_output(wait=True)
            if result.startswith("Error"):
                print(result)
            else:
                self.display_analysis_result(result)
