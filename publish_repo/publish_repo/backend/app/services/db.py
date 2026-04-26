import os
import logging

class WeaviateGraphDB:
    def __init__(self):
        self.enabled = False
        self.client = None
        try:
            import weaviate
            import weaviate.classes as wvc
            # Connects to the local Weaviate Docker container
            weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
            host = "weaviate" if os.getenv("WEAVIATE_URL") else "localhost"
            
            self.client = weaviate.connect_to_local(host=host)
            self.enabled = True
            print(f"Connected to Weaviate at {host}")
        except Exception as e:
            logging.error(f"Could not connect to Weaviate: {e}. Running in Mock Mode.")

    def create_schema(self):
        """Defines the schema with Graph-like cross-references."""
        if not self.enabled:
            return
            
        try:
            import weaviate.classes as wvc
            if not self.client.collections.exists("MultimodalNode"):
                self.client.collections.create(
                    name="MultimodalNode",
                    properties=[
                        wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="modality", data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="source_file", data_type=wvc.config.DataType.TEXT),
                    ],
                    vectorizer_config=wvc.config.Configure.Vectorizer.none(), 
                )
        except Exception as e:
            logging.error(f"Error creating schema: {e}")

    def insert_node(self, content: str, modality: str, source: str, vector: list):
        """Inserts a chunk and its embedding into the database."""
        if not self.enabled:
            print(f"[MOCK DB] Inserted {modality} node from {source}")
            return "mock-uuid"
            
        collection = self.client.collections.get("MultimodalNode")
        uuid = collection.data.insert(
            properties={"content": content, "modality": modality, "source_file": source},
            vector=vector
        )
        return uuid

    def retrieve_top_k(self, query_vector: list, top_k: int = 3):
        """Performs vector search to find the most relevant context."""
        if not self.enabled:
            print("[MOCK DB] Retrieving top-k chunks (Empty response)")
            return []
            
        collection = self.client.collections.get("MultimodalNode")
        results = collection.query.near_vector(
            near_vector=query_vector,
            limit=top_k,
            return_properties=["content", "modality", "source_file"]
        )
        return results.objects
