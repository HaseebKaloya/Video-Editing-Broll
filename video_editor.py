"""
Automated Video Editor with Speech Recognition and B-Roll
This script automatically edits educational videos by:
1. Transcribing speech using Whisper AI
2. Identifying key phrases and topics
3. Adding relevant images/animations every 5-15 seconds
4. Applying color grading and effects
"""

import os
import sys
import json
import re
from pathlib import Path
import whisper
import torch
from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip, 
    TextClip, concatenate_videoclips, AudioFileClip,
    ColorClip, vfx
)
from moviepy.video.fx.all import fadein, fadeout, resize
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2
from image_downloader import ImageDownloader
from effects_manager import EffectsManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VideoEditor:
    def __init__(self, video_path, output_path="edited_video.mp4"):
        self.video_path = video_path
        self.output_path = output_path
        self.video = None
        self.transcript = []
        self.keywords = []
        self.image_downloader = ImageDownloader()
        self.effects_manager = EffectsManager()
        
        # Load Whisper model
        print("Loading Whisper AI model for speech recognition...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = whisper.load_model("base", device=device)
        print(f"Model loaded on {device}")
        
    def load_video(self):
        """Load the video file"""
        print(f"Loading video: {self.video_path}")
        self.video = VideoFileClip(self.video_path)
        print(f"Video loaded: {self.video.duration:.2f}s, {self.video.fps} fps")
        
    def transcribe_audio(self):
        """Transcribe audio using Whisper AI"""
        print("Extracting and transcribing audio...")
        
        # Extract audio temporarily
        temp_audio = "temp_audio.wav"
        self.video.audio.write_audiofile(temp_audio, verbose=False, logger=None)
        
        # Transcribe with Whisper
        result = self.whisper_model.transcribe(
            temp_audio, 
            language="en",
            word_timestamps=True,
            verbose=False
        )
        
        # Clean up
        os.remove(temp_audio)
        
        # Store segments with timestamps
        self.transcript = result['segments']
        
        # Save transcript
        with open('transcript.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"Transcription complete: {len(self.transcript)} segments")
        return self.transcript
    
    def extract_keywords(self):
        """Extract key phrases and topics from transcript"""
        print("Extracting keywords and topics...")
        
        # Health/exercise related keywords to prioritize
        priority_keywords = [
            'exercise', 'workout', 'health', 'fitness', 'muscle',
            'training', 'body', 'nutrition', 'diet', 'sleep',
            'water', 'hydration', 'prostate', 'bladder', 'urinate',
            'night', 'pee', 'kidney', 'doctor', 'medical'
        ]
        
        keywords_with_time = []
        
        for segment in self.transcript:
            text = segment['text'].lower()
            start_time = segment['start']
            end_time = segment['end']
            
            # Extract important phrases (2-4 words)
            words = re.findall(r'\b\w+\b', text)
            
            # Single important words
            for word in words:
                if word in priority_keywords or len(word) > 5:
                    keywords_with_time.append({
                        'keyword': word,
                        'time': start_time,
                        'duration': end_time - start_time,
                        'context': segment['text']
                    })
            
            # Multi-word phrases
            for i in range(len(words) - 1):
                phrase = ' '.join(words[i:i+2])
                if any(kw in phrase for kw in priority_keywords):
                    keywords_with_time.append({
                        'keyword': phrase,
                        'time': start_time,
                        'duration': end_time - start_time,
                        'context': segment['text']
                    })
        
        self.keywords = keywords_with_time
        
        # Save keywords
        with open('keywords.json', 'w', encoding='utf-8') as f:
            json.dump(keywords_with_time, f, indent=2, ensure_ascii=False)
            
        print(f"Extracted {len(keywords_with_time)} keywords/phrases")
        return keywords_with_time
    
    def plan_broll_insertions(self, min_interval=5, max_interval=15):
        """Plan where to insert B-roll images (every 5-15 seconds)"""
        print(f"Planning B-roll insertions (every {min_interval}-{max_interval}s)...")
        
        duration = self.video.duration
        insertions = []
        current_time = 2  # Start after 2 seconds
        
        while current_time < duration - 3:
            # Find relevant keyword near this time
            relevant_keywords = [
                kw for kw in self.keywords 
                if abs(kw['time'] - current_time) < 3
            ]
            
            if relevant_keywords:
                # Use the closest keyword
                keyword = min(relevant_keywords, key=lambda k: abs(k['time'] - current_time))
            else:
                # Use general topic
                keyword = {'keyword': 'health exercise', 'context': 'health'}
            
            insertions.append({
                'time': current_time,
                'duration': np.random.uniform(3, 6),  # B-roll duration 3-6 seconds
                'keyword': keyword['keyword'],
                'context': keyword.get('context', '')
            })
            
            # Next insertion in 5-15 seconds
            current_time += np.random.uniform(min_interval, max_interval)
        
        print(f"Planned {len(insertions)} B-roll insertions")
        
        # Save plan
        with open('broll_plan.json', 'w', encoding='utf-8') as f:
            json.dump(insertions, f, indent=2, ensure_ascii=False)
            
        return insertions
    
    def download_images(self, insertions):
        """Download relevant images for each insertion"""
        print("Downloading relevant images...")
        
        downloaded = []
        for i, insertion in enumerate(insertions):
            print(f"Downloading image {i+1}/{len(insertions)}: {insertion['keyword']}")
            
            image_path = self.image_downloader.download_image(
                insertion['keyword'],
                f"image_{i:03d}.jpg"
            )
            
            if image_path:
                insertion['image_path'] = image_path
                downloaded.append(insertion)
            else:
                print(f"  Warning: Could not download image for '{insertion['keyword']}'")
        
        print(f"Successfully downloaded {len(downloaded)}/{len(insertions)} images")
        return downloaded
    
    def apply_color_grading(self, clip):
        """Apply professional color grading"""
        def color_grade(get_frame, t):
            frame = get_frame(t)
            
            # Convert to PIL for processing
            img = Image.fromarray(frame)
            
            # Enhance colors
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2)  # Increase saturation by 20%
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.15)  # Increase contrast
            
            # Enhance brightness slightly
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.05)
            
            # Slight sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            return np.array(img)
        
        return clip.fl(color_grade)
    
    def create_broll_overlay(self, image_path, duration, position='right', effect='slide'):
        """Create a B-roll image overlay with animations"""
        # Load and prepare image
        img_clip = ImageClip(image_path).set_duration(duration)
        
        # Resize to fit in frame corner/side (30% of video width)
        target_width = int(self.video.w * 0.35)
        img_clip = img_clip.resize(width=target_width)
        
        # Add border and shadow effect
        img_clip = self.effects_manager.add_border_shadow(img_clip)
        
        # Add animation based on effect type
        if effect == 'slide':
            img_clip = self.effects_manager.slide_in_animation(
                img_clip, position, self.video.w, self.video.h
            )
        elif effect == 'zoom':
            img_clip = self.effects_manager.zoom_animation(img_clip)
        elif effect == 'fade':
            img_clip = img_clip.crossfadein(0.5).crossfadeout(0.5)
        
        return img_clip
    
    def add_text_animation(self, text, start_time, duration=3):
        """Add animated text overlay"""
        txt_clip = TextClip(
            text,
            fontsize=40,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(self.video.w - 100, None)
        ).set_duration(duration).set_start(start_time)
        
        # Position at bottom center
        txt_clip = txt_clip.set_position(('center', self.video.h - 150))
        
        # Add fade in/out
        txt_clip = txt_clip.crossfadein(0.3).crossfadeout(0.3)
        
        return txt_clip
    
    def compose_final_video(self, broll_insertions):
        """Compose the final video with all elements"""
        print("Composing final video...")
        
        # Apply color grading to main video
        print("  Applying color grading...")
        enhanced_video = self.apply_color_grading(self.video)
        
        # Prepare all overlay clips
        overlay_clips = []
        
        # Add B-roll overlays
        print(f"  Adding {len(broll_insertions)} B-roll overlays...")
        for i, insertion in enumerate(broll_insertions):
            if 'image_path' not in insertion:
                continue
                
            position = 'right' if i % 2 == 0 else 'left'
            effect = ['slide', 'zoom', 'fade'][i % 3]
            
            broll_clip = self.create_broll_overlay(
                insertion['image_path'],
                insertion['duration'],
                position=position,
                effect=effect
            ).set_start(insertion['time'])
            
            overlay_clips.append(broll_clip)
        
        # Add text animations for key moments
        print("  Adding text animations...")
        text_moments = [
            seg for i, seg in enumerate(self.transcript) 
            if i % 5 == 0  # Every 5th segment
        ][:5]  # Maximum 5 text overlays
        
        for seg in text_moments:
            # Extract a short, punchy phrase
            text = seg['text'].strip()[:60]  # Max 60 chars
            if text:
                txt_clip = self.add_text_animation(
                    text,
                    seg['start'],
                    min(3, seg['end'] - seg['start'])
                )
                overlay_clips.append(txt_clip)
        
        # Composite everything
        print("  Compositing all layers...")
        final_video = CompositeVideoClip(
            [enhanced_video] + overlay_clips,
            size=(self.video.w, self.video.h)
        )
        
        return final_video
    
    def export_video(self, final_video):
        """Export the final video"""
        print(f"Exporting video to {self.output_path}...")
        print("This may take a while depending on video length...")
        
        final_video.write_videofile(
            self.output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            fps=self.video.fps,
            preset='medium',
            threads=4,
            verbose=False,
            logger=None
        )
        
        print(f"✓ Video exported successfully: {self.output_path}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.video:
            self.video.close()
    
    def process(self):
        """Main processing pipeline"""
        try:
            print("\n" + "="*60)
            print("AUTOMATED VIDEO EDITOR")
            print("="*60 + "\n")
            
            # Step 1: Load video
            self.load_video()
            
            # Step 2: Transcribe audio
            self.transcribe_audio()
            
            # Step 3: Extract keywords
            self.extract_keywords()
            
            # Step 4: Plan B-roll insertions
            insertions = self.plan_broll_insertions(min_interval=5, max_interval=15)
            
            # Step 5: Download images
            insertions = self.download_images(insertions)
            
            # Step 6: Compose final video
            final_video = self.compose_final_video(insertions)
            
            # Step 7: Export
            self.export_video(final_video)
            
            # Cleanup
            self.cleanup()
            
            print("\n" + "="*60)
            print("✓ VIDEO EDITING COMPLETE!")
            print("="*60)
            print(f"\nYour edited video is ready: {self.output_path}")
            
        except Exception as e:
            print(f"\n✗ Error during processing: {str(e)}")
            import traceback
            traceback.print_exc()
            self.cleanup()
            sys.exit(1)


if __name__ == "__main__":
    # Configuration
    VIDEO_FILE = "Men Over 50_ This One Mistake Is Why You Wake Up to Pee at Night!.mp4"
    OUTPUT_FILE = "edited_video_final.mp4"
    
    if not os.path.exists(VIDEO_FILE):
        print(f"Error: Video file not found: {VIDEO_FILE}")
        sys.exit(1)
    
    # Create editor and process
    editor = VideoEditor(VIDEO_FILE, OUTPUT_FILE)
    editor.process()
