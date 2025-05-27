# UK Legislation ETL Pipeline for Retrieval Augmented Generation (RAG)

This project implements an ETL pipeline that processes UK legislation data from [legislation.gov.uk](https://www.legislation.gov.uk) for use in Retrieval Augmented Generation applications.

## Features

- Downloads legislation for specified time periods and categories
- Cleans and processes legal texts (removes images, watermarks, non-essential annotations)
- Extracts and stores metadata in PostgreSQL
- Generates embeddings using sentence-transformers/all-MiniLM-L6-v2
- Stores embeddings in Qdrant vector database
- Provides CLI for semantic search queries

## System Architecture

┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ │ │ │ │ │
│ Pipeline │──▶│ PostgreSQL │──▶│ Qdrant │
│ │ │ │ │ │
└─────────────┘ └─────────────┘ └─────────────┘



## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 24GB RAM recommended
- 10GB disk space for data cache

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/uk-legislation-rag.git
   cd uk-legislation-rag



2. Build and start the containers:

   docker-compose up -d


Configuration
Configure via environment variables:

Variable	Description	Default
LEGISLATION_CATEGORY	Legislation category to download	planning
START_DATE	Start date (YYYY-MM-DD)	2024-08-01
END_DATE	End date (YYYY-MM-DD)	2024-08-31
POSTGRES_*	PostgreSQL connection settings	See docker-compose.yml
QDRANT_*	Qdrant connection settings	See docker-compose.yml
Usage
Running the Pipeline

3. docker-compose run pipeline python -m pipeline.main

4. Querying the Data

docker-compose run pipeline python -m pipeline.query "your search query here"

Example:

docker-compose run pipeline python pipeline/query.py "liability to a high income child benefit charge"


5. Direct Script Execution
Alternatively, you can run scripts directly:

docker-compose run pipeline python pipeline/query.py "your query"


6. Port Configuration
The following ports are exposed:

Service	Port	Protocol	Purpose
PostgreSQL	5432	TCP	Database access
Qdrant	6333	gRPC	Vector DB gRPC interface
Qdrant	6334	HTTP	Vector DB HTTP interface


7. Viewing Logs
docker-compose logs -f pipeline