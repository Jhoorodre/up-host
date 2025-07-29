from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from pathlib import Path


class MangaStatus(str, Enum):
    ONGOING = "Em Andamento"
    COMPLETED = "Concluído"
    HIATUS = "Hiato"
    CANCELLED = "Cancelado"
    PAUSED = "Pausado"


@dataclass
class Chapter:
    name: str
    path: Path
    images: List[Path]
    number: Optional[int] = None
    volume: Optional[str] = ""
    
    def __post_init__(self):
        if not self.images:
            self.images = self._scan_images()
    
    def _scan_images(self) -> List[Path]:
        """Scan chapter directory for images"""
        extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        images = []
        if self.path.exists() and self.path.is_dir():
            for file in sorted(self.path.iterdir()):
                if file.suffix.lower() in extensions:
                    images.append(file)
        return images


@dataclass
class Manga:
    title: str
    path: Path
    description: str = ""
    artist: str = ""
    author: str = ""
    cover_url: str = ""
    status: MangaStatus = MangaStatus.ONGOING
    chapters: List[Chapter] = None
    
    def __post_init__(self):
        if self.chapters is None:
            self.chapters = self._scan_chapters()
    
    def rescan_with_structure(self, structure: str):
        """Rescan chapters with specific structure"""
        self.chapters = self._scan_chapters(structure)
    
    def _scan_chapters(self, structure: str = "standard") -> List[Chapter]:
        """Scan manga directory for chapters based on structure type"""
        chapters = []
        if not self.path.exists() or not self.path.is_dir():
            return chapters
            
        if structure == "standard":
            # Standard: Manga/Chapter/images
            chapters = self._scan_standard_structure()
        elif structure == "flat":
            # Flat: Manga/images (single chapter)
            chapters = self._scan_flat_structure()
        elif structure == "volume_based":
            # Volume-based: Manga/Volume/Chapter/images
            chapters = self._scan_volume_based_structure()
        elif structure == "scan_manga_chapter":
            # Scan-based: Scan/ScanName/Manga/Chapter/images
            chapters = self._scan_scan_manga_chapter_structure()
        elif structure == "scan_manga_volume_chapter":
            # Scan-volume-based: Scan/ScanName/Manga/Volume/Chapter/images
            chapters = self._scan_scan_manga_volume_chapter_structure()
        else:
            # Fallback to standard
            chapters = self._scan_standard_structure()
            
        return chapters
    
    def _scan_standard_structure(self) -> List[Chapter]:
        """Standard structure: Manga/Chapter/images"""
        chapters = []
        for item in sorted(self.path.iterdir()):
            if item.is_dir():
                chapter = Chapter(
                    name=item.name,
                    path=item,
                    images=[]
                )
                chapters.append(chapter)
        return chapters
    
    def _scan_flat_structure(self) -> List[Chapter]:
        """Flat structure: All images directly in manga folder"""
        extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        images = []
        
        for file in sorted(self.path.iterdir()):
            if file.is_file() and file.suffix.lower() in extensions:
                images.append(file)
        
        if images:
            # Create a single chapter with all images
            chapter = Chapter(
                name=f"{self.title} - Volume Único",
                path=self.path,
                images=images
            )
            return [chapter]
        return []
    
    def _scan_volume_based_structure(self) -> List[Chapter]:
        """Volume-based structure: Manga/Volume/Chapter/images"""
        chapters = []
        
        for volume_item in sorted(self.path.iterdir()):
            if volume_item.is_dir():
                volume_name = volume_item.name
                
                for chapter_item in sorted(volume_item.iterdir()):
                    if chapter_item.is_dir():
                        chapter_name = f"{volume_name} - {chapter_item.name}"
                        chapter = Chapter(
                            name=chapter_name,
                            path=chapter_item,
                            images=[]
                        )
                        chapters.append(chapter)
        
        return chapters
    
    def _scan_scan_manga_chapter_structure(self) -> List[Chapter]:
        """Scan-based structure: Scan/ScanName/Manga/Chapter/images"""
        chapters = []
        
        # Navigate: self.path is the root folder containing scan folders
        # Structure: root/scan_name/manga_title/chapter/images
        # We need to find manga folders across all scan folders
        
        for scan_item in sorted(self.path.iterdir()):
            if scan_item.is_dir():  # This is a scan folder
                scan_name = scan_item.name
                
                # Look for manga folders inside this scan
                for manga_item in sorted(scan_item.iterdir()):
                    if manga_item.is_dir() and manga_item.name == self.title:
                        # Found our manga inside this scan
                        for chapter_item in sorted(manga_item.iterdir()):
                            if chapter_item.is_dir():
                                chapter_name = f"[{scan_name}] {chapter_item.name}"
                                chapter = Chapter(
                                    name=chapter_name,
                                    path=chapter_item,
                                    images=[]
                                )
                                chapters.append(chapter)
        
        return chapters
    
    def _scan_scan_manga_volume_chapter_structure(self) -> List[Chapter]:
        """Scan-volume-based structure: Scan/ScanName/Manga/Volume/Chapter/images"""
        chapters = []
        
        # Navigate: self.path is the root folder containing scan folders
        # Structure: root/scan_name/manga_title/volume/chapter/images
        # We need to find manga folders across all scan folders
        
        for scan_item in sorted(self.path.iterdir()):
            if scan_item.is_dir():  # This is a scan folder
                scan_name = scan_item.name
                
                # Look for manga folders inside this scan
                for manga_item in sorted(scan_item.iterdir()):
                    if manga_item.is_dir() and manga_item.name == self.title:
                        # Found our manga inside this scan
                        for volume_item in sorted(manga_item.iterdir()):
                            if volume_item.is_dir():
                                volume_name = volume_item.name
                                
                                for chapter_item in sorted(volume_item.iterdir()):
                                    if chapter_item.is_dir():
                                        chapter_name = f"[{scan_name}] {volume_name} - {chapter_item.name}"
                                        chapter = Chapter(
                                            name=chapter_name,
                                            path=chapter_item,
                                            images=[]
                                        )
                                        chapters.append(chapter)
        
        return chapters


@dataclass
class UploadResult:
    url: str
    filename: str
    success: bool = True
    error: Optional[str] = None


@dataclass
class ChapterUploadResult:
    chapter_name: str
    album_url: str
    image_urls: List[str]
    failed_uploads: List[str]
    success: bool = True