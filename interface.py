# interface.py
import ipywidgets as widgets
from IPython.display import display, clear_output
from eia_api import EIAAPI
from hf_api import HFAPI
from data_processing import generate_prompt
import pandas as pd

# Interface class to encapsulate UI elements and logic
class EnergyCostOptimizationInterface:
    def __init__(self):
        # Initialize API key inputs and dropdowns
        self.eia_api_key_input = widgets.Text(
            placeholder='Enter EIA API Key', description='EIA API Key:'
        )
        self.hf_api_key_input = widgets.Text(
            placeholder='Enter Hugging Face API Key', description='HF API Key:'
        )
        self.date_range = widgets.Dropdown(
            options=['Last Month', 'Last Quarter', 'Last Year'],
            value='Last Month',
            description='Date Range:'
        )
        self.run_button = widgets.Button(
            description="Run Analysis", button_style='success'
        )

        # Attach the event handler for the button
        self.run_button.on_click(self.run_analysis)

        # Display the UI when initialized
        self.display_interface()

    def display_interface(self):
        # Display input fields and button
        display(self.eia_api_key_input, self.hf_api_key_input, self.date_range, self.run_button)

    def run_analysis(self, b):
        # Clear previous output
        clear_output(wait=True)
        self.display_interface()

        # Fetch API keys and selected date range
        eia_api_key = self.eia_api_key_input.value
        hf_api_key = self.hf_api_key_input.value
        selected_range = self.date_range.value

        # Initialize API handlers
        eia_api = EIAAPI(api_key=eia_api_key)
        hf_api = HFAPI(api_key=hf_api_key)

        # Set date range for EIA API
        date_ranges = {
            'Last Month': ('2023-09-01', '2023-09-30'),
            'Last Quarter': ('2023-07-01', '2023-09-30'),
            'Last Year': ('2023-01-01', '2023-12-31')
        }
        start_date, end_date = date_ranges[selected_range]

        # Fetch data from the EIA API
        try:
            df = eia_api.fetch_data(start_date, end_date)
            display(df.head())  # Show data preview

            # Generate prompt for Hugging Face API
            prompt = generate_prompt(df, selected_range)
            hf_result = hf_api.analyze_data(prompt)

            # Display analysis result
            print("Analysis Result:", hf_result)
        except Exception as e:
            print("Error:", e)
