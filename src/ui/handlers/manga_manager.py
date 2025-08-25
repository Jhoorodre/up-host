"""Manga and chapter management handler for UI backend"""

import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Any
from PySide6.QtCore import QObject, Signal, Property, Slot
from core.config import ConfigManager
from core.models import Manga, Chapter
from core.services.uploader import MangaUploaderService
from ui.models import MangaListModel, ChapterListModel
from utils.helpers import sanitize_filename
from loguru import logger


class MangaManager(QObject):
    """Handles all manga and chapter-related operations"""
    
    mangaListChanged = Signal()
    chapterListChanged = Signal()
    mangaInfoChanged = Signal('QVariant')  # CRITICAL: Add mangaInfoChanged signal
    uploadProgressChanged = Signal(str, int)
    uploadCompleted = Signal(str)
    uploadFailed = Signal(str, str)
    
    def __init__(self, config_manager: ConfigManager, uploader_service: MangaUploaderService):
        super().__init__()
        self.config_manager = config_manager
        self.uploader_service = uploader_service
        
        # Models for QML
        self.manga_model = MangaListModel(self)
        self.chapter_model = ChapterListModel(self)
        
        # Current selections
        self.current_manga: Optional[Manga] = None
        self.selected_chapters: List[Chapter] = []
        
        # Connect uploader signals
        self._connect_uploader_signals()
    
    # Properties for QML
    @Property(QObject, notify=mangaListChanged)
    def mangaModel(self):
        return self.manga_model
    
    @Property(QObject, notify=chapterListChanged)
    def chapterModel(self):
        return self.chapter_model
    
    @Property(str, notify=chapterListChanged)
    def selectedMangaTitle(self):
        return self.current_manga.title if self.current_manga else ""
    
    @Property(str, notify=chapterListChanged)
    def selectedMangaCover(self):
        return self.current_manga.cover_url if self.current_manga else ""
    
    @Property(str, notify=chapterListChanged)
    def selectedMangaDescription(self):
        return self.current_manga.description if self.current_manga else ""
    
    def _connect_uploader_signals(self):
        """Connect uploader service signals to local signals"""
        # TODO: Connect actual uploader signals when they exist
        pass
    
    @Slot(str)
    @Slot()
    def refresh_manga_list(self):
        """Refresh the manga list from root folder"""
        try:
            root_folder = Path(self.config_manager.config.root_folder)
            if not root_folder.exists():
                logger.warning(f"Root folder does not exist: {root_folder}")
                return
            
            mangas = []
            for manga_dir in root_folder.iterdir():
                if manga_dir.is_dir() and not manga_dir.name.startswith('.'):
                    # Count chapters (subdirectories with images)
                    chapter_count = 0
                    for chapter_dir in manga_dir.iterdir():
                        if chapter_dir.is_dir():
                            # Check if directory contains images
                            has_images = any(
                                f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']
                                for f in chapter_dir.iterdir()
                                if f.is_file()
                            )
                            if has_images:
                                chapter_count += 1
                    
                    # Create manga object
                    manga = Manga(
                        title=manga_dir.name,
                        path=manga_dir,
                        cover_url="",  # Will be loaded from metadata
                        description=""  # Will be loaded from metadata
                    )
                    # Add chapter count as custom attribute
                    manga._chapter_count = chapter_count
                    mangas.append(manga)
            
            # Sort by title
            mangas.sort(key=lambda m: m.title.lower())
            
            # Convert to the expected format for the model
            manga_entries = []
            for manga in mangas:
                # Try to load cover from JSON metadata using comprehensive search
                cover_url = self._load_manga_cover(manga)
                
                manga_entry = {
                    'title': manga.title,
                    'path': str(manga.path),
                    'chapterCount': getattr(manga, '_chapter_count', 0),
                    'coverUrl': cover_url
                }
                manga_entries.append(manga_entry)
            
            # Update model
            self.manga_model.setMangas(manga_entries)
            self.mangaListChanged.emit()
            
            logger.info(f"Loaded {len(mangas)} manga titles")
            
        except Exception as e:
            logger.error(f"Error refreshing manga list: {e}")
    
    @Slot(str)
    def select_manga(self, manga_title: str):
        """Select a manga and load its chapters"""
        try:
            # Find manga in current list - FIXED: use _mangas instead of mangas
            manga = None
            for manga_entry in self.manga_model._mangas:
                if manga_entry.get('title') == manga_title:
                    # Create manga object from entry
                    from pathlib import Path
                    manga = Manga(
                        title=manga_entry['title'],
                        path=Path(manga_entry['path']),
                        cover_url=manga_entry.get('coverUrl', ''),
                        description=''  # Will be loaded in _load_manga_info
                    )
                    break
            
            if not manga:
                logger.warning(f"Manga not found: {manga_title}")
                return
            
            self.current_manga = manga
            self._load_chapters()
            
            # Load comprehensive manga info and emit signal
            chapter_count = len(getattr(manga, 'chapters', [])) or self.chapter_model.rowCount()
            manga_info = self._load_manga_info(manga_title, chapter_count)
            
            if manga_info:
                # Emit signal with loaded manga info
                self.mangaInfoChanged.emit(manga_info)
                logger.debug(f"Emitted mangaInfoChanged signal for {manga_title}")
            
        except Exception as e:
            logger.error(f"Error selecting manga: {e}")
    
    def _load_chapters(self):
        """Load chapters for current manga"""
        if not self.current_manga:
            return
        
        try:
            chapters = []
            manga_path = Path(self.current_manga.path)
            
            for chapter_dir in manga_path.iterdir():
                if chapter_dir.is_dir() and not chapter_dir.name.startswith('.'):
                    # Get image files
                    image_files = [
                        f for f in chapter_dir.iterdir()
                        if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']
                    ]
                    
                    if image_files:
                        # Sort images numerically
                        image_files.sort(key=lambda x: (len(x.stem), x.stem))
                        
                        chapter = Chapter(
                            name=chapter_dir.name,
                            path=chapter_dir,
                            images=image_files
                        )
                        # Add custom attributes
                        chapter._image_count = len(image_files)
                        chapter._is_uploaded = False  # TODO: Check if already uploaded
                        chapters.append(chapter)
            
            # Sort chapters
            chapters.sort(key=lambda c: self._natural_sort_key(c.name))
            
            # Convert to the expected format for the model
            chapter_entries = []
            for chapter in chapters:
                chapter_entry = {
                    'name': chapter.name,
                    'path': str(chapter.path),
                    'imageCount': getattr(chapter, '_image_count', 0),
                    'selected': False
                }
                chapter_entries.append(chapter_entry)
            
            # Update model
            self.chapter_model.setChapters(chapter_entries)
            self.chapterListChanged.emit()
            
            logger.debug(f"Loaded {len(chapters)} chapters for {self.current_manga.title}")
            
        except Exception as e:
            logger.error(f"Error loading chapters: {e}")
    
    def _natural_sort_key(self, text: str):
        """Generate natural sorting key for chapter names"""
        import re
        parts = re.split(r'(\d+)', text.lower())
        return [int(part) if part.isdigit() else part for part in parts]
    
    def _load_manga_info(self, manga_title: str, folder_chapter_count: int):
        """Load manga information from JSON file if it exists - COMPREHENSIVE VERSION FROM ORIGINAL"""
        try:
            output_folder = Path(self.config_manager.config.output_folder)
            manga_folder = output_folder / manga_title
            
            # Try multiple approaches to find JSON file - EXACT LOGIC FROM ORIGINAL
            json_file = None
            
            # 0. First try in root folder (same directory as manga folder)
            root_folder = Path(self.config_manager.config.root_folder)
            sanitized_title = sanitize_filename(manga_title, is_file=False, remove_accents=True)
            root_json = root_folder / f"{sanitized_title}.json"
            if root_json.exists():
                json_file = root_json
                logger.debug(f"Found JSON method 0 (root) for _load_manga_info {manga_title}: {json_file.name}")
            
            # 0.1. Also try glob search in root folder
            if not json_file:
                for file in root_folder.glob("*.json"):
                    if sanitize_filename(manga_title, is_file=False, remove_accents=True) == sanitize_filename(file.stem, is_file=True, remove_accents=True):
                        json_file = file
                        logger.debug(f"Found JSON method 0.1 (root glob) for _load_manga_info {manga_title}: {json_file.name}")
                        break
            
            # 1. Try with sanitized filename in output folder
            if not json_file:
                potential_json = manga_folder / f"{sanitized_title}.json"
                if potential_json.exists():
                    json_file = potential_json
            
            # 2. If not found, try looking for any .json file in the folder
            if not json_file and manga_folder.exists():
                for file in manga_folder.glob("*.json"):
                    json_file = file
                    break
            
            # 2.5. If manga folder doesn't exist, try to find similar named folders
            if not json_file and not manga_folder.exists():
                if output_folder.exists():
                    # Look for folders with similar names
                    manga_name_words = manga_title.lower().split()
                    for folder in output_folder.iterdir():
                        if folder.is_dir():
                            folder_name_words = folder.name.lower().split()
                            # Check if there's significant overlap
                            if len(set(manga_name_words) & set(folder_name_words)) >= 2:
                                # Found a similar folder, try to find JSON in it
                                for file in folder.glob("*.json"):
                                    json_file = file
                                    logger.debug(f"Found JSON method 2.5 for _load_manga_info {manga_title}: {json_file.name} (in folder {folder.name})")
                                    break
                                if json_file:
                                    break
            
            # 3. Try with exact folder name
            if not json_file:
                exact_json = manga_folder / f"{manga_title}.json"
                if exact_json.exists():
                    json_file = exact_json
            
            # 4. Try different sanitization variations
            if not json_file and manga_folder.exists():
                variations = [
                    "Tower_of_God_A_Ascensao_de_Urek_Mazzino",
                    "Tower_of_God_-_A_Ascensao_de_Urek_Mazzino",  
                    "Tower of God - A Ascensão de Urek Mazzino",
                    "Tower_of_God_A_Ascensao_de_Urek_Mazzino"
                ]
                for variation in variations:
                    if variation != manga_title:  
                        for ext in ['.json']:
                            potential_file = manga_folder / f"{variation}{ext}"
                            logger.debug(f"Trying variation: {potential_file}")
                            if potential_file.exists():
                                json_file = potential_file
                                logger.debug(f"Found JSON method 4 for {manga_title}: {json_file.name} (variation: {variation})")
                                break
            
            # Add fuzzy search in output folder for _load_manga_info
            if not json_file and output_folder.exists():
                logger.debug(f"Trying fuzzy search in output folder for _load_manga_info: {manga_title}")
                for file in output_folder.glob("*.json"):
                    file_stem = sanitize_filename(file.stem, is_file=False, remove_accents=True)
                    if (sanitized_title in file_stem or 
                        file_stem in sanitized_title or
                        self._fuzzy_match_names(sanitized_title, file_stem)):
                        json_file = file
                        logger.debug(f"Found JSON via fuzzy match in output folder for _load_manga_info: {json_file}")
                        break
            
            if json_file and json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract group from first chapter if not at root level
                group = data.get("group", "")
                if not group:
                    chapters = data.get("chapters", {})
                    if chapters:
                        first_chapter = list(chapters.values())[0]
                        groups = first_chapter.get("groups", {})
                        if groups:
                            group = list(groups.keys())[0]  # Get first group name
                
                # Update manga with JSON data
                if self.current_manga:
                    self.current_manga.description = data.get("description", "")
                    self.current_manga.cover_url = data.get("cover", "")
                
                # Update internal manga info state
                manga_info = {
                    "title": data.get("title", manga_title),
                    "description": data.get("description", ""),
                    "artist": data.get("artist", ""),
                    "author": data.get("author", ""),
                    "cover": data.get("cover", ""),
                    "status": data.get("status", ""),
                    "group": group,  # Use extracted group
                    "chapterCount": len(data.get("chapters", {})),
                    "hasJson": True
                }
                logger.debug(f"Loaded manga info from JSON: {manga_info['title']}")
                logger.debug(f"Extracted metadata in _load_manga_info - artist: '{manga_info['artist']}', "
                           f"author: '{manga_info['author']}', group: '{manga_info['group']}'")
                return manga_info
            else:
                # No JSON found, use folder data
                manga_info = {
                    "title": manga_title,
                    "description": "",
                    "artist": "",
                    "author": "",
                    "cover": "",
                    "status": "",
                    "group": "",
                    "chapterCount": folder_chapter_count,
                    "hasJson": False
                }
                logger.debug(f"No JSON found, using folder data: {manga_title}")
                return manga_info
            
        except Exception as e:
            logger.error(f"Error loading manga info: {e}")
            # Use fallback data
            manga_info = {
                "title": manga_title,
                "description": "",
                "artist": "",
                "author": "",
                "cover": "",
                "status": "",
                "group": "",
                "chapterCount": folder_chapter_count,
                "hasJson": False
            }
            return manga_info
    
    def _load_manga_metadata(self):
        """Load manga metadata from JSON - wrapper for compatibility"""
        if not self.current_manga:
            return
            
        # Get chapter count for current manga
        chapter_count = len(getattr(self.current_manga, 'chapters', [])) or self.chapter_model.rowCount()
        
        # Load comprehensive manga info
        manga_info = self._load_manga_info(self.current_manga.title, chapter_count)
        
        # Update current manga with loaded info
        if manga_info:
            self.current_manga.description = manga_info.get('description', '')
            self.current_manga.cover_url = manga_info.get('cover', '')
            
            # Emit signal with updated manga info
            self.mangaInfoChanged.emit(manga_info)
            logger.debug(f"Updated manga metadata for {self.current_manga.title}")
    
    def _fuzzy_match_names(self, name1: str, name2: str, threshold: float = 0.6) -> bool:
        """Simple fuzzy matching for manga names - EXACT LOGIC FROM ORIGINAL"""
        name1_words = set(name1.lower().replace('_', ' ').split())
        name2_words = set(name2.lower().replace('_', ' ').split())
        
        if not name1_words or not name2_words:
            return False
            
        intersection = name1_words & name2_words
        union = name1_words | name2_words
        
        similarity = len(intersection) / len(union) if union else 0
        return similarity >= threshold
    
    @Slot(list)
    def set_selected_chapters(self, chapter_indices: List[int]):
        """Set selected chapters for upload"""
        try:
            chapters = self.chapter_model.chapters
            self.selected_chapters = [chapters[i] for i in chapter_indices if i < len(chapters)]
            logger.debug(f"Selected {len(self.selected_chapters)} chapters for upload")
        except Exception as e:
            logger.error(f"Error setting selected chapters: {e}")
    
    @Slot()
    def toggle_chapter_order(self):
        """Toggle chapter order between ascending and descending"""
        try:
            # Use the model's built-in toggleOrder method
            self.chapter_model.toggleOrder()
            self.chapterListChanged.emit()
            logger.debug("Toggled chapter order")
        except Exception as e:
            logger.error(f"Error toggling chapter order: {e}")
    
    @Slot(result=str)
    def get_manga_info(self) -> str:
        """Get manga information as JSON string"""
        if not self.current_manga:
            return "{}"
        
        try:
            manga_info = {
                "title": self.current_manga.title,
                "path": str(self.current_manga.path),
                "chapter_count": self.current_manga.chapter_count,
                "cover_url": self.current_manga.cover_url,
                "description": self.current_manga.description,
                "selected_chapters": len(self.selected_chapters)
            }
            return json.dumps(manga_info, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error getting manga info: {e}")
            return "{}"
    
    def get_selected_chapters(self) -> List[Chapter]:
        """Get currently selected chapters"""
        return self.selected_chapters.copy()
    
    def get_current_manga(self) -> Optional[Manga]:
        """Get currently selected manga"""
        return self.current_manga
    
    # === CRITICAL MISSING METHODS FROM ORIGINAL ===
    
    def filter_manga_list(self, search_text: str):
        """Filter manga list based on search text - CRITICAL"""
        try:
            root_folder = Path(self.config_manager.config.root_folder)
            if not root_folder.exists():
                logger.warning(f"Root folder does not exist: {root_folder}")
                return
            
            mangas = []
            search_lower = search_text.lower().strip()
            
            for manga_dir in root_folder.iterdir():
                if manga_dir.is_dir() and not manga_dir.name.startswith('.'):
                    # Check if manga matches search
                    if not search_lower or search_lower in manga_dir.name.lower():
                        # Count chapters (subdirectories with images)
                        chapter_count = 0
                        for chapter_dir in manga_dir.iterdir():
                            if chapter_dir.is_dir():
                                # Check if directory contains images
                                has_images = any(
                                    f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']
                                    for f in chapter_dir.iterdir()
                                    if f.is_file()
                                )
                                if has_images:
                                    chapter_count += 1
                        
                        # Create manga object
                        manga = Manga(
                            title=manga_dir.name,
                            path=manga_dir,
                            cover_url="",  # TODO: Find cover image
                            description=""  # TODO: Load from metadata
                        )
                        # Add chapter count as custom attribute
                        manga._chapter_count = chapter_count
                        mangas.append(manga)
            
            # Sort by title
            mangas.sort(key=lambda m: m.title.lower())
            
            # Convert to the expected format for the model
            manga_entries = []
            for manga in mangas:
                # Try to load cover from JSON metadata
                cover_url = self._load_manga_cover(manga)
                
                manga_entry = {
                    'title': manga.title,
                    'path': str(manga.path),
                    'chapterCount': getattr(manga, '_chapter_count', 0),
                    'coverUrl': cover_url
                }
                manga_entries.append(manga_entry)
            
            # Update model with correct format
            self.manga_model.setMangas(manga_entries)
            self.mangaListChanged.emit()
            
            logger.info(f"Filtered to {len(mangas)} manga titles for search: '{search_text}'")
            
        except Exception as e:
            logger.error(f"Error filtering manga list: {e}")
    
    def load_manga_details(self, manga_path: str):
        """Load details for specific manga - CRITICAL"""
        try:
            manga_path_obj = Path(manga_path)
            if not manga_path_obj.exists():
                logger.warning(f"Manga path does not exist: {manga_path}")
                return
            
            # Select this manga
            self.select_manga(manga_path_obj.name)
            
        except Exception as e:
            logger.error(f"Error loading manga details: {e}")
    
    def start_upload(self):
        """Start upload process - CRITICAL"""
        try:
            if not self.current_manga:
                raise ValueError("No manga selected")
            
            selected_chapters = self.get_selected_chapters()
            if not selected_chapters:
                raise ValueError("No chapters selected")
            
            # TODO: Implement actual upload logic using uploader_service
            logger.info(f"Starting upload for {len(selected_chapters)} chapters of {self.current_manga.title}")
            
            # For now, just emit signals
            self.uploadProgressChanged.emit(self.current_manga.title, 0)
            
            # Simulate upload completion (replace with actual upload logic)
            self.uploadCompleted.emit(self.current_manga.title)
            
        except Exception as e:
            logger.error(f"Error starting upload: {e}")
            self.uploadFailed.emit(
                self.current_manga.title if self.current_manga else "Unknown", 
                str(e)
            )
    
    def load_existing_metadata(self, manga_title: str):
        """Load existing metadata for editing - COMPREHENSIVE VERSION FROM ORIGINAL"""
        try:
            output_folder = Path(self.config_manager.config.output_folder)
            manga_folder = output_folder / manga_title
            
            logger.debug(f"Loading metadata for edit: {manga_title}")
            logger.debug(f"Looking in folder: {manga_folder}")
            
            # Try multiple approaches to find JSON file - EXACT LOGIC FROM ORIGINAL
            json_file = None
            
            # 0. First try in root folder (same directory as manga folder)
            root_folder = Path(self.config_manager.config.root_folder)
            sanitized_title = sanitize_filename(manga_title, is_file=False, remove_accents=True)
            root_json = root_folder / f"{sanitized_title}.json"
            if root_json.exists():
                json_file = root_json
                logger.debug(f"Found JSON method 0 (root) for loadExistingMetadata {manga_title}: {json_file.name}")
            
            # 0.1. Also try glob search in root folder
            if not json_file:
                for file in root_folder.glob("*.json"):
                    if sanitize_filename(manga_title, is_file=False, remove_accents=True) == sanitize_filename(file.stem, is_file=True, remove_accents=True):
                        json_file = file
                        logger.debug(f"Found JSON method 0.1 (root glob) for loadExistingMetadata {manga_title}: {json_file.name}")
                        break
            
            # 1. Try with sanitized filename in output folder
            if not json_file:
                potential_json = manga_folder / f"{sanitized_title}.json"
                if potential_json.exists():
                    json_file = potential_json
                    logger.debug(f"Found JSON with sanitized name: {json_file}")
            
            # 2. If not found, try looking for any .json file in the folder
            if not json_file and manga_folder.exists():
                for file in manga_folder.glob("*.json"):
                    json_file = file
                    logger.debug(f"Found JSON file: {json_file}")
                    break
            
            # 2.5. If manga folder doesn't exist, try to find similar named folders
            if not json_file and not manga_folder.exists():
                if output_folder.exists():
                    # Look for folders with similar names
                    manga_name_words = manga_title.lower().split()
                    for folder in output_folder.iterdir():
                        if folder.is_dir():
                            folder_name_words = folder.name.lower().split()
                            # Check if there's significant overlap
                            if len(set(manga_name_words) & set(folder_name_words)) >= 2:
                                # Found a similar folder, try to find JSON in it
                                for file in folder.glob("*.json"):
                                    json_file = file
                                    logger.debug(f"Found JSON method 2.5 for loadExistingMetadata {manga_title}: {json_file.name} (in folder {folder.name})")
                                    break
                                if json_file:
                                    break
            
            # 2.7. Try directly in output folder with sanitized name
            if not json_file:
                direct_json = output_folder / f"{sanitized_title}.json"
                if direct_json.exists():
                    json_file = direct_json
                    logger.debug(f"Found JSON directly in output folder: {json_file}")
            
            # 2.8. Try fuzzy search in output folder for similar JSON files
            if not json_file and output_folder.exists():
                logger.debug(f"Trying fuzzy search in output folder for: {manga_title}")
                for file in output_folder.glob("*.json"):
                    file_stem = sanitize_filename(file.stem, is_file=False, remove_accents=True)
                    if (sanitized_title in file_stem or 
                        file_stem in sanitized_title or
                        self._fuzzy_match_names(sanitized_title, file_stem)):
                        json_file = file
                        logger.debug(f"Found JSON via fuzzy match in output folder: {json_file}")
                        break
            
            # 3. Try with exact folder name
            if not json_file:
                exact_json = manga_folder / f"{manga_title}.json"
                if exact_json.exists():
                    json_file = exact_json
                    logger.debug(f"Found JSON with exact name: {json_file}")
            
            # 4. Try different sanitization variations
            if not json_file and manga_folder.exists():
                logger.debug(f"Trying variations for: {manga_title}")
                # Try with different characters replacement
                base_name = manga_title
                variations = [
                    # Standard variations
                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" ", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" - ", "_").replace(" ", "_").replace("–", "-").replace("ã", "a").replace("ç", "c"),
                    base_name.replace(" ", "_").replace("-", "_").replace("–", "_").replace("ã", "a").replace("ç", "c"),
                    # More aggressive variations  
                    base_name.replace(" - ", " ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace(" - ", "").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    # With "A" instead of "A"
                    base_name.replace(" - A ", " A ").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace(" - A ", "_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    # Remove articles
                    base_name.replace("Tower of God - A ", "Tower_of_God_A_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_"),
                    base_name.replace("Tower of God - A ", "Tower_of_God_").replace("–", "").replace("ã", "a").replace("ç", "c").replace(" ", "_")
                ]
                
                for i, variation in enumerate(variations):
                    potential_file = manga_folder / f"{variation}.json"
                    logger.debug(f"Variation {i+1}: trying {potential_file}")
                    if potential_file.exists():
                        json_file = potential_file
                        logger.debug(f"Found JSON with variation for {manga_title}: {json_file}")
                        break
            
            if json_file and json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract group from first chapter if not at root level
                group = data.get("group", "")
                if not group:
                    chapters = data.get("chapters", {})
                    if chapters:
                        first_chapter = list(chapters.values())[0]
                        groups = first_chapter.get("groups", {})
                        if groups:
                            group = list(groups.keys())[0]  # Get first group name
                
                # Ensure all metadata fields are present
                metadata = {
                    "title": data.get("title", manga_title),
                    "description": data.get("description", ""),
                    "artist": data.get("artist", ""),
                    "author": data.get("author", ""),
                    "cover": data.get("cover", ""),
                    "status": data.get("status", "Em Andamento"),
                    "group": group
                }
                
                logger.debug(f"Found existing metadata: {metadata.get('title', 'No title')}")
                logger.debug(f"Extracted metadata - artist: '{metadata['artist']}', "
                           f"author: '{metadata['author']}', group: '{metadata['group']}'")
                logger.debug(f"Returning loadExistingMetadata data: {metadata}")
                return metadata
            else:
                logger.debug(f"No JSON found for {manga_title}, using defaults")
                # No existing metadata, use defaults
                default_data = {
                    "title": manga_title,
                    "description": "",
                    "artist": "",
                    "author": "",
                    "group": "",
                    "cover": "",
                    "status": "Em Andamento"
                }
                logger.debug(f"Returning default loadExistingMetadata data: {default_data}")
                return default_data
                
        except Exception as e:
            logger.error(f"Error loading metadata for {manga_title}: {e}")
            # Use defaults on error
            default_data = {
                "title": manga_title,
                "description": "",
                "artist": "", 
                "author": "",
                "cover": "",
                "status": "Em Andamento"
            }
            return default_data
    
    def _load_manga_cover(self, manga: Manga) -> str:
        """Load cover URL from manga metadata using comprehensive search"""
        try:
            # Use the comprehensive _load_manga_info method to get cover
            chapter_count = getattr(manga, '_chapter_count', 0)
            manga_info = self._load_manga_info(manga.title, chapter_count)
            
            if manga_info and manga_info.get('cover'):
                return manga_info['cover']
                    
        except Exception as e:
            logger.debug(f"Could not load cover for {manga.title}: {e}")
        
        return ""
    
    @Slot(str)
    def filterMangaList(self, search_text: str):
        """Filter manga list based on search text"""
        try:
            root_folder = Path(self.config_manager.config.root_folder)
            if not root_folder.exists():
                return
            
            search_lower = search_text.lower().strip()
            manga_entries = []
            
            for manga_dir in root_folder.iterdir():
                if manga_dir.is_dir() and not manga_dir.name.startswith('.'):
                    # Check if manga matches search
                    if not search_lower or search_lower in manga_dir.name.lower():
                        # Count chapters
                        chapter_count = sum(
                            1 for chapter_dir in manga_dir.iterdir()
                            if chapter_dir.is_dir() and any(
                                f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']
                                for f in chapter_dir.iterdir() if f.is_file()
                            )
                        )
                        
                        # Create manga object to get cover
                        manga = Manga(
                            title=manga_dir.name,
                            path=manga_dir,
                            cover_url="",
                            description=""
                        )
                        cover_url = self._load_manga_cover(manga)
                        
                        manga_entry = {
                            'title': manga_dir.name,
                            'path': str(manga_dir),
                            'chapterCount': chapter_count,
                            'coverUrl': cover_url
                        }
                        manga_entries.append(manga_entry)
            
            self.manga_model.setMangas(manga_entries)
            self.mangaListChanged.emit()
            
        except Exception as e:
            logger.error(f"Error filtering manga list: {e}")
    
    @Slot(str)
    def loadMangaDetails(self, manga_path: str):
        """Load details for selected manga (compatibility method)"""
        try:
            path = Path(manga_path)
            self.select_manga(path.name)
        except Exception as e:
            logger.error(f"Error loading manga details: {e}")
    
    @Slot()
    def selectAllChapters(self):
        """Select all chapters in the current manga"""
        if hasattr(self.chapter_model, 'selectAll'):
            self.chapter_model.selectAll()
    
    @Slot()
    def unselectAllChapters(self):
        """Unselect all chapters in the current manga"""
        if hasattr(self.chapter_model, 'unselectAll'):
            self.chapter_model.unselectAll()
    
    def getSelectedChapters(self) -> List[str]:
        """Get selected chapter names for upload (compatibility method)"""
        try:
            if hasattr(self.chapter_model, 'getSelectedChapters'):
                return self.chapter_model.getSelectedChapters()
            return []
        except Exception as e:
            logger.error(f"Error getting selected chapters: {e}")
            return []
    
    def update_metadata(self, metadata_dict: Dict[str, Any]):
        """Update metadata for current manga - FIXED TO PROPERLY UPDATE hasJson STATE"""
        try:
            if not self.current_manga:
                logger.error("No manga selected for metadata update")
                return
            
            output_folder = Path(self.config_manager.config.output_folder)
            manga_title = self.current_manga.title
            
            # Find existing JSON file
            json_file = None
            
            # Try in manga folder first
            manga_folder = output_folder / manga_title
            if manga_folder.exists():
                for file in manga_folder.glob("*.json"):
                    json_file = file
                    break
            
            # Try fuzzy search if not found
            if not json_file and output_folder.exists():
                sanitized_title = sanitize_filename(manga_title, is_file=False, remove_accents=True)
                for file in output_folder.glob("*.json"):
                    file_stem = sanitize_filename(file.stem, is_file=False, remove_accents=True)
                    if (sanitized_title in file_stem or 
                        file_stem in sanitized_title or
                        self._fuzzy_match_names(sanitized_title, file_stem)):
                        json_file = file
                        break
            
            json_operation_success = False
            
            if json_file and json_file.exists():
                # Update existing file
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Update metadata fields (exclude "group" as it belongs in chapters)
                data["title"] = metadata_dict.get("title", "")
                data["description"] = metadata_dict.get("description", "")
                data["artist"] = metadata_dict.get("artist", "")
                data["author"] = metadata_dict.get("author", "")
                data["cover"] = metadata_dict.get("cover", "")
                data["status"] = metadata_dict.get("status", "Em Andamento")
                
                # Save updated data
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                json_operation_success = True
                logger.info(f"Metadata updated: {json_file}")
                
            else:
                # Create new JSON file
                logger.info(f"Creating new JSON file for: {manga_title}")
                
                # Create output folder if needed
                manga_folder = output_folder / manga_title
                manga_folder.mkdir(parents=True, exist_ok=True)
                
                # Create sanitized filename
                sanitized_title = sanitize_filename(manga_title, is_file=True, remove_accents=True)
                if not sanitized_title.endswith('.json'):
                    sanitized_title += '.json'
                
                new_json_file = manga_folder / sanitized_title
                
                # Create new metadata structure (exclude "group" as it belongs in chapters)
                new_data = {
                    "title": metadata_dict.get("title", ""),
                    "description": metadata_dict.get("description", ""),
                    "artist": metadata_dict.get("artist", ""),
                    "author": metadata_dict.get("author", ""),
                    "cover": metadata_dict.get("cover", ""),
                    "status": metadata_dict.get("status", "Em Andamento"),
                    "chapters": {}  # Empty chapters for now
                }
                
                # Save new JSON file
                with open(new_json_file, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, indent=2, ensure_ascii=False)
                
                json_operation_success = True
                logger.info(f"New metadata file created: {new_json_file}")
            
            # CRITICAL FIX: Update manga info with hasJson = true after successful JSON operation
            if json_operation_success:
                # Get current chapter count
                chapter_count = self.chapter_model.rowCount() if self.chapter_model else 0
                
                # Create updated manga info with hasJson = true
                updated_manga_info = {
                    "title": metadata_dict.get("title", manga_title),
                    "description": metadata_dict.get("description", ""),
                    "artist": metadata_dict.get("artist", ""),
                    "author": metadata_dict.get("author", ""),
                    "cover": metadata_dict.get("cover", ""),
                    "status": metadata_dict.get("status", "Em Andamento"),
                    "group": metadata_dict.get("group", ""),  # Include group from update
                    "chapterCount": chapter_count,
                    "hasJson": True  # CRITICAL: Set hasJson to true after successful update
                }
                
                # Update current manga properties
                if self.current_manga:
                    self.current_manga.description = updated_manga_info["description"]
                    self.current_manga.cover_url = updated_manga_info["cover"]
                
                # Emit signal with updated manga info - THIS WILL UPDATE THE GITHUB BUTTON STATE
                self.mangaInfoChanged.emit(updated_manga_info)
                logger.info(f"✅ Emitted mangaInfoChanged with hasJson=true for {manga_title}")
            else:
                logger.error("JSON operation failed - not updating hasJson state")
            
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            raise