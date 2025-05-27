from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """Initialize the embedding generator"""
        try:
            logger.info(f"Loading model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not texts:
            logger.warning("No texts provided for embedding generation")
            return []
            
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(texts, convert_to_tensor=False).tolist()
            logger.info("Embeddings generated successfully")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            return []

class VectorDB:
    def __init__(self, host: str, port: int):
        """Initialize Qdrant client"""
        try:
            logger.info(f"Connecting to Qdrant at {host}:{port}")
            self.client = QdrantClient(host=host, port=port)
            logger.info("Qdrant connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise

    def initialize_collection(self, collection_name: str, vector_size: int = 384):
        """Initialize Qdrant collection"""
        try:
            logger.info(f"Initializing collection: {collection_name}")
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection {collection_name} initialized")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {str(e)}")
            raise

    def upsert_embeddings(self, collection_name: str, points: List[Dict]):
        """Upsert embeddings into Qdrant"""
        if not points:
            logger.warning("No points to upsert")
            return
            
        try:
            logger.info(f"Upserting {len(points)} points to {collection_name}")
            
            # Prepare points for Qdrant
            qdrant_points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=point['vector'],
                    payload={
                        'text': point['text'],
                        'legislation_id': point['legislation_id'],
                        'chunk_number': point['chunk_number'],
                        'source_url': point['source_url']
                    }
                )
                for point in points
            ]
            
            # Batch upsert
            self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points,
                wait=True
            )
            logger.info(f"Successfully upserted {len(points)} embeddings")
            
        except Exception as e:
            logger.error(f"Failed to upsert embeddings: {str(e)}")
            raise

    def search_similar(self, collection_name: str, query_embedding: List[float], limit: int = 4):
        """Search for similar vectors"""
        try:
            return self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to search similar vectors: {str(e)}")
            return []