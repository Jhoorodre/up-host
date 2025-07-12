import httpx
from pathlib import Path
from typing import Optional, List
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
import base64

from .base import BaseHost
from core.models import UploadResult


class ImgurHost(BaseHost):
    """Imgur.com async implementation"""
    
    API_URL = "https://api.imgur.com/3/"
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.client_id = config.get('client_id', '')
        self.access_token = config.get('access_token', '')
        self.client = httpx.AsyncClient(timeout=300.0)
        
        # Rate limit tracking
        self.user_remaining = None
        self.user_reset = None
        self.client_remaining = None
    
    def _get_headers(self) -> dict:
        """Get appropriate headers based on auth type"""
        if self.access_token:
            return {'Authorization': f'Bearer {self.access_token}'}
        elif self.client_id:
            return {'Authorization': f'Client-ID {self.client_id}'}
        else:
            raise ValueError("Imgur requires client_id or access_token")
    
    def _update_rate_limits(self, headers: dict):
        """Update rate limit info from response headers"""
        try:
            self.user_remaining = int(headers.get('X-RateLimit-UserRemaining', 0))
            self.user_reset = int(headers.get('X-RateLimit-UserReset', 0))
            self.client_remaining = int(headers.get('X-RateLimit-ClientRemaining', 0))
        except (TypeError, ValueError):
            pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=5, max=30)
    )
    async def upload_image(self, filepath: Path) -> UploadResult:
        """Upload image to Imgur"""
        if not filepath.exists():
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error="File not found"
            )
        
        # Check rate limits
        if self.client_remaining is not None and self.client_remaining < 5:
            wait_time = max(10, self.user_reset - asyncio.get_event_loop().time())
            await asyncio.sleep(wait_time)
        
        try:
            # Read and encode image
            with open(filepath, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            response = await self.client.post(
                f"{self.API_URL}image",
                headers=self._get_headers(),
                json={'image': image_data, 'type': 'base64'}
            )
            
            self._update_rate_limits(response.headers)
            
            if response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get('Retry-After', 60))
                await asyncio.sleep(retry_after)
                raise Exception("Rate limited")
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') and data.get('data', {}).get('link'):
                return UploadResult(
                    url=data['data']['link'],
                    filename=filepath.name,
                    success=True
                )
            else:
                error = data.get('data', {}).get('error', 'Unknown error')
                return UploadResult(
                    url="",
                    filename=filepath.name,
                    success=False,
                    error=error
                )
                
        except Exception as e:
            return UploadResult(
                url="",
                filename=filepath.name,
                success=False,
                error=str(e)
            )
    
    async def create_album(self, title: str, description: str, image_ids: List[str]) -> Optional[str]:
        """Create Imgur album (requires auth)"""
        if not self.access_token:
            return None  # Albums require authenticated requests
        
        if not image_ids:
            return None
        
        try:
            response = await self.client.post(
                f"{self.API_URL}album",
                headers=self._get_headers(),
                json={
                    'ids': image_ids,
                    'title': title,
                    'description': description,
                    'privacy': 'hidden'
                }
            )
            
            self._update_rate_limits(response.headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success') and data.get('data', {}).get('id'):
                album_id = data['data']['id']
                return f"https://imgur.com/a/{album_id}"
            
        except Exception:
            pass
        
        return None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()