import sys
import asyncio
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from loguru import logger
import qasync  # type: ignore[import-untyped]

# Add src to path
# sys.path.insert(0, str(Path(__file__).parent))

from ui.backend import Backend


def setup_logging():
    """Configure logging"""
    log_dir = Path.home() / ".manga_uploader" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_dir / "app.log",
        rotation="10 MB",
        retention="1 week",
        level="INFO"
    )
    logger.info("Manga Uploader Pro iniciado")


def main():
    # Setup logging
    setup_logging()
    
    # Create Qt Application
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Manga Uploader Pro")
    app.setOrganizationName("MangaUploader")
    
    # Setup async event loop BEFORE creating backend
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Create backend with running event loop
    backend = Backend()
    
    # Initialize async services now that loop is ready
    loop.create_task(backend.upload_queue.start())
    
    # Register backend
    engine.rootContext().setContextProperty("backend", backend)
    
    # Register models
    engine.rootContext().setContextProperty("mangaModel", backend.mangaModel)
    engine.rootContext().setContextProperty("chapterModel", backend.chapterModel)
    engine.rootContext().setContextProperty("githubFolderModel", backend.githubFolderModel)
    
    # Load QML
    qml_file = Path(__file__).parent / "ui" / "qml" / "main.qml"
    engine.load(str(qml_file))
    
    if not engine.rootObjects():
        logger.error("Falha ao carregar QML")
        sys.exit(1)
    
    # Run application with proper cleanup while loop is still active
    with loop:
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
        finally:
            try:
                try:
                    loop.run_until_complete(asyncio.wait_for(backend.shutdown(), timeout=3.0))
                except asyncio.TimeoutError:
                    logger.warning("Backend shutdown timed out")

                pending = [task for task in asyncio.all_tasks(loop) if not task.done()]
                for task in pending:
                    task.cancel()

                if pending:
                    try:
                        loop.run_until_complete(
                            asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), timeout=2.0)
                        )
                    except asyncio.TimeoutError:
                        logger.warning("Some tasks didn't complete during shutdown")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()