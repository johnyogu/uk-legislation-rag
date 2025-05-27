from setuptools import setup, find_packages

setup(
    name="uk_legislation_pipeline",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.12.2",
        "requests>=2.31.0",
        "psycopg2-binary>=2.9.9",
        "lxml>=4.9.4",
        "sentence-transformers>=2.2.2",
        "qdrant-client>=1.1.1",
        "click>=8.1.3",
        "python-dotenv>=0.21.0",
        "torch>=2.0.0",
        "tqdm>=4.64.1",
        "transformers>=4.26.0"
    ],
    python_requires=">=3.9",
)