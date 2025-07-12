import re
import unicodedata
from pathlib import Path
from typing import List, Optional


def normalize_text(text: str) -> str:
    """Normalize text for comparisons"""
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize('NFKC', text.strip())


def sanitize_filename(name: str, is_file: bool = True, remove_accents: bool = True) -> str:
    """
    Sanitize name for filesystem
    
    Args:
        name: Original name
        is_file: Whether this is a filename (True) or folder name (False)
        remove_accents: Whether to remove accents and special characters
    
    Examples:
        sanitize_filename("Tower of God: A Ascensão!", True, True) -> "Tower_of_God_A_Ascensao"
        sanitize_filename("Naruto: Último", True, True) -> "Naruto_Ultimo" 
    """
    if not name:
        return "sem_titulo" if is_file else "pasta_sem_nome"
    
    temp = name
    
    # Remove accents if requested
    if remove_accents:
        # Normalize unicode and remove accent marks
        temp = unicodedata.normalize('NFD', temp)
        temp = ''.join(c for c in temp if unicodedata.category(c) != 'Mn')
    
    # Replace spaces with underscores for files
    if is_file:
        temp = temp.replace(" ", "_")
    
    # Remove invalid filesystem characters
    temp = re.sub(r'[\\/*?:"<>|]', "", temp)
    
    # Additional cleanup for files with extensions
    if is_file:
        # Handle file extensions
        base, dot, ext = temp.rpartition('.')
        if dot and ext:  # Has extension
            # Clean the base name
            base = re.sub(r'[^\w_-]', '', base)  # Keep only alphanumeric, underscore, hyphen
            base = re.sub(r'_+', '_', base)      # Remove multiple underscores
            base = base.strip('_-')              # Remove leading/trailing
            temp = (base if base else "arquivo_sem_nome") + dot + ext
        else:
            # No extension, treat as base name
            temp = re.sub(r'[^\w_-]', '', temp)
            temp = re.sub(r'_+', '_', temp)
            temp = temp.strip('_-')
    else:
        # Folder name cleanup
        temp = re.sub(r'[^\w\s_-]', '', temp)
        temp = re.sub(r'[\s_-]+', '_', temp)
        temp = temp.strip('_-')
    
    return temp if temp else ("sem_titulo" if is_file else "pasta_sem_nome")


def natural_sort_key(text: str) -> List:
    """Natural sorting key function"""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', text)]


def find_images(directory: Path, extensions: Optional[set] = None) -> List[Path]:
    """Find all images in a directory"""
    if extensions is None:
        extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
    
    images = []
    if directory.exists() and directory.is_dir():
        for file in sorted(directory.iterdir(), key=lambda p: natural_sort_key(p.name)):
            if file.is_file() and file.suffix.lower() in extensions:
                images.append(file)
    
    return images


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def estimate_upload_time(total_size: int, speed_mbps: float = 10.0) -> float:
    """Estimate upload time in seconds"""
    speed_bytes_per_sec = (speed_mbps * 1024 * 1024) / 8
    return total_size / speed_bytes_per_sec