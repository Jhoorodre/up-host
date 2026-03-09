from pathlib import Path

from src.core.services.scan_service import ScanService


def test_scan_manga_folder_sync_uses_path_images(tmp_path: Path) -> None:
    manga_dir = tmp_path / "MyManga"
    chapter_dir = manga_dir / "Chapter 001"
    chapter_dir.mkdir(parents=True)

    image_file = chapter_dir / "001.png"
    image_file.write_bytes(b"fake-image")

    service = ScanService(max_workers=1, enable_cache=False)
    manga = service._scan_manga_folder_sync(manga_dir)

    assert manga is not None
    assert manga.chapters is not None
    assert len(manga.chapters) == 1
    assert len(manga.chapters[0].images) == 1
    assert isinstance(manga.chapters[0].images[0], Path)
    assert manga.chapters[0].images[0].name == "001.png"
