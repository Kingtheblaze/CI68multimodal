import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

# Mock E-commerce Data
products = [
    {
        "id": "prod_001",
        "name": "Sentinel Speed Runners",
        "description": "High-performance running shoes with breathable mesh and responsive cushioning. Perfect for marathons and daily training.",
        "category": "Footwear",
        "brand": "VelocityX",
        "image": "shoes.png"
    },
    {
        "id": "prod_002",
        "name": "Apex Chronograph",
        "description": "Luxury minimalist watch with a genuine leather strap and sapphire crystal. Water-resistant up to 50m.",
        "category": "Accessories",
        "brand": "LuxeTime",
        "image": "watch.png"
    },
    {
        "id": "prod_003",
        "name": "Titanium Book Pro",
        "description": "Ultra-slim metallic laptop with high-resolution display and 16-hour battery life. Designed for creators.",
        "category": "Electronics",
        "brand": "TitanTech",
        "image": "laptop.png"
    }
]

def ingest():
    # Use absolute path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    
    for p in products:
        image_path = os.path.join(data_dir, p["image"])
        if not os.path.exists(image_path):
            print(f"Skipping {p['name']}, image not found.")
            continue
            
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {
                "name": p["name"],
                "description": p["description"],
                "category": p["category"],
                "brand": p["brand"],
                "product_id": p["id"]
            }
            try:
                # Wait for backend to be ready if needed
                response = requests.post(f"{BASE_URL}/ingest", files=files, data=data)
                if response.status_code == 200:
                    print(f"✅ Ingested {p['name']}")
                else:
                    print(f"❌ Failed to ingest {p['name']}: {response.text}")
            except Exception as e:
                print(f"Error connecting to backend: {e}")

if __name__ == "__main__":
    import time
    print("Waiting for backend services...")
    time.sleep(5) # Basic wait
    ingest()
