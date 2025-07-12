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
    
    def _scan_chapters(self) -> List[Chapter]:
        """Scan manga directory for chapters"""
        chapters = []
        if self.path.exists() and self.path.is_dir():
            for item in sorted(self.path.iterdir()):
                if item.is_dir():
                    chapter = Chapter(
                        name=item.name,
                        path=item,
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