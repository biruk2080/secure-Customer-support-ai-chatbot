
import json
import requests
def send_to_splunk(data):
    # Replace these variables with your HEC token and Splunk URL
    hec_token = "9b36bc88-0888-4432-9a97-e47d10b87083"
    splunk_url = "http://localhost:8088/services/collector/event"

    headers = {
        'Authorization': f'Splunk {hec_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(splunk_url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == 200:
        print("Data sent to Splunk successfully")
    else:
        print(f"Failed to send data to Splunk: {response.status_code}, {response.text}")