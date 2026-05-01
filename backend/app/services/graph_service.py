import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import time

load_dotenv()

class GraphService:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        self.enabled = False

        for i in range(5):
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                self.driver.verify_connectivity()
                self.enabled = True
                print("Successfully connected to Neo4j!")
                break
            except Exception as e:
                print(f"Neo4j connection attempt {i+1} failed. Retrying in 5s... Error: {e}")
                time.sleep(5)

        if not self.enabled:
            print("Neo4j is unavailable. Graph features will run in disabled mode.")

    def close(self):
        if self.driver:
            self.driver.close()

    def add_product_node(self, product_id, name, description, category, brand):
        if not self.enabled or self.driver is None:
            print(f"Neo4j disabled. Skipping graph insert for {product_id}.")
            return

        with self.driver.session() as session:
            session.execute_write(self._create_product_tx, product_id, name, description, category, brand)

    @staticmethod
    def _create_product_tx(tx, product_id, name, description, category, brand):
        query = (
            "MERGE (p:Product {id: $product_id}) "
            "SET p.name = $name, p.description = $description "
            "MERGE (c:Category {name: $category}) "
            "MERGE (b:Brand {name: $brand}) "
            "MERGE (p)-[:BELONGS_TO]->(c) "
            "MERGE (p)-[:MANUFACTURED_BY]->(b) "
            "RETURN p"
        )
        tx.run(
            query,
            product_id=product_id,
            name=name,
            description=description,
            category=category,
            brand=brand,
        )

    def add_review(self, product_id, review_id, content, sentiment):
        if not self.enabled or self.driver is None:
            return

        with self.driver.session() as session:
            session.execute_write(self._create_review_tx, product_id, review_id, content, sentiment)

    @staticmethod
    def _create_review_tx(tx, product_id, review_id, content, sentiment):
        query = (
            "MATCH (p:Product {id: $product_id}) "
            "MERGE (r:Review {id: $review_id}) "
            "SET r.content = $content, r.sentiment = $sentiment "
            "MERGE (r)-[:REVIEWS]->(p) "
            "RETURN r"
        )
        tx.run(query, product_id=product_id, review_id=review_id, content=content, sentiment=sentiment)

    def get_related_context(self, product_id):
        """Retrieves graph context for a product: category, brand, and reviews."""
        if not self.enabled or self.driver is None:
            return None

        with self.driver.session() as session:
            result = session.execute_read(self._get_context_tx, product_id)
            return result

    def search_products(self, query_text, limit=5):
        if not self.enabled or self.driver is None:
            return []

        with self.driver.session() as session:
            return session.execute_read(self._search_products_tx, query_text or "", limit)

    @staticmethod
    def _get_context_tx(tx, product_id):
        query = (
            "MATCH (p:Product {id: $product_id}) "
            "OPTIONAL MATCH (p)-[:BELONGS_TO]->(c:Category) "
            "OPTIONAL MATCH (p)-[:MANUFACTURED_BY]->(b:Brand) "
            "OPTIONAL MATCH (r:Review)-[:REVIEWS]->(p) "
            "RETURN c.name as category, b.name as brand, collect(r.content)[..3] as reviews"
        )
        record = tx.run(query, product_id=product_id).single()
        if record:
            return {
                "category": record["category"],
                "brand": record["brand"],
                "reviews": record["reviews"]
            }
        return None

    @staticmethod
    def _search_products_tx(tx, query_text, limit):
        # Split query into words to make it more fuzzy/keyword-based
        words = [w.lower() for w in query_text.split() if len(w) > 2]
        if not words and query_text:
            words = [query_text.lower()]
            
        query = (
            "MATCH (p:Product) "
            "OPTIONAL MATCH (p)-[:BELONGS_TO]->(c:Category) "
            "OPTIONAL MATCH (p)-[:MANUFACTURED_BY]->(b:Brand) "
            "WITH p, c, b, $words AS keywords "
            "WHERE size(keywords) = 0 "
            "   OR any(word IN keywords WHERE toLower(p.name) CONTAINS word) "
            "   OR any(word IN keywords WHERE toLower(coalesce(p.description, '')) CONTAINS word) "
            "   OR any(word IN keywords WHERE toLower(coalesce(c.name, '')) CONTAINS word) "
            "   OR any(word IN keywords WHERE toLower(coalesce(b.name, '')) CONTAINS word) "
            "RETURN p.id AS product_id, p.name AS name, coalesce(p.description, '') AS description "
            "LIMIT $limit"
        )
        result = tx.run(query, words=words, limit=limit)
        return [record.data() for record in result]

graph_service = GraphService()
