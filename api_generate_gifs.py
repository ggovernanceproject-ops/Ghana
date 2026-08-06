#!/usr/bin/env python3
"""
Vercel Serverless Function: Generate Animated GIFs
Handles requests to create animations from Cloudinary images.
Deploy to Vercel Functions at /api/generate-gifs
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict
import requests
from io import BytesIO
import numpy as np
from PIL import Image

# Add gif_builder to path (installed via requirements.txt)
try:
    from gif_builder import GIFBuilder
except ImportError:
    print("Error: gif_builder module not found. Install via: pip install gif_builder")
    sys.exit(1)


def download_image(url: str, timeout: int = 10) -> Image.Image:
    """Download image from Cloudinary URL."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img.convert('RGB')
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        raise


def create_carousel_gif(images: List[Image.Image], output_path: str) -> Dict:
    """Create animated carousel from images."""
    builder = GIFBuilder(width=480, height=480, fps=15)
    
    for idx, img in enumerate(images):
        # Resize
        img = img.resize((480, 480), Image.Resampling.LANCZOS)
        
        # Fade in (10 frames)
        for frame_num in range(10):
            alpha = frame_num / 10
            faded = fade_frame(np.array(img), alpha)
            builder.add_frame(faded)
        
        # Hold (45 frames = 3 seconds)
        for _ in range(45):
            builder.add_frame(np.array(img))
        
        # Fade out (10 frames, except last)
        if idx < len(images) - 1:
            for frame_num in range(10):
                alpha = 1 - (frame_num / 10)
                faded = fade_frame(np.array(img), alpha)
                builder.add_frame(faded)
    
    return builder.save(output_path, num_colors=128, remove_duplicates=True)


def create_social_gif(images: List[Image.Image], output_path: str, stop_name: str = "Ghana") -> Dict:
    """Create 15-second social media GIF."""
    builder = GIFBuilder(width=480, height=480, fps=15)
    
    total_frames = 15 * 15  # 15 seconds at 15fps
    frames_per_image = total_frames // len(images)
    
    for img in images:
        img = img.resize((480, 480), Image.Resampling.LANCZOS)
        
        # Add text overlay
        img_with_text = add_text_overlay(img, stop_name)
        
        # Hold for duration
        for _ in range(frames_per_image):
            builder.add_frame(np.array(img_with_text))
    
    return builder.save(output_path, num_colors=128, remove_duplicates=True)


def create_transitions_gif(images: List[Image.Image], output_path: str) -> Dict:
    """Create smooth dissolve transitions between images."""
    builder = GIFBuilder(width=480, height=480, fps=15)
    
    for idx in range(len(images) - 1):
        img1 = images[idx].resize((480, 480), Image.Resampling.LANCZOS)
        img2 = images[idx + 1].resize((480, 480), Image.Resampling.LANCZOS)
        
        img1_arr = np.array(img1)
        img2_arr = np.array(img2)
        
        # 15 frames of dissolve (1 second at 15fps)
        for frame_num in range(15):
            alpha = frame_num / 15
            blended = blend_images(img1_arr, img2_arr, alpha)
            builder.add_frame(blended)
    
    return builder.save(output_path, num_colors=128, remove_duplicates=True)


def create_hero_stripe_gif(output_path: str) -> Dict:
    """Create animated kente pattern for hero."""
    builder = GIFBuilder(width=480, height=480, fps=20)
    
    colors = [
        (242, 183, 5),      # gold
        (181, 71, 27),      # terracotta
        (14, 77, 52),       # forest
        (242, 183, 5),      # gold
        (140, 58, 22)       # clay
    ]
    
    for frame_num in range(30):
        frame = create_animated_kente_frame(colors, frame_num)
        builder.add_frame(frame)
    
    return builder.save(output_path, num_colors=128, remove_duplicates=True)


# ============================================================
# Utility Functions
# ============================================================

def fade_frame(frame: np.ndarray, alpha: float) -> np.ndarray:
    """Fade frame in/out."""
    white = np.ones_like(frame) * 255
    return (frame * alpha + white * (1 - alpha)).astype(np.uint8)


def blend_images(img1: np.ndarray, img2: np.ndarray, alpha: float) -> np.ndarray:
    """Blend two images together."""
    return (img1 * (1 - alpha) + img2 * alpha).astype(np.uint8)


def add_text_overlay(img: Image.Image, text: str) -> Image.Image:
    """Add semi-transparent text overlay to image."""
    from PIL import ImageDraw
    
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    
    # Semi-transparent background
    overlay_bg = Image.new('RGBA', img.size, (27, 24, 18, 180))
    overlay = Image.alpha_composite(overlay, overlay_bg)
    
    # Draw text
    draw = ImageDraw.Draw(overlay)
    text_y = img.size[1] - 60
    draw.text((40, text_y), text, fill=(242, 183, 5), font=None)
    
    # Composite
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    return img.convert('RGB')


def create_animated_kente_frame(colors: List, frame_num: int) -> np.ndarray:
    """Create a frame of animated kente pattern."""
    img = Image.new('RGB', (480, 480), (237, 230, 214))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    stripe_width = 480 // len(colors)
    
    for idx, color in enumerate(colors):
        x = idx * stripe_width
        wave_offset = int(10 * np.sin((frame_num + idx * 30) * 0.2))
        
        for y in range(480):
            wave_x = x + wave_offset
            draw.line([(wave_x, y), (wave_x + stripe_width // 2, y)], fill=color)
    
    return np.array(img)


# ============================================================
# Vercel Handler
# ============================================================

def handler(request):
    """Vercel serverless function handler."""
    
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(request.body)
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON'})
        }
    
    animation_data = body.get('animation_data', {})
    cloudinary_name = body.get('cloudinary_name')
    
    if not cloudinary_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing cloudinary_name'})
        }
    
    result_gifs = {}
    
    try:
        # Process each stop
        for stop_key, stop_data in animation_data.items():
            if stop_key in ['selectedAnimation', 'lastUpdated']:
                continue
            
            if not isinstance(stop_data, dict):
                continue
            
            animation_type = stop_data.get('animation_type', 'carousel')
            image_urls = stop_data.get('image_urls', [])
            
            # Generate GIF based on type
            if animation_type == 'hero_stripe':
                # No images needed
                gif_path = f'/tmp/{stop_key}_{animation_type}.gif'
                create_hero_stripe_gif(gif_path)
            elif image_urls:
                # Download images
                try:
                    images = [download_image(url) for url in image_urls[:5]]
                except Exception as e:
                    print(f"Error downloading images for {stop_key}: {e}")
                    continue
                
                gif_path = f'/tmp/{stop_key}_{animation_type}.gif'
                
                if animation_type == 'carousel':
                    create_carousel_gif(images, gif_path)
                elif animation_type == 'social':
                    create_social_gif(images, gif_path, stop_key.replace('_', ' ').title())
                elif animation_type == 'transitions':
                    create_transitions_gif(images, gif_path)
            else:
                continue
            
            # Upload to Cloudinary
            gif_url = upload_to_cloudinary(gif_path, stop_key, cloudinary_name)
            if gif_url:
                result_gifs[stop_key] = gif_url
            
            # Cleanup
            if os.path.exists(gif_path):
                os.remove(gif_path)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'gifs': result_gifs
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


def upload_to_cloudinary(file_path: str, stop_key: str, cloud_name: str) -> str:
    """Upload generated GIF to Cloudinary."""
    
    # Using Cloudinary unsigned upload (requires unsigned upload preset)
    upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'upload_preset': 'ghana-lookbook',  # Must match your upload preset
                'folder': 'ghana-lookbook',
                'public_id': f'stop-{stop_key}'
            }
            
            response = requests.post(upload_url, files=files, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('secure_url')
    
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None


# For local testing
if __name__ == '__main__':
    class MockRequest:
        method = 'POST'
        body = json.dumps({
            'animation_data': {
                'castles': {
                    'animation_type': 'hero_stripe',
                    'image_urls': []
                }
            },
            'cloudinary_name': 'demo'
        })
    
    result = handler(MockRequest())
    print(json.dumps(result, indent=2))
