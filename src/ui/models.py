from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex
from typing import List, Dict, Any


class MangaListModel(QAbstractListModel):
    TitleRole = Qt.UserRole + 1
    PathRole = Qt.UserRole + 2
    ChapterCountRole = Qt.UserRole + 3
    CoverUrlRole = Qt.UserRole + 4
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mangas = []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._mangas)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._mangas):
            return None
        
        manga = self._mangas[index.row()]
        
        if role == Qt.DisplayRole or role == self.TitleRole:
            return manga["title"]
        elif role == self.PathRole:
            return manga["path"]
        elif role == self.ChapterCountRole:
            return manga["chapterCount"]
        elif role == self.CoverUrlRole:
            return manga.get("coverUrl", "")
        
        return None
    
    def roleNames(self):
        return {
            self.TitleRole: b"title",
            self.PathRole: b"path",
            self.ChapterCountRole: b"chapterCount",
            self.CoverUrlRole: b"coverUrl"
        }
    
    def setMangas(self, mangas: List[Dict[str, Any]]):
        self.beginResetModel()
        self._mangas = mangas
        self.endResetModel()
    
    def clear(self):
        self.beginResetModel()
        self._mangas = []
        self.endResetModel()
    
    def setFilterMode(self, mode: str, filter_value: str = ""):
        """Set filter mode for manga list"""
        self._filter_mode = mode
        self._filter_value = filter_value
        
        # Apply filter to current data
        if hasattr(self, '_all_mangas'):
            self._applyFilter()
    
    def _applyFilter(self):
        """Apply current filter to manga list"""
        if not hasattr(self, '_all_mangas'):
            return
            
        filtered_mangas = []
        
        for manga in self._all_mangas:
            include = False
            
            if self._filter_mode == "all":
                include = True
            elif self._filter_mode == "favorites":
                # Check if manga is in favorites (this would need to be passed from backend)
                include = manga.get("is_favorite", False)
            elif self._filter_mode == "recent":
                # Check if manga is in recent list
                include = manga.get("is_recent", False)
            elif self._filter_mode == "progress":
                # Check if manga has uploads in progress
                include = manga.get("status") in ["uploading", "pending"]
            elif self._filter_mode == "completed":
                # Check if manga is completed
                include = manga.get("status") == "completed"
            elif self._filter_mode == "tag":
                # Check if manga has the specified tag
                manga_tags = manga.get("tags", [])
                include = self._filter_value in manga_tags
            
            if include:
                filtered_mangas.append(manga)
        
        self.beginResetModel()
        self._mangas = filtered_mangas
        self.endResetModel()
    
    def setMangasWithFilter(self, mangas: List[Dict[str, Any]]):
        """Set mangas and store for filtering"""
        self._all_mangas = mangas
        self._filter_mode = "all"
        self._filter_value = ""
        
        self.beginResetModel()
        self._mangas = mangas
        self.endResetModel()


class ChapterListModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    PathRole = Qt.UserRole + 2
    ImageCountRole = Qt.UserRole + 3
    SelectedRole = Qt.UserRole + 4
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._chapters = []
        self._selected = set()
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._chapters)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._chapters):
            return None
        
        chapter = self._chapters[index.row()]
        
        if role == Qt.DisplayRole or role == self.NameRole:
            return chapter["name"]
        elif role == self.PathRole:
            return chapter["path"]
        elif role == self.ImageCountRole:
            return chapter["imageCount"]
        elif role == self.SelectedRole:
            return chapter["name"] in self._selected
        
        return None
    
    def setData(self, index, value, role):
        if role == self.SelectedRole and index.isValid():
            chapter_name = self._chapters[index.row()]["name"]
            if value:
                self._selected.add(chapter_name)
            else:
                self._selected.discard(chapter_name)
            self.dataChanged.emit(index, index, [role])
            return True
        return False
    
    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return Qt.NoItemFlags
    
    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.PathRole: b"path",
            self.ImageCountRole: b"imageCount",
            self.SelectedRole: b"selected"
        }
    
    def setChapters(self, chapters: List[Dict[str, Any]]):
        self.beginResetModel()
        self._chapters = chapters
        self._selected.clear()
        self.endResetModel()
    
    def getSelectedChapters(self):
        return list(self._selected)
    
    def clear(self):
        self.beginResetModel()
        self._chapters = []
        self._selected.clear()
        self.endResetModel()
    
    def selectAll(self):
        """Select all chapters"""
        for chapter in self._chapters:
            self._selected.add(chapter["name"])
        # Emit data changed for all items
        if self._chapters:
            top_left = self.index(0, 0)
            bottom_right = self.index(len(self._chapters) - 1, 0)
            self.dataChanged.emit(top_left, bottom_right, [self.SelectedRole])
    
    def unselectAll(self):
        """Unselect all chapters"""
        self._selected.clear()
        # Emit data changed for all items
        if self._chapters:
            top_left = self.index(0, 0)
            bottom_right = self.index(len(self._chapters) - 1, 0)
            self.dataChanged.emit(top_left, bottom_right, [self.SelectedRole])
    
    def toggleOrder(self):
        """Toggle chapter order between ascending and descending"""
        self.beginResetModel()
        self._chapters.reverse()
        self.endResetModel()


class GitHubFolderListModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    PathRole = Qt.UserRole + 2
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._folders = []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._folders)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._folders):
            return None
        
        folder = self._folders[index.row()]
        
        if role == Qt.DisplayRole or role == self.NameRole:
            return folder["name"]
        elif role == self.PathRole:
            return folder["path"]
        
        return None
    
    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.PathRole: b"path"
        }
    
    def setFolders(self, folders: List[Dict[str, Any]]):
        self.beginResetModel()
        self._folders = folders
        self.endResetModel()
    
    def clear(self):
        self.beginResetModel()
        self._folders = []
        self.endResetModel()