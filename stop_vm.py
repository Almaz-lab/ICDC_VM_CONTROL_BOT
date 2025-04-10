import requests
import json
from dotenv import load_dotenv
import os
import sys

def stop_vm(vm_id):
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    URL = os.getenv("URL")
    x_miq_group = os.getenv("x-miq-group")
    x_icdc_account = os.getenv("x-icdc-account")
    x_icdc_role = os.getenv("x-icdc-role")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        "x-miq-group": x_miq_group,
        "x-icdc-account": x_icdc_account,
        "x-icdc-role": x_icdc_role
    }
    
    data = {
        "action": "stop"
    }
    
    #vm_id = input("Enter VM ID: ")
    response = requests.post(f"{URL}/{vm_id}", headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"VM with ID {vm_id} is stopped...")
    else:
        print(f"Failed to stop VM. Status code: {response.status_code}")
        print(f"Error message: {response.text}")

if __name__ == "__main__":
    stop_vm(sys.argv[1])