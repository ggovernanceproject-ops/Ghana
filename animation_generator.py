#!/usr/bin/env python3
"""
Ghana Lookbook Animation Generator
Generates 4 different animation types to beautify lookbook updates.
Uses gif_builder from slack-gif-creator.
"""

import sys
from pathlib import Path
from typing import List, Optional
import numpy as np
from PIL import Image, ImageDraw
import requests
from io import BytesIO

# Copy gif_builder from slack-gif-creator (adapt as needed)
try:
    from gif_builder import GIFBuilder
except ImportError:
    print("Error: gif_builder.py not found. Copy from skills/examples/slack-gif-creator/core/")
    sys.exit(1)


class AnimationGenerator:
    """Generate all 4 animation types for Ghana lookbook."""
    
    ANIMATION_TYPES = {
        'carousel': 'Stop carousel - multiple images looping',
        'hero_stripe': 'Hero kente stripe - animated pattern flow',
        'social': 'Social media GIF - shareable 15-second loop',
        'transitions': 'Section transitions - smooth image dissolves'
    }
    
    # Ghana lookbook color palette
    COLORS = {
        'forest': (14, 77, 52),
        'forest_dark': (10, 54, 38),
        'gold': (242, 183, 5),
        'terracotta': (181, 71, 27),
        'clay': (140, 58, 22),
        'ink': (27, 24, 18),
        'ivory': (237, 230, 214),
    }
    
    def __init__(self, width: int = 480, height: int = 480, fps: int = 15):
        self.width = width
        self.height = height
        self.fps = fps
        self.builder = GIFBuilder(width, height, fps)
    
    # ============================================================
    # OPTION A: Animated Stop Carousel
    # ============================================================
    def create_carousel(self, image_urls: List[str], duration_per_image: int = 3) -> GIFBuilder:
        """
        Create animated carousel from multiple images.
        Smooth fade transition between images.
        
        Args:
            image_urls: List of Cloudinary URLs
            duration_per_image: Seconds to display each image
        
        Returns:
            GIFBuilder with frames
        """
        print(f"📽️  Creating carousel animation ({len(image_urls)} images)...")
        
        images = []
        for url in image_urls:
            try:
                response = requests.get(url, timeout=10)
                img = Image.open(BytesIO(response.content))
                img = img.convert('RGB').resize((self.width, self.height))
                images.append(img)
            except Exception as e:
                print(f"  ⚠️  Could not load {url}: {e}")
                continue
        
        if not images:
            raise ValueError("No images loaded successfully")
        
        self.builder.clear()
        
        # Add each image with fade transition
        frames_per_image = self.fps * duration_per_image
        for idx, img in enumerate(images):
            # Fade in
            for frame_num in range(10):
                alpha = frame_num / 10
                faded = self._fade_frame(np.array(img), alpha)
                self.builder.add_frame(faded)
            
            # Hold image
            for _ in range(frames_per_image - 20):
                self.builder.add_frame(np.array(img))
            
            # Fade out (except for last image)
            if idx < len(images) - 1:
                for frame_num in range(10):
                    alpha = 1 - (frame_num / 10)
                    faded = self._fade_frame(np.array(img), alpha)
                    self.builder.add_frame(faded)
        
        print(f"  ✓ Carousel ready ({len(self.builder.frames)} frames)")
        return self.builder
    
    # ============================================================
    # OPTION B: Social Media GIF
    # ============================================================
    def create_social_gif(self, image_urls: List[str], stop_name: str = "Ghana") -> GIFBuilder:
        """
        Create shareable social media GIF (15 seconds).
        Includes text overlay with stop name.
        
        Args:
            image_urls: List of Cloudinary URLs (3-5 images)
            stop_name: Stop/location name to display
        
        Returns:
            GIFBuilder with frames
        """
        print(f"📱 Creating social media GIF for '{stop_name}'...")
        
        images = []
        for url in image_urls[:5]:  # Max 5 images
            try:
                response = requests.get(url, timeout=10)
                img = Image.open(BytesIO(response.content))
                img = img.convert('RGB').resize((480, 480))
                images.append(img)
            except Exception as e:
                print(f"  ⚠️  Could not load image: {e}")
                continue
        
        self.builder.clear()
        
        # 15 seconds total = 225 frames at 15 fps
        total_duration = 15
        frames_per_image = (total_duration * self.fps) // len(images)
        
        for idx, img in enumerate(images):
            # Add text overlay
            img_with_text = self._add_text_overlay(
                np.array(img),
                stop_name,
                position='bottom'
            )
            
            # Hold for duration
            for _ in range(frames_per_image):
                self.builder.add_frame(img_with_text)
        
        print(f"  ✓ Social media GIF ready (15 seconds, {len(self.builder.frames)} frames)")
        return self.builder
    
    # ============================================================
    # OPTION C: Hero Kente Stripe Animation
    # ============================================================
    def create_hero_stripe(self, num_stripes: int = 5) -> GIFBuilder:
        """
        Create animated kente stripe pattern for hero section.
        Generates abstract woven pattern animation.
        
        Args:
            num_stripes: Number of color stripes
        
        Returns:
            GIFBuilder with frames
        """
        print(f"🎨 Creating animated kente stripe pattern...")
        
        self.builder = GIFBuilder(self.width, self.height, fps=20)
        self.builder.clear()
        
        stripe_colors = [
            self.COLORS['gold'],
            self.COLORS['terracotta'],
            self.COLORS['forest'],
            self.COLORS['gold'],
            self.COLORS['clay']
        ]
        
        # 30 frames of animated weaving
        for frame_num in range(30):
            frame = self._create_animated_kente_frame(
                stripe_colors,
                frame_num,
                offset=frame_num * 2
            )
            self.builder.add_frame(frame)
        
        print(f"  ✓ Kente animation ready (30 frames)")
        return self.builder
    
    # ============================================================
    # OPTION D: Section Transitions
    # ============================================================
    def create_transitions(self, image_urls: List[str], transition_type: str = 'dissolve') -> GIFBuilder:
        """
        Create smooth transition animations between sections.
        
        Args:
            image_urls: List of Cloudinary URLs
            transition_type: 'dissolve', 'slide', 'fade-scale'
        
        Returns:
            GIFBuilder with frames
        """
        print(f"🔄 Creating {transition_type} transitions ({len(image_urls)} sections)...")
        
        images = []
        for url in image_urls[:8]:  # Max 8 transitions
            try:
                response = requests.get(url, timeout=10)
                img = Image.open(BytesIO(response.content))
                img = img.convert('RGB').resize((self.width, self.height))
                images.append(img)
            except Exception as e:
                print(f"  ⚠️  Could not load image: {e}")
                continue
        
        self.builder.clear()
        
        transition_frames = 15  # 1 second at 15fps
        
        for idx in range(len(images) - 1):
            img1 = np.array(images[idx])
            img2 = np.array(images[idx + 1])
            
            if transition_type == 'dissolve':
                for frame_num in range(transition_frames):
                    alpha = frame_num / transition_frames
                    frame = self._blend_images(img1, img2, alpha)
                    self.builder.add_frame(frame)
            
            elif transition_type == 'slide':
                for frame_num in range(transition_frames):
                    progress = frame_num / transition_frames
                    frame = self._slide_transition(img1, img2, progress)
                    self.builder.add_frame(frame)
            
            elif transition_type == 'fade-scale':
                for frame_num in range(transition_frames):
                    progress = frame_num / transition_frames
                    frame = self._fade_scale_transition(img1, img2, progress)
                    self.builder.add_frame(frame)
        
        print(f"  ✓ Transitions ready ({len(self.builder.frames)} frames)")
        return self.builder
    
    # ============================================================
    # Utility Functions
    # ============================================================
    
    def _fade_frame(self, frame: np.ndarray, alpha: float) -> np.ndarray:
        """Fade frame in/out."""
        white = np.ones_like(frame) * 255
        return (frame * alpha + white * (1 - alpha)).astype(np.uint8)
    
    def _blend_images(self, img1: np.ndarray, img2: np.ndarray, alpha: float) -> np.ndarray:
        """Blend two images together."""
        return (img1 * (1 - alpha) + img2 * alpha).astype(np.uint8)
    
    def _add_text_overlay(self, frame: np.ndarray, text: str, position: str = 'center') -> np.ndarray:
        """Add semi-transparent text overlay."""
        img = Image.fromarray(frame)
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Add semi-transparent background
        overlay_bg = Image.new('RGBA', img.size, (27, 24, 18, 180))  # ink color with 70% opacity
        overlay = Image.alpha_composite(overlay, overlay_bg)
        
        # Draw text
        draw = ImageDraw.Draw(overlay)
        # Position text based on argument
        if position == 'bottom':
            text_y = img.size[1] - 60
        else:
            text_y = img.size[1] // 2
        
        draw.text((40, text_y), text, fill=(242, 183, 5), font=None)  # Gold text
        
        # Composite overlay onto image
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        return np.array(img.convert('RGB'))
    
    def _create_animated_kente_frame(self, colors: List, frame_num: int, offset: int = 0) -> np.ndarray:
        """Create a frame of animated kente weaving pattern."""
        img = Image.new('RGB', (self.width, self.height), self.COLORS['ivory'])
        draw = ImageDraw.Draw(img)
        
        stripe_width = self.width // len(colors)
        
        for idx, color in enumerate(colors):
            x = idx * stripe_width
            
            # Create wave effect
            wave_offset = int(10 * np.sin((frame_num + offset + idx * 30) * 0.2))
            
            # Draw vertical stripe with wave
            for y in range(self.height):
                wave_x = x + wave_offset
                draw.line([(wave_x, y), (wave_x + stripe_width // 2, y)], fill=color)
        
        return np.array(img)
    
    def _slide_transition(self, img1: np.ndarray, img2: np.ndarray, progress: float) -> np.ndarray:
        """Create slide transition from img1 to img2."""
        offset = int(self.width * progress)
        
        result = np.zeros_like(img1)
        # img1 slides out to the left
        result[:, :self.width - offset] = img1[:, offset:]
        # img2 slides in from the right
        result[:, self.width - offset:] = img2[:, :offset]
        
        return result.astype(np.uint8)
    
    def _fade_scale_transition(self, img1: np.ndarray, img2: np.ndarray, progress: float) -> np.ndarray:
        """Create fade + scale transition."""
        # Scale img2 from center
        scale = 0.5 + (progress * 0.5)  # Scale from 0.5x to 1x
        
        img2_pil = Image.fromarray(img2.astype(np.uint8))
        new_size = (int(self.width * scale), int(self.height * scale))
        img2_scaled = img2_pil.resize(new_size)
        
        # Center it
        result = Image.fromarray(img1.astype(np.uint8))
        x = (self.width - new_size[0]) // 2
        y = (self.height - new_size[1]) // 2
        result.paste(img2_scaled, (x, y))
        
        # Fade between
        alpha = progress
        result_faded = Image.blend(
            Image.fromarray(img1.astype(np.uint8)),
            result,
            alpha
        )
        
        return np.array(result_faded)
    
    def save_gif(self, output_path: str, animation_type: str = 'carousel') -> dict:
        """
        Save the current builder's frames as GIF.
        
        Args:
            output_path: Path to save GIF
            animation_type: Type for metadata
        
        Returns:
            Dictionary with GIF info
        """
        return self.builder.save(
            output_path,
            num_colors=128,
            optimize_for_emoji=False,
            remove_duplicates=True
        )


def main():
    """CLI for testing animation generation."""
    print("🎨 Ghana Lookbook Animation Generator")
    print("=" * 50)
    
    # Example: Create carousel from sample Cloudinary URLs
    # In production, these come from Firestore + Cloudinary
    sample_urls = [
        "https://res.cloudinary.com/demo/image/fetch/w_480/https://images.unsplash.com/photo-1606216174052-f2343c5c7d2d?w=480",
        "https://res.cloudinary.com/demo/image/fetch/w_480/https://images.unsplash.com/photo-1606216174052-f2343c5c7d2d?w=480",
    ]
    
    gen = AnimationGenerator()
    
    # Test carousel
    print("\n1️⃣  Testing Carousel Animation...")
    try:
        gen.create_carousel(sample_urls, duration_per_image=2)
        info = gen.save_gif('/tmp/test_carousel.gif')
        print(f"  Saved to: {info['path']}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test kente stripe
    print("\n2️⃣  Testing Kente Stripe Animation...")
    try:
        gen.create_hero_stripe()
        info = gen.save_gif('/tmp/test_kente.gif')
        print(f"  Saved to: {info['path']}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n✅ Animation types are ready!")
    print("Use AnimationGenerator class in your backend to create animations on-demand.")


if __name__ == '__main__':
    main()
