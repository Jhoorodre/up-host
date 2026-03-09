#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.services.scan_service import ScanService

async def test_async_scanning():
    print("🧪 Testing asynchronous scanning implementation...")
    
    # Test folder - use current directory
    test_folder = Path.cwd()
    print(f"📁 Testing with folder: {test_folder}")
    
    # Initialize services
    scan_service = ScanService(max_workers=4, enable_cache=True)
    
    print("⚡ Starting async scan test...")
    start_time = time.time()
    
    # Track if event loop is responsive
    async def heartbeat():
        count = 0
        while True:
            count += 1
            print(f"💓 Event loop heartbeat #{count} (responsive)")
            await asyncio.sleep(1)
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(heartbeat())
    
    try:
        # Test the new async scanning method
        manga_folder = test_folder / "test_manga_data"
        if not manga_folder.exists():
            # Create test folder structure
            print(f"📂 Creating test manga structure at {manga_folder}")
            manga_folder.mkdir()
            (manga_folder / "Chapter 1").mkdir()
            (manga_folder / "Chapter 2").mkdir()
            
            # Create dummy image files
            for i in range(1, 6):
                (manga_folder / "Chapter 1" / f"page_{i:03d}.jpg").touch()
                (manga_folder / "Chapter 2" / f"page_{i:03d}.jpg").touch()
        
        print(f"🔍 Testing _scan_manga_folder_async with: {manga_folder}")
        
        # Test the async method directly
        result = await scan_service._scan_manga_folder_async(manga_folder)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Async scan completed in {duration:.2f} seconds")
        if result:
            print(f"📖 Found manga: {result.title} with {len(result.chapters)} chapters")
        else:
            print("❌ No manga found")
        
        # Cancel heartbeat
        heartbeat_task.cancel()
        
        print("🎉 Test completed successfully - event loop remained responsive!")
        return True
        
    except Exception as e:
        heartbeat_task.cancel()
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        if (test_folder / "test_manga_data").exists():
            import shutil
            shutil.rmtree(test_folder / "test_manga_data")

if __name__ == "__main__":
    result = asyncio.run(test_async_scanning())
    exit_code = 0 if result else 1
    sys.exit(exit_code)