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