"""
Image Downloader Module
Downloads relevant images from Pexels and Pixabay APIs
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()


class ImageDownloader:
    def __init__(self, output_dir="broll_images"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(exist_ok=True)
        
        self.pexels_api_key = os.getenv('PEXELS_API_KEY', '')
        self.pixabay_api_key = os.getenv('PIXABAY_API_KEY', '')
        
        # Cache to avoid duplicate downloads
        self.cache = {}
        
    def search_pexels(self, query, per_page=1):
        """Search Pexels for images"""
        if not self.pexels_api_key:
            return None
            
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.pexels_api_key}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "landscape"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('photos'):
                # Return medium-sized image URL
                return data['photos'][0]['src']['large']
        except Exception as e:
            print(f"  Pexels search failed: {e}")
        
        return None
    
    def search_pixabay(self, query):
        """Search Pixabay for images"""
        if not self.pixabay_api_key:
            return None
            
        url = "https://pixabay.com/api/"
        params = {
            "key": self.pixabay_api_key,
            "q": query,
            "image_type": "photo",
            "orientation": "horizontal",
            "per_page": 3
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('hits'):
                return data['hits'][0]['largeImageURL']
        except Exception as e:
            print(f"  Pixabay search failed: {e}")
        
        return None
    
    def get_fallback_image(self, query):
        """Get fallback image using Lorem Picsum with relevant search"""
        # Use unsplash source as fallback
        try:
            # Map keywords to categories
            category_map = {
                'exercise': 'fitness',
                'workout': 'fitness',
                'health': 'health',
                'doctor': 'medical',
                'sleep': 'rest',
                'water': 'nature',
                'food': 'food',
                'nutrition': 'food'
            }
            
            category = 'health'  # default
            for key, cat in category_map.items():
                if key in query.lower():
                    category = cat
                    break
            
            # Use Unsplash Source API
            url = f"https://source.unsplash.com/800x600/?{category},{query.replace(' ', ',')}"
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                return response.url
        except Exception as e:
            print(f"  Fallback image failed: {e}")
        
        # Last resort: use Lorem Picsum
        return f"https://picsum.photos/800/600?random={abs(hash(query))}"
    
    def download_image(self, query, filename):
        """Download an image based on query"""
        # Check cache
        if query in self.cache:
            return self.cache[query]
        
        output_path = os.path.join(self.output_dir, filename)
        
        # If file already exists, return it
        if os.path.exists(output_path):
            self.cache[query] = output_path
            return output_path
        
        # Try different sources
        image_url = None
        
        # Try Pexels first
        if self.pexels_api_key:
            image_url = self.search_pexels(query)
            time.sleep(0.5)  # Rate limiting
        
        # Try Pixabay if Pexels failed
        if not image_url and self.pixabay_api_key:
            image_url = self.search_pixabay(query)
            time.sleep(0.5)
        
        # Use fallback if both failed
        if not image_url:
            print(f"  Using fallback image source for: {query}")
            image_url = self.get_fallback_image(query)
        
        # Download image
        try:
            response = requests.get(image_url, timeout=15, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"  ✓ Downloaded: {filename}")
            self.cache[query] = output_path
            return output_path
            
        except Exception as e:
            print(f"  ✗ Download failed for {query}: {e}")
            return None
    
    def clear_cache(self):
        """Clear downloaded images"""
        import shutil
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        Path(self.output_dir).mkdir(exist_ok=True)
        self.cache = {}


if __name__ == "__main__":
    # Test the downloader
    downloader = ImageDownloader()
    
    test_queries = [
        "exercise fitness",
        "healthy sleep",
        "doctor medical"
    ]
    
    print("Testing Image Downloader...")
    for i, query in enumerate(test_queries):
        print(f"\nDownloading: {query}")
        path = downloader.download_image(query, f"test_{i}.jpg")
        if path:
            print(f"Success: {path}")
        else:
            print("Failed")
