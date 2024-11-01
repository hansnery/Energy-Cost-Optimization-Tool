def generate_prompt(df, date_range):
    return (
        f"Analyze the energy data trends for {date_range}:\n\n"
        f"Monthly Price: {df['price'].values.tolist()}\n"
        f"Monthly Revenue: {df['revenue'].values.tolist()}\n"
        f"Monthly Sales: {df['sales'].values.tolist()}\n\n"
        "Provide insights on changes, peaks, and any notable patterns."
    )
