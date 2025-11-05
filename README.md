# 🎬 Automated Video Editor with AI

An intelligent video editing system that automatically adds B-roll images, animations, and effects to educational videos using AI-powered speech recognition.

## ✨ Features

- **🎤 AI Speech Recognition**: Uses OpenAI's Whisper to transcribe and understand video content
- **🖼️ Automatic B-Roll**: Adds relevant images every 5-15 seconds based on spoken content
- **🎨 Professional Effects**: 
  - Color grading and beautification
  - Animated image overlays with slide, zoom, and fade effects
  - Text animations for key phrases
  - Borders, shadows, and professional styling
- **🤖 Smart Content Matching**: Automatically finds relevant images based on keywords and context
- **📊 Multiple Animation Styles**: Varied animations to keep content engaging

## 🎥 Reference

This editor is designed to create videos similar to professional educational content. See reference: https://youtu.be/hyxpjFoYQIM

## 🚀 Quick Start

### 1. Install Dependencies

First, install Python 3.8 or higher, then run:

```bash
pip install -r requirements.txt
```

This will install:
- moviepy (video editing)
- openai-whisper (speech recognition)
- torch (AI models)
- opencv-python (effects)
- PIL/Pillow (image processing)
- And other required libraries

**Note**: First installation may take 5-10 minutes as it downloads AI models.

### 2. Configure API Keys (Optional but Recommended)

For best results, get free API keys for image sources:

1. **Pexels API** (Recommended): 
   - Go to https://www.pexels.com/api/
   - Sign up for free
   - Get your API key

2. **Pixabay API** (Optional):
   - Go to https://pixabay.com/api/docs/
   - Sign up for free
   - Get your API key

Create a `.env` file in the project folder:

```env
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here
```

**Without API keys**: The script will still work using free fallback image sources (Unsplash), but results may be less relevant.

### 3. Run the Editor

Simply run:

```bash
python run_editor.py
```

The script will:
1. ✅ Check all dependencies
2. 🔍 Find your video file
3. 🎤 Transcribe the audio
4. 🔍 Extract keywords and topics
5. 🖼️ Download relevant images
6. 🎬 Apply effects and animations
7. 💾 Export the final video

## 📁 Project Structure

```
Video-Editing/
├── video_editor.py          # Main editing engine
├── image_downloader.py      # Image search and download
├── effects_manager.py       # Visual effects and animations
├── run_editor.py           # Simple runner script
├── requirements.txt        # Python dependencies
├── .env                    # API keys (create this)
├── README.md              # This file
│
├── Your_Video.mp4         # Input video
├── edited_Your_Video.mp4  # Output video
│
└── (Generated during processing)
    ├── broll_images/      # Downloaded images
    ├── transcript.json    # Speech transcription
    ├── keywords.json      # Extracted keywords
    └── broll_plan.json    # B-roll insertion plan
```

## 🎛️ Customization

### Adjust B-Roll Frequency

Edit `video_editor.py`, line ~175:

```python
insertions = self.plan_broll_insertions(min_interval=5, max_interval=15)
```

Change `min_interval` and `max_interval` to control how often images appear.

### Change Animation Styles

Edit `video_editor.py`, line ~305:

```python
effect = ['slide', 'zoom', 'fade'][i % 3]
```

Choose from: `'slide'`, `'zoom'`, `'fade'`, or implement custom effects in `effects_manager.py`.

### Adjust Color Grading

Edit `video_editor.py`, lines ~230-247 in the `apply_color_grading` method to adjust:
- Saturation
- Contrast
- Brightness
- Sharpness

### Image Position

Edit `video_editor.py`, line ~304:

```python
position = 'right' if i % 2 == 0 else 'left'
```

Options: `'right'`, `'left'`, `'top-left'`, `'top-right'`, `'bottom-left'`, `'bottom-right'`, `'center'`

## 🔧 Advanced Usage

### Process Specific Video

```python
from video_editor import VideoEditor

editor = VideoEditor(
    video_path="my_video.mp4",
    output_path="my_edited_video.mp4"
)
editor.process()
```

### Custom Keyword Extraction

Edit the `priority_keywords` list in `video_editor.py` (lines ~102-107) to match your video topic:

```python
priority_keywords = [
    'exercise', 'workout', 'health',  # Add your keywords here
    'your', 'custom', 'keywords'
]
```

## 📊 Output Files

After processing, you'll find:

- **edited_[video_name].mp4**: Your final edited video
- **transcript.json**: Full transcription with timestamps
- **keywords.json**: Extracted keywords and phrases
- **broll_plan.json**: B-roll insertion timeline
- **broll_images/**: Downloaded images used in the video

## ⚙️ System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **GPU**: Optional (CUDA-compatible GPU speeds up processing)
- **Disk Space**: 5GB free (for dependencies and processing)

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### Slow processing
- Use a GPU if available (automatically detected)
- Close other heavy applications
- Reduce video resolution before processing

### Poor image matching
- Add API keys (Pexels/Pixabay) for better results
- Customize `priority_keywords` for your specific topic
- Check `keywords.json` to see what was extracted

### Video export fails
- Ensure you have enough disk space
- Check video codec compatibility
- Try reducing output quality in `export_video` method

## 🎯 Tips for Best Results

1. **Clear Audio**: Better audio quality = better transcription = better keyword matching
2. **Structured Content**: Videos with clear topics and phrases work best
3. **API Keys**: Use Pexels API for professional stock images
4. **Review Keywords**: Check `keywords.json` after processing to improve matching
5. **Test Settings**: Try different intervals and effect combinations

## 📝 Technical Details

### Speech Recognition
- Uses OpenAI Whisper "base" model (74M parameters)
- Supports 99+ languages (set to English by default)
- Includes word-level timestamps for precise synchronization

### Image Sources
1. **Pexels** (with API key): High-quality stock photos
2. **Pixabay** (with API key): Free stock images
3. **Unsplash** (fallback): Random relevant images
4. **Lorem Picsum** (last resort): Generic placeholder images

### Video Processing
- Maintains original video quality
- Uses H.264 codec for broad compatibility
- Preserves original audio
- Non-destructive editing (original file unchanged)

## 🤝 Contributing

Feel free to modify and extend this project:
- Add new animation effects in `effects_manager.py`
- Integrate new image sources in `image_downloader.py`
- Improve keyword extraction in `video_editor.py`

## 📄 License

This project is for educational purposes. Ensure you have rights to use:
- Your source video content
- Downloaded images (check source licenses)
- Generated content

## 🙋 Support

For issues:
1. Check the troubleshooting section
2. Review generated JSON files for debugging
3. Check console output for specific errors

## 🎉 Example Workflow

```bash
# 1. Install dependencies (first time only)
pip install -r requirements.txt

# 2. Add your video to the folder
# 3. (Optional) Add API keys to .env file

# 4. Run the editor
python run_editor.py

# 5. Wait for processing (5-15 minutes depending on video length)

# 6. Enjoy your edited video!
```

---

**Happy Editing! 🎬✨**

Made with ❤️ By HASEEB KALOYA
