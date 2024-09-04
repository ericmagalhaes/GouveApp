import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys and other sensitive information
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'default-openai-api-key')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'text-embedding-3-small')

# Qdrant client settings
QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', '6333'))

# Qdrant collection name
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'cacao_show_collection')

# Server settings
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8000'))
