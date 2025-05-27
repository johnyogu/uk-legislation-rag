import click
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

@click.command()
@click.argument('query_text')
def query_legislation(query_text: str):
    """Query the legislation database for semantically similar content"""
    # Initialize components
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    qdrant = QdrantClient(
        host=os.getenv('QDRANT_HOST', 'localhost'),
        port=int(os.getenv('QDRANT_PORT', 6333)))
    
    # Generate embedding for query
    query_embedding = model.encode(query_text, convert_to_tensor=False).tolist()
    
    # Search vector DB
    results = qdrant.search(
        collection_name="legislation",
        query_vector=query_embedding,
        limit=4
    )
    
    # Display results
    for i, result in enumerate(results, 1):
        click.echo(f"\nResult {i} (Score: {result.score:.4f}):")
        click.echo(f"Source: {result.payload['source_url']}")
        click.echo(f"Chunk #{result.payload['chunk_number']}")
        click.echo("=" * 50)
        click.echo(result.payload['text'])
        click.echo("=" * 50)

if __name__ == '__main__':
    query_legislation()