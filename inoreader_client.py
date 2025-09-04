import aiohttp
import asyncio
import base64
from typing import Dict, List, Optional, Any
from cachetools import TTLCache
from config import Config
import json

class InoreaderClient:
    def __init__(self):
        self.base_url = Config.INOREADER_BASE_URL
        self.app_id = Config.INOREADER_APP_ID
        self.app_key = Config.INOREADER_APP_KEY
        self.username = Config.INOREADER_USERNAME
        self.password = Config.INOREADER_PASSWORD
        self.cache = TTLCache(maxsize=100, ttl=Config.CACHE_TTL)
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        # Create SSL context that doesn't verify certificates (for macOS issues)
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connector with custom SSL context
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        await self._authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def _authenticate(self):
        """Authenticate with Inoreader API"""
        auth_url = 'https://www.inoreader.com/accounts/ClientLogin'
        params = {
            'Email': self.username,
            'Passwd': self.password,
        }
        headers = {
            'AppId': self.app_id,
            'AppKey': self.app_key,
        }
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Authenticating user: {self.username}")
        
        async with self.session.post(auth_url, data=params, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.error(f"Auth failed: {resp.status} - {text}")
                raise Exception(f"Authentication failed: {resp.status} - {text}")
            
            text = await resp.text()
            logger.debug(f"Auth response: {text}")
            
            for line in text.split('\n'):
                if line.startswith('Auth='):
                    self.auth_token = line[5:]
                    logger.info(f"Got auth token: {self.auth_token[:10]}...")
                    break
            
            if not self.auth_token:
                logger.error("No auth token in response")
                raise Exception("No auth token received")
                
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'GoogleLogin auth={self.auth_token}',
            'AppId': self.app_id,
            'AppKey': self.app_key,
        }
        
    async def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Any:
        """Make an API request"""
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        
        timeout = aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)
        
        # Log request details
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Making {method} request to {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Params: {params}")
        
        async with self.session.request(
            method, url, params=params, data=data, headers=headers, timeout=timeout
        ) as resp:
            logger.info(f"Response status: {resp.status}")
            
            if resp.status != 200:
                text = await resp.text()
                logger.error(f"API error response: {text}")
                raise Exception(f"API request failed: {resp.status} - {text}")
            
            # Check if response is JSON
            content_type = resp.headers.get('Content-Type', '')
            logger.debug(f"Response content-type: {content_type}")
            
            if 'application/json' in content_type:
                result = await resp.json()
                logger.debug(f"JSON response keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
                return result
            else:
                text = await resp.text()
                logger.warning(f"Non-JSON response: {text[:200]}")
                return text
                
    async def get_subscription_list(self) -> List[Dict]:
        """Get list of subscribed feeds"""
        cache_key = 'subscription_list'
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        result = await self._request('GET', 'subscription/list')
        subscriptions = result.get('subscriptions', [])
        
        self.cache[cache_key] = subscriptions
        return subscriptions
        
    async def get_stream_contents(self, stream_id: Optional[str] = None, 
                                 count: int = 50, 
                                 exclude_read: bool = True,
                                 newer_than: Optional[int] = None) -> Dict:
        """Get articles from a stream"""
        params = {
            'n': min(count, Config.MAX_ARTICLES_PER_REQUEST),
            'output': 'json'
        }
        
        if exclude_read:
            params['xt'] = 'user/-/state/com.google/read'
            
        if newer_than:
            params['ot'] = newer_than
            
        endpoint = f"stream/contents/{stream_id}" if stream_id else "stream/contents/user/-/state/com.google/reading-list"
        
        result = await self._request('GET', endpoint, params=params)
        
        # Handle string responses (usually errors)
        if isinstance(result, str):
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"API returned string instead of JSON: {result[:500]}")
            
            # Try to parse as JSON if it looks like JSON
            if result.strip().startswith('{'):
                try:
                    import json
                    return json.loads(result)
                except json.JSONDecodeError:
                    pass
            
            # Return empty structure if we can't parse
            return {'items': []}
            
        return result
        
    async def get_stream_item_contents(self, item_ids: List[str]) -> Dict:
        """Get full content for specific items"""
        if not item_ids:
            return {'items': []}
            
        data = {
            'i': item_ids
        }
        
        return await self._request('POST', 'stream/items/contents', data=data)
        
    async def mark_as_read(self, item_ids: List[str]) -> bool:
        """Mark items as read"""
        if not item_ids:
            return True
            
        data = {
            'i': item_ids,
            'a': 'user/-/state/com.google/read'
        }
        
        result = await self._request('POST', 'edit-tag', data=data)
        return result == 'OK'
        
    async def search(self, query: str, count: int = 50, newer_than: Optional[int] = None) -> Dict:
        """Search articles"""
        params = {
            'q': query,
            'n': min(count, Config.MAX_ARTICLES_PER_REQUEST),
            'output': 'json'
        }
        
        if newer_than:
            params['ot'] = newer_than
            
        result = await self._request('GET', 'stream/contents/user/-/state/com.google/search', params=params)
        
        # Handle string responses (usually errors)
        if isinstance(result, str):
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Search API returned string: {result[:500]}")
            
            # Try to parse as JSON if it looks like JSON
            if result.strip().startswith('{'):
                try:
                    import json
                    return json.loads(result)
                except json.JSONDecodeError:
                    pass
            
            # Return empty structure if we can't parse
            return {'items': []}
            
        return result
        
    async def get_unread_count(self) -> Dict:
        """Get unread counts for all feeds"""
        result = await self._request('GET', 'unread-count')
        return result.get('unreadcounts', [])