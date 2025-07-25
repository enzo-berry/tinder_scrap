# Tinder API Continuous Scraper

A Python script that leverages the Tinder API to continuously scrape user recommendations. It allows you to set your account's location and configure discovery settings such as distance, age range, and gender interest before fetching and saving profiles to a well-structured CSV file.

## Features

- **Continuous Scraping**: Runs indefinitely until you stop it or it receives an error from the API.
- **Set Geolocation**: Programmatically update your profile's latitude and longitude to get recommendations from any location in the world.
- **Advanced Discovery Settings**:
    - **Distance Filter**: Set the maximum search radius in kilometers.
    - **Age Filter**: Define a specific age range (min/max) for profiles.
    - **Gender Interest**: Choose to see men (0) or women (1).
- **CSV Export**: Automatically saves all unique user profiles into a timestamped CSV file with headers for easy data analysis.
- **Duplicate Prevention**: Keeps track of collected users to ensure no duplicate entries are saved.
- **Resilient**: Handles request and JSON parsing errors gracefully.
- **Configurable**: Easily set your auth token, scraper delays, and all discovery preferences in one central configuration block.

## How It Works

The script uses the `curl_cffi` library to impersonate a browser and make authenticated requests to internal Tinder API endpoints. Before starting the scraping loop, it sends a series of `POST` requests to update your profile's discovery settings:
1.  **Location**: Sets the latitude and longitude.
2.  **Age Range**: Sets the `age_filter_min` and `age_filter_max`.
3.  **Distance**: Sets the `distance_filter` (converting KM to miles as required by the API).
4.  **Gender**: Sets the `interested_in_genders`.

Once configured, it continuously calls the `/v2/recs/core` endpoint, parses the user results, and appends them to a CSV file.

## Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/tinder-scraper.git
    cd tinder-scraper
    ```

2.  **Install the required Python library:**
    This script depends on `curl_cffi` to make requests that can bypass Tinder's browser checks.
    ```sh
    pip install "curl_cffi"
    ```

## Usage

1.  **Get Your Tinder Auth Token**
    You must obtain your `X-Auth-Token` to use this script. You can get this by:
    - Logging into Tinder on a web browser.
    - Opening the browser's developer tools (F12 or Ctrl+Shift+I).
    - Go to the "Network" tab.
    - Look for requests made to `api.gotinder.com`.
    - Find the `X-Auth-Token` value in the request headers.

2.  **Configure the Scraper**
    Open the script and edit the `main()` function to set your preferences:
    ```python
    def main():
        """Main function to configure and run the scraper."""
        # --- CONFIGURATION ---
        AUTH_TOKEN = "YOUR_X_AUTH_TOKEN_HERE"  # IMPORTANT: Replace with your actual token

        # Location Settings (e.g., Lyon, France)
        LATITUDE = 45.766684
        LONGITUDE = 4.742095

        # Discovery Settings
        MIN_AGE = 18
        MAX_AGE = 25
        DISTANCE_KM = 15  # Search radius in kilometers
        INTERESTED_IN_GENDER = 1  # 0 for Men, 1 for Women

        # Scraper Settings
        DELAY_BETWEEN_REQUESTS = 2  # Seconds to wait between requests
        MAX_REQUESTS = None  # Set to a number to limit, or None to run forever

        # --- EXECUTION ---
        # ...
    ```

3.  **Run the Script**
    Execute the script from your terminal:
    ```sh
    python tinder_scraper.py
    ```
    The script will first update your profile settings and then begin scraping. You can stop it at any time by pressing `Ctrl+C`.

## Output

The script generates a CSV file named `tinder_users_YYYYMMDD_HHMMSS.csv`. The file contains the following columns:
-   `user_id`: The unique Tinder user ID.
-   `name`: The user's first name.
-   `age`: The user's calculated age.
-   `bio`: The user's profile biography.
-   `birth_date`: The raw birth date string from the API.
-   `photo_count`: The number of photos on the profile.
-   `photo_urls`: A `|`-separated list of URLs for the user's photos.

## Disclaimer

This script is intended for educational and research purposes only. The Tinder API is not public, and using it may be against their Terms of Service. The developers of this script are not responsible for any consequences of its use, including account suspension or banning. Use this tool responsibly and ethically.
