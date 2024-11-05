# Energy Cost Optimization Tool

This tool leverages real-time data from the U.S. Energy Information Administration (EIA) API along with the capabilities of a Large Language Model (LLM) to provide advanced insights into energy costs and trends. This mini-application was created to assist users in understanding energy consumption, optimizing energy usage, and reducing costs effectively.

[![Open in Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hansnery/Energy-Cost-Optimization-Tool/blob/main/Energy_Cost_Optimization_Tool.ipynb)

## Table of Contents

1. [Features](#features)
2. [Getting Started](#getting-started)
3. [Installation](#installation)
4. [Usage Guide](#usage-guide)
5. [APIs Used](#apis-used)
6. [Folder Structure](#folder-structure)
7. [Contributing](#contributing)
8. [License](#license)

## Features

- **Fetch Real-time Data**: The app fetches data from the EIA API to provide a real-time perspective on energy usage and trends.
- **Large Language Model Integration**: Uses GPT-4 (ChatGPT-4) to analyze the fetched energy data, giving insights, suggestions, and optimization strategies.
- **User-friendly UI**: The interface was built using `ipywidgets` in a Jupyter Notebook to make interactions intuitive and easy to follow.
- **Data Visualization**: Presents analyzed data in a simple, readable format, designed to help decision-makers quickly grasp key points.

## Getting Started

To get started with the **Energy Cost Optimization Tool**, you'll need to have a Jupyter environment (such as Google Colab or Jupyter Notebook) ready to go. This project uses `ipywidgets` for the interface, making it interactive and easy to work with.

### Prerequisites

- Python 3.7+
- Jupyter Notebook or Google Colab
- An API key from the U.S. Energy Information Administration (EIA)
- An API key for the OpenAI API to utilize GPT-4

Make sure the following Python packages are installed:

- `ipywidgets`
- `requests`
- `pandas`
- `dotenv`

These can be installed via the `requirements.txt` file as shown in the [Installation](#installation) section.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/Energy-Cost-Optimization-Tool.git
   cd Energy-Cost-Optimization-Tool
   ```
2. **Install Dependencies**
   Install the required packages using `pip`:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   EIA_API_KEY=your_eia_api_key_here
   CHAT_GPT_API_KEY=your_openai_api_key_here
   ```

## Usage Guide

1. **Launch in Google Colab**  
   Simply click the **Open in Google Colab** button, and the notebook will automatically:

   - Clone the repository.
   - Set up the environment.
   - Display the interface for you to start using immediately.

OR

1. **Launch Jupyter Notebook**
   Run the Jupyter Notebook from your terminal:

   ```bash
   jupyter notebook Energy_Cost_Optimization_Tool.ipynb
   ```

1. **Select a Data Route**
   The interface will allow you to select data routes related to electricity usage, such as "Electricity Sales to Ultimate Customers" or "Electric Power Operations".

1. **Configure Data Fetching**
   Use dropdowns to configure parameters like:

   - Frequency (Monthly, Quarterly, Annual)
   - State/Census Region
   - Sector
   - Date Range (Start and End Dates)

1. **Fetch and Analyze Data**

   - Click **Fetch Data** to retrieve the information from the EIA API.
   - Click **Run Analysis** to let GPT-4 analyze the fetched data and provide insightful suggestions for energy cost optimization.

1. **View Analysis**
   The results from the LLM analysis will be displayed clearly in a bordered text area for easy reading.

## APIs Used

- **EIA API**: Provides real-time electricity and energy data that serves as the core dataset for this application.
- **OpenAI GPT-4 (ChatGPT-4)**: Processes the energy data to generate a detailed analysis, highlighting opportunities for cost savings and efficiency improvements.

## Folder Structure

- `Energy_Cost_Optimization_Tool.ipynb`: The main Jupyter Notebook containing the UI and integration code.
- `eia_api.py`: Script for managing requests and interactions with the EIA API.
- `chat_gpt_api.py`: Script for interfacing with OpenAI's API to perform data analysis.
- `interface.py`: Handles UI components built with `ipywidgets`.
- `.env`: Environment file containing API keys (not included in the repo for security).
- `README.md`: This document, providing project details and setup instructions.

## Contributing

If you'd like to contribute to improving this tool, please fork the repository and create a pull request. We appreciate all contributions and ideas for enhancing functionality.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
