import os
import time
import requests
from dotenv import load_dotenv, set_key

# Загружаем .env
ENV_FILE = ".env"
load_dotenv(ENV_FILE)

# Константы
API_URL = os.getenv("API_URL")
CLIENT_ID = "insights"
USERNAME = os.getenv("ICDC_USERNAME", "your_username")
PASSWORD = os.getenv("ICDC_PASSWORD", "your_password")

def get_token_via_refresh():
    refresh_token = os.getenv("REFRESH_TOKEN")
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",

        "refresh_token": refresh_token,
        "scope": "openid profile email groups"  # Add scope to ensure proper group permissions
    }
    response = requests.post(API_URL, data=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("access_token"), response_data.get("refresh_token")
    else:
        response_data = response.json()
        if response_data.get("error") == "invalid_grant":
            return get_token()
        print("Error getting token via refresh_token:", response.text)        
        return None, None

def get_token():
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
        # "scope": "openid profile email groups"  # Add scope to ensure proper group permissions
    }
    response = requests.post(API_URL, data=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("access_token"), response_data.get("refresh_token")
    else:
        print("Error getting token via password:", response.text)        
        return None, None
    
    
def update_env(token, refresh_token):
    if token and refresh_token:
        set_key(ENV_FILE, "TOKEN", token.strip('"').strip("'"))
        set_key(ENV_FILE, "REFRESH_TOKEN", refresh_token.strip('"').strip("'"))
        print("Token and refresh_token successfully updated in .env")
    else:
        print("Failed to update .env")

def main():
    while True:
        token, refresh_token = get_token_via_refresh()
        update_env(token, refresh_token)
        time.sleep(1500)  # 25 minutes = 1500 seconds

if __name__ == "__main__":
    main()