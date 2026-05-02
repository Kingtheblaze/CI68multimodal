import requests
import os

# The URL where your backend is running
url = "http://localhost:8000/ingest"

# 1. Prepare the product metadata
payload = {
    "name": "Nebula Wireless Mouse",
    "description": "Ergonomic RGB gaming mouse with 25k DPI sensor.",
    "category": "Peripherals",
    "brand": "Nebula",
    "product_id": "mouse_001"
}

# 2. Use an existing image from your project for the test
# We'll look for shoes.png in the backend/data folder
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "backend", "data", "shoes.png")

if not os.path.exists(image_path):
    print(f"❌ Error: Could not find test image at {image_path}")
    print("Please make sure you are running this from the multimodal-graph-rag folder.")
else:
    print(f"--- Sending ingest request for '{payload['name']}' ---")
    with open(image_path, "rb") as img_file:
        files = {"file": img_file}
        try:
            response = requests.post(url, data=payload, files=files)
            if response.status_code == 200:
                print("SUCCESS!")
                print(response.json())
            else:
                print(f"FAILED with status code {response.status_code}")
                print(response.text)
        except requests.exceptions.ConnectionError:
            print("CONNECTION ERROR: Is your backend running at http://localhost:8000?")
            print("Hint: Make sure 'docker compose up' is running successfully.")
