import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    INOREADER_APP_ID = os.getenv('INOREADER_APP_ID')
    INOREADER_APP_KEY = os.getenv('INOREADER_APP_KEY')
    INOREADER_USERNAME = os.getenv('INOREADER_USERNAME')
    INOREADER_PASSWORD = os.getenv('INOREADER_PASSWORD')
    
    # API Base URL
    INOREADER_BASE_URL = 'https://www.inoreader.com/reader/api/0'
    
    # Cache settings
    CACHE_TTL = 300  # 5 minutes
    
    # Request settings
    REQUEST_TIMEOUT = 10
    MAX_ARTICLES_PER_REQUEST = 50
    
    @classmethod
    def validate(cls):
        required = ['INOREADER_APP_ID', 'INOREADER_APP_KEY', 'INOREADER_USERNAME', 'INOREADER_PASSWORD']
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return True