import requests
import json

url = "http://127.0.0.1:5000/admin/generate_table_qr"
headers = {"Content-Type": "application/json"}
data = {"table_number": 1}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:", response.json())
    except json.JSONDecodeError:
        print("Response Text:", response.text)
except Exception as e:
    print(f"Request failed: {e}")
