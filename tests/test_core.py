import pytest
import asyncio
from pathlib import Path
from src.core.models import Manga, Chapter, MangaStatus
from src.core.hosts import CatboxHost
from src.core.services import MangaUploaderService


@pytest.fixture
def sample_manga():
    return Manga(
        title="Test Manga",
        path=Path("tests/fixtures/manga"),
        description="Test description",
        artist="Test Artist",
        author="Test Author",
        status=MangaStatus.ONGOING
    )


@pytest.fixture
def sample_chapter():
    return Chapter(
        name="Chapter 1",
        path=Path("tests/fixtures/manga/ch1"),
        images=[]
    )


@pytest.fixture
async def uploader_service():
    service = MangaUploaderService()
    catbox = CatboxHost({"userhash": "", "max_workers": 2})
    service.register_host("Catbox", catbox)
    service.set_host("Catbox")
    return service


class TestModels:
    def test_manga_creation(self, sample_manga):
        assert sample_manga.title == "Test Manga"
        assert sample_manga.status == MangaStatus.ONGOING
    
    def test_chapter_creation(self, sample_chapter):
        assert sample_chapter.name == "Chapter 1"
        assert isinstance(sample_chapter.images, list)


class TestHosts:
    @pytest.mark.asyncio
    async def test_catbox_init(self):
        host = CatboxHost({"userhash": "test123"})
        assert host.userhash == "test123"
        assert host.max_workers == 5


class TestUploaderService:
    @pytest.mark.asyncio
    async def test_register_host(self, uploader_service):
        assert "Catbox" in uploader_service.hosts
        assert uploader_service.current_host is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])