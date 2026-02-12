"""Configuration management for the AI Research Assistant"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def get_config(key, default=None):
    """Get config from environment or streamlit secrets"""
    # 1. Check OS Environment (Local/Docker)
    val = os.getenv(key)
    if val:
        return val
    
    # 2. Check Streamlit Secrets (Cloud)
    try:
        import streamlit as st
        # st.secrets behaves like a nested dict
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
        
    return default

class Config:
    """Application configuration"""
    
    # API Keys
    GROQ_API_KEY = get_config("GROQ_API_KEY")
    OPENAI_API_KEY = get_config("OPENAI_API_KEY")  # Optional, for embeddings only
    TAVILY_API_KEY = get_config("TAVILY_API_KEY")
    QDRANT_URL = get_config("QDRANT_URL") # Optional, defaults to local path
    QDRANT_API_KEY = get_config("QDRANT_API_KEY") # For Qdrant Cloud

    # LLM Provider (groq or openai)
    LLM_PROVIDER = get_config("LLM_PROVIDER", "groq")
    print(f"LLM_PROVIDER: {LLM_PROVIDER}")
    
    # Groq Settings
    GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast and capable
    CHUNKING_LLM_MODEL = "llama-3.1-8b-instant"  # Smaller, faster model for chunking
    # Alternative models: "mixtral-8x7b-32768", "llama-3.1-8b-instant"

    # Embedding Settings
    # Options: "local" (free), "openai" (premium)
    # If using openai, make sure to set OPENAI_API_KEY in .env file as well as EMBEDDING_PROVIDER = "openai"
    EMBEDDING_PROVIDER = get_config("EMBEDDING_PROVIDER", "local")
    print(f"EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER}")
  
    
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
    LOCAL_EMBEDDING_MODEL = "multi-qa-distilbert-cos-v1"
    
    # Active model selection
    EMBEDDING_MODEL = OPENAI_EMBEDDING_MODEL if EMBEDDING_PROVIDER == "openai" else LOCAL_EMBEDDING_MODEL
    print(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
    
    # Vector size must match the model
    # all-MiniLM-L6-v2: 384, text-embedding-3-small: 1536
    VECTOR_SIZE = 1536 if EMBEDDING_PROVIDER == "openai" else 768
    print(f"VECTOR_SIZE: {VECTOR_SIZE}")


    
    # General LLM Settings
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    
    # RAG Settings
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 5
    # if USE_INTELLIGENT_CHUNKING is True, make sure to set CHUNKING_LLM_MODEL in .env file as well
    USE_INTELLIGENT_CHUNKING = str(get_config("USE_INTELLIGENT_CHUNKING", "False")).lower() == "true"


    print(f"USE_INTELLIGENT_CHUNKING: {USE_INTELLIGENT_CHUNKING}")
    
    COLLECTION_NAME = "research_documents"
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"

    # Qdrant Settings
    QDRANT_TIMEOUT = 60
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        elif cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Create necessary directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)


# Validate on import
Config.validate()





