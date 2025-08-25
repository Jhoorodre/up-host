"""
JSON updater for manga metadata
Handles merging new chapters with existing JSON files
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger


class JSONUpdater:
    """Handles updating existing manga JSON files"""
    
    @staticmethod
    def load_existing_json(json_path: Path) -> Optional[Dict[str, Any]]:
        """Load existing JSON file if it exists"""
        if not json_path.exists():
            return None
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading existing JSON {json_path}: {e}")
            return None
    
    @staticmethod
    def merge_metadata(existing: Dict[str, Any], new_data: Dict[str, Any], mode: str = "add") -> Dict[str, Any]:
        """
        Merge new chapter data with existing JSON
        
        Args:
            existing: Existing JSON data
            new_data: New chapter data to merge
            mode: "add" (append new), "replace" (overwrite existing), "smart" (intelligent merge)
        
        Returns:
            Merged JSON data
        """
        # Start with existing data
        merged = existing.copy()
        
        # Update basic metadata (title, description, etc.)
        for key in ['title', 'description', 'artist', 'author', 'cover', 'status']:
            if key in new_data and new_data[key]:
                merged[key] = new_data[key]
        
        # Handle chapters based on mode
        existing_chapters = existing.get('chapters', {})
        new_chapters = new_data.get('chapters', {})
        
        if mode == "replace":
            # Replace all chapters with new ones
            merged['chapters'] = new_chapters
            logger.info(f"Replaced all chapters with {len(new_chapters)} new chapters")
            
        elif mode == "add":
            # Add new chapters, keep existing ones
            # Find the next available index
            max_index = JSONUpdater._get_max_chapter_index(existing_chapters)
            
            for new_key, new_chapter in new_chapters.items():
                # Check if chapter already exists by title
                existing_key = JSONUpdater._find_chapter_by_title(existing_chapters, new_chapter['title'])
                
                if existing_key:
                    # Chapter exists, update it
                    existing_chapters[existing_key] = new_chapter
                    logger.info(f"Updated existing chapter: {new_chapter['title']}")
                else:
                    # New chapter, add with next index
                    max_index += 1
                    new_index = f"{max_index:03d}"
                    existing_chapters[new_index] = new_chapter
                    logger.info(f"Added new chapter at index {new_index}: {new_chapter['title']}")
            
            merged['chapters'] = existing_chapters
            
        elif mode == "smart":
            # Intelligent merge: update existing, add new, preserve order
            merged_chapters = existing_chapters.copy()
            
            for new_key, new_chapter in new_chapters.items():
                existing_key = JSONUpdater._find_chapter_by_title(merged_chapters, new_chapter['title'])
                
                if existing_key:
                    # Update existing chapter but preserve index
                    merged_chapters[existing_key] = new_chapter
                    logger.info(f"Smart update: {new_chapter['title']} at {existing_key}")
                else:
                    # Find appropriate index for new chapter
                    best_index = JSONUpdater._find_best_index(merged_chapters, new_chapter['title'])
                    merged_chapters[best_index] = new_chapter
                    logger.info(f"Smart add: {new_chapter['title']} at {best_index}")
            
            merged['chapters'] = merged_chapters
        
        logger.info(f"Merge completed: {len(merged['chapters'])} total chapters")
        return merged
    
    @staticmethod
    def _get_max_chapter_index(chapters: Dict[str, Any]) -> int:
        """Get the highest chapter index number"""
        max_index = -1
        for key in chapters.keys():
            try:
                index = int(key)
                max_index = max(max_index, index)
            except ValueError:
                continue
        return max_index
    
    @staticmethod
    def _find_chapter_by_title(chapters: Dict[str, Any], title: str) -> Optional[str]:
        """Find existing chapter by title"""
        for key, chapter in chapters.items():
            if chapter.get('title', '').strip() == title.strip():
                return key
        return None
    
    @staticmethod
    def _find_best_index(chapters: Dict[str, Any], title: str) -> str:
        """Find the best index for a new chapter based on title"""
        # Simple implementation: use next available index
        max_index = JSONUpdater._get_max_chapter_index(chapters)
        return f"{max_index + 1:03d}"
    
    @staticmethod
    def clean_corrupted_json(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean corrupted JSON by removing "group" field from root level
        Groups should only exist in chapters structure
        """
        cleaned_data = data.copy()
        
        # Remove "group" from root level if it exists
        if "group" in cleaned_data:
            logger.warning("DETECTED AND REMOVING corrupted 'group' field from JSON root level!")
            logger.warning(f"Corrupted group value was: '{cleaned_data['group']}'")
            del cleaned_data["group"]
            logger.success("JSON corruption cleaned - 'group' field removed from root level")
        
        return cleaned_data

    @staticmethod
    def save_json(data: Dict[str, Any], output_path: Path) -> bool:
        """Save JSON data to file"""
        try:
            # Clean any corruption before saving
            clean_data = JSONUpdater.clean_corrupted_json(data)
            # Create backup of existing file if it exists
            if output_path.exists():
                import time
                timestamp = int(time.time())
                backup_path = output_path.with_suffix(f'.json.backup.{timestamp}')
                
                # Remove old backup if exists (keep only latest)
                old_backup = output_path.with_suffix('.json.backup')
                if old_backup.exists():
                    try:
                        old_backup.unlink()
                        logger.debug(f"Removed old backup: {old_backup}")
                    except Exception as e:
                        logger.debug(f"Could not remove old backup: {e}")
                
                output_path.rename(backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, indent=2, ensure_ascii=False)
            
            logger.success(f"JSON saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving JSON {output_path}: {e}")
            return False