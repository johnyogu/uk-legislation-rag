import logging
from datetime import datetime
import os
from .extract import LegislationExtractor
from .transform import LegislationTransformer
from .load import DatabaseLoader
from .embed import EmbeddingGenerator, VectorDB
from .database import get_legislation_chunks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline():
    
    # Configuration
    category = os.getenv('LEGISLATION_CATEGORY', 'planning')
    start_date = datetime.strptime(os.getenv('START_DATE', '2024-08-01'), '%Y-%m-%d')
    end_date = datetime.strptime(os.getenv('END_DATE', '2024-08-31'), '%Y-%m-%d')
    
    # Initialize components
    extractor = LegislationExtractor(category, start_date, end_date)
    transformer = LegislationTransformer()
    
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'postgres'),
        'port': os.getenv('POSTGRES_PORT', 5432),
        'user': os.getenv('POSTGRES_USER', 'legislation'),
        'password': os.getenv('POSTGRES_PASSWORD', 'legislation'),
        'dbname': os.getenv('POSTGRES_DB', 'legislation')
    }
    
    # Initialize databases
    with DatabaseLoader(db_config) as db_loader:
        db_loader.initialize_database()
        
        # Step 1: Extract legislation
        logger.info("Fetching legislation list...")
        legislation_list = extractor.fetch_legislation_list()
        logger.info(f"Found {len(legislation_list)} legislation items")
        
        # Step 2: Process each legislation
        for legislation_item in legislation_list:
            logger.info(f"Processing: {legislation_item['title']}")
            
            try:
                # Extract full text
                legislation_data = extractor.fetch_legislation_text(legislation_item['url'])
                legislation_item.update(legislation_data['metadata'])
                
                # Transform text
                cleaned_text = transformer.clean_text(legislation_data['text'])
                chunks = transformer.split_into_chunks(cleaned_text)
                
                # Load to database
                legislation_id = db_loader.save_legislation(legislation_item)
                db_loader.save_chunks(legislation_id, chunks)
                
            except Exception as e:
                logger.error(f"Failed to process {legislation_item['title']}: {str(e)}")
                continue
    
    # Step 3: Generate embeddings
    logger.info("Generating embeddings...")
    embedding_generator = EmbeddingGenerator()
    vector_db = VectorDB(
        host=os.getenv('QDRANT_HOST', 'qdrant'),
        port=int(os.getenv('QDRANT_PORT', 6333)))
    
    vector_db.initialize_collection("legislation")
    
    chunks = get_legislation_chunks(db_config)
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedding_generator.generate_embeddings(texts)
    
    # Prepare points for vector DB
    points = []
    for chunk, embedding in zip(chunks, embeddings):
        points.append({
            'vector': embedding,
            'text': chunk['text'],
            'legislation_id': chunk['legislation_id'],
            'chunk_number': chunk['chunk_number'],
            'source_url': chunk['source_url']
        })
    
    # Store embeddings
    vector_db.upsert_embeddings("legislation", points)
    logger.info("Pipeline completed successfully!")

if __name__ == '__main__':
    run_pipeline()