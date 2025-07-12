"""
Utilities for sanitizing file names and removing accents
"""
import re
import unicodedata
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """
    Sanitize a filename by removing accents and special characters
    
    Examples:
        "Tower of God: A Ascensão de Urek Mazzino" -> "Tower_of_God_A_Ascensao_de_Urek_Mazzino"
        "Naruto: Último Capítulo!" -> "Naruto_Ultimo_Capitulo"
    """
    if not name:
        return "untitled"
    
    # Remove accents and normalize unicode
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    
    # Replace spaces and special characters with underscores
    name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars except spaces and hyphens
    name = re.sub(r'[-\s]+', '_', name)   # Replace spaces and hyphens with underscores
    
    # Remove multiple underscores
    name = re.sub(r'_+', '_', name)
    
    # Remove leading/trailing underscores
    name = name.strip('_')
    
    # Ensure we have something
    if not name:
        return "untitled"
    
    return name


def sanitize_json_filename(manga_title: str) -> str:
    """
    Create a sanitized JSON filename for a manga
    
    Args:
        manga_title: Original manga title
        
    Returns:
        Sanitized filename with .json extension
        
    Example:
        "Tower of God: A Ascensão de Urek Mazzino" -> "Tower_of_God_A_Ascensao_de_Urek_Mazzino.json"
    """
    sanitized = sanitize_filename(manga_title)
    return f"{sanitized}.json"


def sanitize_folder_name(name: str) -> str:
    """
    Sanitize a folder name for GitHub paths
    
    Args:
        name: Original folder name
        
    Returns:
        Sanitized folder name safe for GitHub paths
    """
    return sanitize_filename(name).lower()  # Use lowercase for folders