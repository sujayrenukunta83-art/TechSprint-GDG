import pandas as pd
import google.genai as genai

def load_data(file):
    """
    Reads a CSV file into a Pandas DataFrame and validates the structure.
    
    Args:
        file: The file object uploaded by the user.
        
    Returns:
        pd.DataFrame: A cleaned dataframe.
        
    Raises:
        ValueError: If columns are missing or data formats are invalid.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file)

        # Standardize column names (remove extra spaces)
        df.columns = df.columns.str.strip()

        # Check for required columns
        required_columns = {'Date', 'City', 'AQI'}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise ValueError(f"Missing required columns: {', '.join(missing)}. Please ensure CSV has 'Date', 'City', and 'AQI'.")

        # Convert Date column to datetime objects
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Check if Date conversion failed for any row
        if df['Date'].isna().any():
            df = df.dropna(subset=['Date'])

            raise ValueError("Date column could not be parsed. Please check the date format.")

        # Ensure AQI is numeric, coerce errors to NaN and drop them
        df['AQI'] = pd.to_numeric(df['AQI'], errors='coerce')
        df = df.dropna(subset=['Date', 'AQI'])

        return df

    except Exception as e:
        raise ValueError(f"Error loading data: {str(e)}")


def summarize_data(df):
    """
    Generates a statistical summary of the dataset for the LLM to analyze.
    This reduces token usage by sending stats instead of raw rows.
    
    Args:
        df (pd.DataFrame): The cleaned dataframe.
        
    Returns:
        str: A text summary of the data trends.
    """
    # 1. Basic Metadata
    start_date = df['Date'].min().strftime('%Y-%m-%d')
    end_date = df['Date'].max().strftime('%Y-%m-%d')
    cities = df['City'].unique().tolist()
    
    summary_lines = [
        "### DATASET SUMMARY",
        f"Date Range: {start_date} to {end_date}",
        f"Cities Included: {', '.join(cities)}",
        "\n### CITY-WISE STATISTICS"
    ]

    # 2. Iterate through each city to calculate stats
    for city in cities:
        city_df = df[df['City'] == city]
        
        # General stats
        min_aqi = city_df['AQI'].min()
        max_aqi = city_df['AQI'].max()
        avg_aqi = city_df['AQI'].mean()
        
        summary_lines.append(f"\nCity: {city}")
        summary_lines.append(f"- Overall Min AQI: {min_aqi:.2f}")
        summary_lines.append(f"- Overall Max AQI: {max_aqi:.2f}")
        summary_lines.append(f"- Overall Avg AQI: {avg_aqi:.2f}")
        
        # Monthly Trends (Resample by Month)
        # We group by month to see the seasonal trend
        monthly_trend = city_df.set_index('Date').resample('ME')['AQI'].mean()
        
        summary_lines.append("- Monthly Averages:")
        for date, value in monthly_trend.items():
            if pd.notna(value):
                summary_lines.append(f"  {date.strftime('%Y-%m')}: {value:.1f}")

    # Join all lines into a single string
    return "\n".join(summary_lines)




def get_gemini_response(prompt, api_key):
    """
    Sends a prompt to Google Gemini and returns the response.
    Uses the official google-genai SDK (stable usage).
    """
    try:
        if not api_key:
            return "Error: API Key is missing."

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt
        )

        if response and hasattr(response, "text") and response.text:
            return response.text
        else:
            return "Error: Received empty response from Gemini."

    except Exception as e:
        return f"Error connecting to Gemini: {str(e)}"