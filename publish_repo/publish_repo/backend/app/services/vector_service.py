import os
import weaviate
import weaviate.classes.config as wvcc
from dotenv import load_dotenv
import time

load_dotenv()

class VectorService:
    def __init__(self):
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        host_name = weaviate_url.replace("http://", "").replace("https://", "").split(":")[0]

        self.client = None
        self.enabled = False
        print(f"Connecting to Weaviate at host: {host_name}")

        for i in range(5):
            try:
                self.client = weaviate.connect_to_custom(
                    http_host=host_name,
                    http_port=8080,
                    http_secure=False,
                    grpc_host=host_name,
                    grpc_port=50051,
                    grpc_secure=False,
                )
                if self.client.is_ready():
                    self.enabled = True
                    print("Successfully connected to Weaviate!")
                    break
            except Exception as e:
                print(f"Connection attempt {i+1} failed. Retrying in 5s... Error: {e}")
                time.sleep(5)

        if not self.enabled:
            print("Weaviate is unavailable. Vector search will run in disabled mode.")
            return

        self._setup_schema()

    def _setup_schema(self):
        """Initializes the Multimodal Product collection in Weaviate"""
        if not self.enabled or self.client is None:
            return

        try:
            if not self.client.collections.exists("Product"):
                self.client.collections.create(
                    name="Product",
                    vectorizer_config=wvcc.Configure.Vectorizer.multi2vec_clip(
                        image_fields=["image"],
                        text_fields=["name", "description"]
                    ),
                    description="E-commerce products with multimodal support",
                    properties=[
                        wvcc.Property(name="name", data_type=wvcc.DataType.TEXT),
                        wvcc.Property(name="description", data_type=wvcc.DataType.TEXT),
                        wvcc.Property(name="image", data_type=wvcc.DataType.BLOB),
                        wvcc.Property(name="product_id", data_type=wvcc.DataType.TEXT),
                    ]
                )
                print("Product schema created successfully.")
        except Exception as e:
            print(f"Error setting up Weaviate schema: {e}")

    def add_product(self, name, description, image_b64, product_id):
        if not self.enabled or self.client is None:
            print(f"Weaviate disabled. Skipping vector insert for {product_id}.")
            return

        products = self.client.collections.get("Product")
        products.insert({
            "name": name,
            "description": description,
            "image": image_b64,
            "product_id": product_id
        })

    def search_multimodal(self, text=None, image_b64=None, limit=5):
        if not self.enabled or self.client is None:
            return []

        products = self.client.collections.get("Product")
        
        if image_b64:
            response = products.query.near_image(
                near_image=image_b64,
                limit=limit
            )
        else:
            response = products.query.near_text(
                query=text,
                limit=limit
            )
        
        return [
            {
                "product_id": obj.properties["product_id"],
                "name": obj.properties["name"],
                "description": obj.properties["description"]
            } 
            for obj in response.objects
        ]

# Create instance
vector_service = VectorService()
