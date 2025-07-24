#!/usr/bin/env python3
"""
Tinder API Continuous Scraper
Makes continuous requests to Tinder's recommendations API until a non-200 response.
Stores all collected users in a CSV file.
"""

import json
import csv
import time
from datetime import datetime
from curl_cffi import requests

class TinderScraper:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.users_collected = []
        self.request_count = 0
        self.csv_filename = f"tinder_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # CSV headers
        self.csv_headers = [
            'user_id', 'name', 'age', 'bio', 'birth_date',
            'photo_count', 'photo_urls'
        ]
        
        # Initialize CSV file
        self.init_csv()

    def init_csv(self):
        """Initialize CSV file with headers"""
        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.csv_headers)
        print(f"Initialized CSV file: {self.csv_filename}")

    def calculate_age(self, birth_date_str):
        """Calculate age from birth date string"""
        try:
            if not birth_date_str or birth_date_str == 'N/A':
                return 'N/A'
            
            birth_date = datetime.fromisoformat(birth_date_str.replace('Z', '+00:00'))
            today = datetime.now()
            age = today.year - birth_date.year
            
            # Adjust if birthday hasn't occurred this year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
                
            return age
        except:
            return 'N/A'

    def _make_profile_update_request(self, data, action_name):
        """Generic method to update user profile settings."""
        print(f"Updating {action_name}...")
        url = "https://api.gotinder.com/v2/profile/user"
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': self.auth_token,
            'User-Agent': 'Tinder/16.14.0 (iPhone; iOS 18.5; Scale/3.00)'
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30, impersonate="chrome110")
            if response.status_code == 200:
                print(f"✓ Successfully updated {action_name}.")
            else:
                print(f"✗ Failed to update {action_name}. Status: {response.status_code}")
                print(f"  Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Request to update {action_name} failed: {e}")
        except json.JSONDecodeError as e:
            print(f"✗ Failed to parse JSON response from {action_name} update: {e}")

    def update_location(self, lat, lon):
        """Update the user's location."""
        print(f"Updating location to: lat={lat}, lon={lon}...")
        url = "https://api.gotinder.com/v2/meta"
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': self.auth_token,
            'User-Agent': 'Tinder/16.14.0 (iPhone; iOS 18.5; Scale/3.00)'
        }
        data = {"force_fetch_resources": True, "background": False, "lat": lat, "lon": lon}
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30, impersonate="chrome110")
            if response.status_code == 200:
                print("✓ Successfully updated location.")
            else:
                print(f"✗ Failed to update location. Status: {response.status_code}")
                print(f"  Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Request to update location failed: {e}")
        except json.JSONDecodeError as e:
            print(f"✗ Failed to parse JSON response from location update: {e}")

    def update_distance_filter(self, distance_km):
        """Update the user's distance filter."""
        distance_miles = distance_km / 1.60934
        data = {"distance_filter": distance_miles}
        self._make_profile_update_request(data, f"distance filter to {distance_km} km ({distance_miles:.2f} miles)")

    def update_gender_interest(self, gender_code):
        """Update the gender interest for recommendations."""
        gender_map = {0: "Men", 1: "Women"}
        if gender_code not in gender_map:
            print(f"✗ Invalid gender code: {gender_code}. Use 0 for Men, 1 for Women.")
            return
        data = {"interested_in_genders": [gender_code]}
        self._make_profile_update_request(data, f"gender interest to {gender_map[gender_code]}")

    def update_age_filter(self, min_age, max_age, auto_expand=True):
        """Update the age filter for recommendations."""
        data = {
            "age_filter_min": min_age,
            "age_filter_max": max_age,
            "auto_expansion": {"age_toggle": auto_expand}
        }
        self._make_profile_update_request(data, f"age filter to {min_age}-{max_age}")


    def make_recs_request(self):
        """Make a single request to the Tinder recommendations API."""
        url = "https://api.gotinder.com/v2/recs/core"
        params = {'locale': 'en-GB'}
        headers = {
            'X-Auth-Token': self.auth_token,
            'User-Agent': 'Tinder/16.14.0 (iPhone; iOS 18.5; Scale/3.00)',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30, impersonate="chrome110")
            return response.status_code, response.json() if response.status_code == 200 else response.text
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None, str(e)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return response.status_code, response.text

    def extract_users_from_response(self, data):
        """Extract users from API response and add to the collection."""
        if 'data' not in data or 'results' not in data['data']:
            return 0
        
        users_found = 0
        for result in data['data']['results']:
            if result.get('type') != 'user':
                continue
            
            user = result.get('user', {})
            user_id = user.get('_id')
            
            if not user_id or any(u['user_id'] == user_id for u in self.users_collected):
                continue
            
            photos = user.get('photos', [])
            photo_urls = [p.get('url') for p in photos if p.get('url')]
            
            user_data = {
                'user_id': user_id,
                'name': user.get('name', ''),
                'age': self.calculate_age(user.get('birth_date', '')),
                'bio': (user.get('bio') or '').replace('\n', ' ').replace('\r', ' '),
                'birth_date': user.get('birth_date', ''),
                'photo_count': len(photos),
                'photo_urls': ' | '.join(photo_urls),
            }
            
            self.users_collected.append(user_data)
            users_found += 1
        
        return users_found

    def save_users_to_csv(self, new_users_data):
        """Append new users to the CSV file."""
        if not new_users_data:
            return
        
        with open(self.csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_headers)
            writer.writerows(new_users_data)
    
    def run_continuous_scraping(self, delay_between_requests=2, max_requests=None):
        """Run continuous scraping until a non-200 response or limit is reached."""
        print("\n" + "-" * 60)
        print("Starting continuous Tinder scraping...")
        print(f"Delay between requests: {delay_between_requests} seconds")
        print("-" * 60)
        
        try:
            while not max_requests or self.request_count < max_requests:
                self.request_count += 1
                print(f"Request #{self.request_count}...", end=" ", flush=True)
                
                status_code, response_data = self.make_recs_request()
                
                if status_code != 200:
                    print(f"Non-200 response: {status_code}")
                    print(f"Response: {response_data}")
                    break
                
                initial_user_count = len(self.users_collected)
                new_users_count = self.extract_users_from_response(response_data)
                
                if new_users_count > 0:
                    new_batch = self.users_collected[initial_user_count:]
                    self.save_users_to_csv(new_batch)
                    print(f"✓ Found {new_users_count} new users (Total: {len(self.users_collected)})")
                else:
                    print("✓ No new users found")
                    break
                
                time.sleep(delay_between_requests)
                    
        except KeyboardInterrupt:
            print("\n\nScraping interrupted by user (Ctrl+C).")
        
        finally:
            print("\n" + "="*60)
            print("SCRAPING SUMMARY")
            print("="*60)
            print(f"Total requests made: {self.request_count}")
            print(f"Total unique users collected: {len(self.users_collected)}")
            print(f"CSV file saved at: {self.csv_filename}")
            
            if self.users_collected:
                print("\nSample of collected users:")
                for i, user in enumerate(self.users_collected[:5]):
                    print(f"  {i+1}. {user['name']} (ID: {user['user_id'][:8]}...) - Age: {user['age']} - {user['photo_count']} photos")
                if len(self.users_collected) > 5:
                    print(f"  ... and {len(self.users_collected) - 5} more users")

def main():
    """Main function to configure and run the scraper."""
    # --- CONFIGURATION ---
    AUTH_TOKEN = "807df1fa-1100-4434-ba6f-9ecc0f827252"  # IMPORTANT: Replace with your actual token
    
    # Location Settings
    LATITUDE = 45.757350,
    LONGITUDE = 4.835801
    
    # Discovery Settings
    MIN_AGE = 18
    MAX_AGE = 25
    DISTANCE_KM = 10
    INTERESTED_IN_GENDER = 0  # 0 for Men, 1 for Women
    
    # Scraper Settings
    DELAY_BETWEEN_REQUESTS = 2  # seconds
    MAX_REQUESTS = None  # Set to None for unlimited, or a number for a limit
    
    # --- EXECUTION ---
    scraper = TinderScraper(AUTH_TOKEN)
    
    # Update profile settings before scraping
    print("Configuring profile settings...")
    scraper.update_location(LATITUDE, LONGITUDE)
    scraper.update_age_filter(MIN_AGE, MAX_AGE)
    scraper.update_distance_filter(DISTANCE_KM)
    scraper.update_gender_interest(INTERESTED_IN_GENDER)
    
    # Run the scraping process
    scraper.run_continuous_scraping(
        delay_between_requests=DELAY_BETWEEN_REQUESTS,
        max_requests=MAX_REQUESTS
    )

if __name__ == "__main__":
    main()