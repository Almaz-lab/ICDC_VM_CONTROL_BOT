import requests
import json
from dotenv import load_dotenv
import os
from tabulate import tabulate

def get_presale_vms():
    load_dotenv()
    URL = os.getenv("URL")
    TOKEN = os.getenv("TOKEN").strip("'")
    x_miq_group = os.getenv("x-miq-group")
    x_icdc_account = os.getenv("x-icdc-account")
    x_icdc_role = os.getenv("x-icdc-role")
    
    if not URL or not TOKEN:
        raise ValueError("URL and TOKEN environment variables must be set")
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        "x-miq-group": x_miq_group,
        "x-icdc-account": x_icdc_account,
        "x-icdc-role": x_icdc_role 
    }
    
    params = {
        "expand": "resources"
    }
    
    try:
        response = requests.get(URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        vms = []
        for resource in data.get('resources', []):
            try:
                if 'PRESALE' in resource.get('description', ''):
                    vm = {
                        'name': resource['name'],
                        'id': resource['id'],
                        'description': resource.get('description', ''),
                        'power_status': resource.get('options', {}).get('power_status', 'unknown')
                    }
                    vms.append(vm)
            except KeyError as e:
                print(f"Skipping malformed resource: {e}")
                continue
        
        return vms
    
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []

if __name__ == "__main__":
    sorted_vms = sorted(get_presale_vms(), key=lambda x: x['name'])
    headers = ['Name', 'ID', 'Description', 'Power Status']
    table_data = [[vm['name'], vm['id'], vm['description'], vm['power_status']] for vm in sorted_vms]
    print(tabulate(table_data, headers=headers, tablefmt='grid'))