from typing import Optional, Dict
from pathlib import Path
from datetime import datetime
import os

from langchain.tools import tool
from google import genai
from google.genai import types

from app.core.config import settings


# Platform-specific aspect ratios for optimal display
ASPECT_RATIOS: Dict[str, str] = {
    "instagram": "1:1",      # Square posts
    "linkedin": "1:1",       # Square posts
    "twitter": "16:9",       # Wide format
    "facebook": "4:3",       # Standard format
    "tiktok": "9:16",        # Vertical video format
    "youtube": "16:9",       # Widescreen
    "pinterest": "2:3",      # Vertical pins
}


@tool
def generate_social_image(
    prompt: str,
    platform: str = "instagram"
) -> str:
    """
    Generate AI image for social media post using Google Imagen 4.0.
    
    Use this tool when users request images, visuals, graphics, or pictures for their posts.
    
    Args:
        prompt: Description of the image to generate (e.g., "modern coffee shop with customers")
        platform: Target social platform - instagram, facebook, linkedin, twitter, tiktok, youtube, pinterest
    
    Returns:
        Success message with file path and image details
    """
    try:
        # Get API key
        api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "❌ Error: Google API key not configured. Please set GOOGLE_API_KEY in .env file."
        
        # Initialize client
        client = genai.Client(api_key=api_key)
        model = getattr(settings, 'imagen_model', 'imagen-4.0-generate-001')
        
        # Create output directory
        output_dir = getattr(settings, 'image_output_dir', 'generated_images')
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get aspect ratio for platform
        aspect_ratio = ASPECT_RATIOS.get(platform.lower(), "1:1")
        
        # Generate image using Imagen API
        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,  # Cost-efficient: generate 1 image
                aspect_ratio=aspect_ratio
            )
        )
        
        # Extract image bytes
        image_bytes = response.generated_images[0].image.image_bytes
        
        # Create unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{platform}_{timestamp}.png"
        filepath = output_path / filename
        
        # Save image to file
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        
        # For hackathon: use local URL instead of Firebase Storage
        # Backend serves images at /generated_images/{filename}
        local_url = f"http://localhost:8000/generated_images/{filename}"
        
        # Return success message with image URL
        result = f"""✅ **Image Generated Successfully!**

![Generated Image]({local_url})

📱 **Platform:** {platform.title()}
📐 **Aspect Ratio:** {aspect_ratio}
🎨 **Model:** Google Imagen 4.0"""
        
        return result
        
    except Exception as e:
        return f"❌ **Image generation failed:** {str(e)}\n\nPlease try again or check your API key configuration."


def should_generate_image(user_input: str) -> bool:
    """
    Utility function to detect if user is requesting image generation.
    
    Args:
        user_input: User's message
        
    Returns:
        bool: True if image generation keywords detected
    """
    image_keywords = [
        "image", "picture", "photo", "visual", "graphic", 
        "illustration", "poster", "thumbnail", "banner",
        "cover", "design", "artwork"
    ]
    
    user_input_lower = user_input.lower()
    return any(keyword in user_input_lower for keyword in image_keywords)
