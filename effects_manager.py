"""
Effects Manager Module
Handles visual effects and animations for video editing
"""

import numpy as np
from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip
from moviepy.video.fx.all import fadein, fadeout, resize
from PIL import Image, ImageDraw, ImageFilter
import cv2


class EffectsManager:
    def __init__(self):
        pass
    
    def add_border_shadow(self, clip, border_width=8, shadow_offset=10):
        """Add border and shadow effect to image clip"""
        def add_frame(get_frame, t):
            frame = get_frame(t)
            
            # Convert to PIL
            img = Image.fromarray(frame)
            
            # Create new image with space for border and shadow
            new_width = img.width + border_width * 2 + shadow_offset
            new_height = img.height + border_width * 2 + shadow_offset
            
            # Create canvas with transparent background
            canvas = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
            
            # Draw shadow
            shadow = Image.new('RGBA', (img.width + border_width*2, img.height + border_width*2), (0, 0, 0, 100))
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
            canvas.paste(shadow, (shadow_offset, shadow_offset), shadow)
            
            # Draw white border
            border_img = Image.new('RGB', (img.width + border_width*2, img.height + border_width*2), (255, 255, 255))
            canvas.paste(border_img, (0, 0))
            
            # Paste original image
            canvas.paste(img, (border_width, border_width))
            
            # Convert back to RGB
            if canvas.mode == 'RGBA':
                background = Image.new('RGB', canvas.size, (255, 255, 255))
                background.paste(canvas, mask=canvas.split()[3])
                canvas = background
            
            return np.array(canvas)
        
        return clip.fl(add_frame)
    
    def slide_in_animation(self, clip, position='right', video_width=1920, video_height=1080):
        """Create slide-in animation from side"""
        duration = clip.duration
        
        if position == 'right':
            # Slide in from right
            start_x = video_width
            end_x = video_width - clip.w - 30
            y_pos = video_height // 2 - clip.h // 2
            
            def pos_func(t):
                progress = min(t / (duration * 0.3), 1)  # Slide in during first 30%
                x = start_x - (start_x - end_x) * self._ease_out_cubic(progress)
                return (int(x), y_pos)
                
        else:  # left
            start_x = -clip.w
            end_x = 30
            y_pos = video_height // 2 - clip.h // 2
            
            def pos_func(t):
                progress = min(t / (duration * 0.3), 1)
                x = start_x + (end_x - start_x) * self._ease_out_cubic(progress)
                return (int(x), y_pos)
        
        clip = clip.set_position(pos_func)
        
        # Add fade in/out
        clip = clip.crossfadein(0.3).crossfadeout(0.3)
        
        return clip
    
    def zoom_animation(self, clip):
        """Create zoom-in animation"""
        duration = clip.duration
        
        def resize_func(t):
            progress = min(t / duration, 1)
            scale = 0.8 + 0.2 * self._ease_out_cubic(progress)  # Zoom from 80% to 100%
            return scale
        
        clip = clip.resize(resize_func)
        clip = clip.set_position('center')
        clip = clip.crossfadein(0.5).crossfadeout(0.5)
        
        return clip
    
    def fade_animation(self, clip):
        """Simple fade in and out"""
        return clip.crossfadein(0.5).crossfadeout(0.5)
    
    def picture_in_picture(self, clip, position='bottom-right', video_width=1920, video_height=1080):
        """Position clip as picture-in-picture"""
        margin = 30
        
        positions = {
            'top-left': (margin, margin),
            'top-right': (video_width - clip.w - margin, margin),
            'bottom-left': (margin, video_height - clip.h - margin),
            'bottom-right': (video_width - clip.w - margin, video_height - clip.h - margin),
            'center': ('center', 'center')
        }
        
        clip = clip.set_position(positions.get(position, positions['bottom-right']))
        return clip
    
    def ken_burns_effect(self, clip, zoom_ratio=1.2):
        """Create Ken Burns effect (slow zoom and pan)"""
        duration = clip.duration
        
        def make_frame(t):
            progress = t / duration
            
            # Zoom in gradually
            scale = 1.0 + (zoom_ratio - 1.0) * progress
            
            # Get frame
            frame = clip.get_frame(t)
            h, w = frame.shape[:2]
            
            # Calculate crop dimensions
            new_h = int(h / scale)
            new_w = int(w / scale)
            
            # Pan from top-left to bottom-right
            top = int((h - new_h) * progress)
            left = int((w - new_w) * progress)
            
            # Crop
            cropped = frame[top:top+new_h, left:left+new_w]
            
            # Resize back to original size
            resized = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
            
            return resized
        
        return clip.fl(make_frame)
    
    def add_vignette(self, clip, intensity=0.3):
        """Add vignette effect"""
        def apply_vignette(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Create vignette mask
            kernel_x = cv2.getGaussianKernel(w, w/2)
            kernel_y = cv2.getGaussianKernel(h, h/2)
            kernel = kernel_y * kernel_x.T
            mask = kernel / kernel.max()
            
            # Apply intensity
            mask = 1 - (1 - mask) * intensity
            mask = np.dstack([mask] * 3)
            
            # Apply to frame
            vignetted = (frame * mask).astype(np.uint8)
            return vignetted
        
        return clip.fl(apply_vignette)
    
    def pulse_animation(self, clip):
        """Create pulsing animation"""
        duration = clip.duration
        
        def resize_func(t):
            # Pulse between 95% and 100%
            pulse = 0.975 + 0.025 * np.sin(2 * np.pi * t * 2)  # 2 Hz pulse
            return pulse
        
        return clip.resize(resize_func).set_position('center')
    
    @staticmethod
    def _ease_out_cubic(t):
        """Easing function for smooth animations"""
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def _ease_in_out_cubic(t):
        """Ease in-out cubic function"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2


if __name__ == "__main__":
    print("Effects Manager module loaded successfully")
    print("Available effects:")
    print("  - add_border_shadow")
    print("  - slide_in_animation")
    print("  - zoom_animation")
    print("  - fade_animation")
    print("  - picture_in_picture")
    print("  - ken_burns_effect")
    print("  - add_vignette")
    print("  - pulse_animation")
