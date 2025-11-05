"""
Simple Runner Script for Video Editor
Run this script to edit your video automatically
"""

import os
import sys
from pathlib import Path


def check_environment():
    """Check if all dependencies are installed"""
    required_modules = [
        'moviepy', 'whisper', 'torch', 'PIL', 
        'cv2', 'numpy', 'requests', 'dotenv'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print("❌ Missing required modules:")
        for mod in missing:
            print(f"   - {mod}")
        print("\n⚠️  Please run: pip install -r requirements.txt")
        return False
    
    return True


def check_video_file():
    """Check if video file exists"""
    video_files = list(Path('.').glob('*.mp4'))
    
    if not video_files:
        print("❌ No video file found in current directory")
        print("   Please add your video file (.mp4) to this folder")
        return None
    
    if len(video_files) == 1:
        return str(video_files[0])
    
    # Multiple videos found
    print("📹 Multiple video files found:")
    for i, video in enumerate(video_files, 1):
        size_mb = video.stat().st_size / (1024 * 1024)
        print(f"   {i}. {video.name} ({size_mb:.1f} MB)")
    
    while True:
        try:
            choice = input("\nSelect video number (or press Enter for first one): ").strip()
            if not choice:
                return str(video_files[0])
            idx = int(choice) - 1
            if 0 <= idx < len(video_files):
                return str(video_files[idx])
        except (ValueError, IndexError):
            print("Invalid choice, please try again")


def check_api_keys():
    """Check if API keys are configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    pexels_key = os.getenv('PEXELS_API_KEY', '')
    pixabay_key = os.getenv('PIXABAY_API_KEY', '')
    
    if not pexels_key and not pixabay_key:
        print("\n⚠️  Warning: No API keys configured")
        print("   The script will use fallback image sources (Unsplash)")
        print("   For better results, get free API keys:")
        print("   - Pexels: https://www.pexels.com/api/")
        print("   - Pixabay: https://pixabay.com/api/docs/")
        print("\n   Create a .env file with your keys:")
        print("   PEXELS_API_KEY=your_key_here")
        input("\n   Press Enter to continue with fallback sources...")
        return False
    
    return True


def main():
    print("\n" + "="*60)
    print("   🎬 AUTOMATED VIDEO EDITOR")
    print("="*60 + "\n")
    
    # Check environment
    print("🔍 Checking environment...")
    if not check_environment():
        sys.exit(1)
    print("✓ All dependencies installed\n")
    
    # Check for video file
    print("🔍 Looking for video file...")
    video_file = check_video_file()
    if not video_file:
        sys.exit(1)
    print(f"✓ Found video: {video_file}\n")
    
    # Check API keys
    check_api_keys()
    
    # Import and run editor
    print("\n" + "="*60)
    print("🚀 Starting video editing process...")
    print("="*60 + "\n")
    
    try:
        from video_editor import VideoEditor
        
        output_file = "edited_" + os.path.basename(video_file)
        editor = VideoEditor(video_file, output_file)
        editor.process()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
