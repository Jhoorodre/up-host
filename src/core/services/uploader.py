import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import json
from loguru import logger

from core.models import Manga, Chapter, ChapterUploadResult
from core.hosts import BaseHost, CatboxHost
from utils.helpers import sanitize_filename
from utils.json_updater import JSONUpdater


class MangaUploaderService:
    """Main service for handling manga uploads"""
    
    def __init__(self):
        self.hosts: Dict[str, BaseHost] = {}
        self.current_host: Optional[BaseHost] = None
        logger.info("MangaUploaderService initialized")
    
    def register_host(self, name: str, host: BaseHost):
        """Register a new host service"""
        self.hosts[name] = host
        logger.info(f"Registered host: {name}")
    
    def set_host(self, name: str) -> bool:
        """Set the active host for uploads"""
        if name in self.hosts:
            self.current_host = self.hosts[name]
            logger.info(f"Active host set to: {name}")
            return True
        logger.error(f"Host not found: {name}")
        return False
    
    async def upload_manga(self, manga: Manga, chapters: List[Chapter]) -> Dict[str, ChapterUploadResult]:
        """Upload selected chapters of a manga"""
        if not self.current_host:
            raise ValueError("No host selected")
        
        results = {}
        
        for chapter in chapters:
            logger.info(f"Processing chapter: {chapter.name}")
            
            # Get images for the chapter
            images = chapter.images
            if not images:
                logger.warning(f"No images found in chapter: {chapter.name}")
                continue
            
            # Upload chapter
            result = await self.current_host.upload_chapter(
                chapter_name=chapter.name,
                images=images
            )
            
            results[chapter.name] = result
            
            if result.success:
                logger.success(f"Chapter uploaded successfully: {chapter.name}")
            else:
                logger.error(f"Failed uploads in chapter {chapter.name}: {result.failed_uploads}")
        
        return results
    
    async def generate_metadata(self, manga: Manga, upload_results: Dict[str, ChapterUploadResult], 
                              output_path: Path, update_mode: str = "add", custom_metadata: Dict = None) -> Path:
        """
        Generate JSON metadata for uploaded manga with merge support
        
        Args:
            manga: Manga object
            upload_results: Upload results for chapters
            output_path: Path for output JSON
            update_mode: "add" (append new), "replace" (overwrite), "smart" (intelligent merge)
        """
        # Create sanitized filename
        sanitized_title = sanitize_filename(manga.title, is_file=True, remove_accents=True)
        if not sanitized_title.endswith('.json'):
            sanitized_title += '.json'
        
        # Update output path with sanitized name
        final_output_path = output_path.parent / sanitized_title
        
        # Prepare new chapter data
        new_chapters_data = {}
        sorted_chapters = sorted(upload_results.items(), key=lambda x: x[0])
        
        for idx, (chapter_name, result) in enumerate(sorted_chapters):
            new_chapters_data[f"{idx:03d}"] = {
                "title": chapter_name,
                "volume": "",
                "last_updated": str(int(asyncio.get_event_loop().time())),
                "groups": {
                    "default": result.image_urls  # Use individual URLs, not album
                }
            }
        
        # Use custom metadata if provided, otherwise use manga defaults
        if custom_metadata:
            new_metadata = {
                "title": custom_metadata.get("title", manga.title),
                "description": custom_metadata.get("description", manga.description),
                "artist": custom_metadata.get("artist", manga.artist),
                "author": custom_metadata.get("author", manga.author),
                "group": custom_metadata.get("group", ""),
                "cover": custom_metadata.get("cover", manga.cover_url),
                "status": custom_metadata.get("status", manga.status.value),
                "chapters": new_chapters_data
            }
        else:
            new_metadata = {
                "title": manga.title,
                "description": manga.description,
                "artist": manga.artist,
                "author": manga.author,
                "group": "",
                "cover": manga.cover_url,
                "status": manga.status.value,
                "chapters": new_chapters_data
            }
        
        # Load existing JSON if it exists
        existing_data = JSONUpdater.load_existing_json(final_output_path)
        
        if existing_data:
            logger.info(f"Found existing JSON with {len(existing_data.get('chapters', {}))} chapters")
            
            # Merge with existing data
            merged_data = JSONUpdater.merge_metadata(existing_data, new_metadata, update_mode)
            
            logger.info(f"Merge mode: {update_mode}")
            logger.info(f"Final JSON will have {len(merged_data.get('chapters', {}))} chapters")
        else:
            logger.info("No existing JSON found, creating new file")
            merged_data = new_metadata
        
        # Save the merged JSON
        success = JSONUpdater.save_json(merged_data, final_output_path)
        
        if success:
            logger.success(f"Metadata saved to: {final_output_path}")
            return final_output_path
        else:
            raise Exception(f"Failed to save JSON to {final_output_path}")