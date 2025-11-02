"""
Watermark service for adding GradGen.AI watermark to free tier photos
"""

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class WatermarkService:
    """Service for adding watermarks to generated images"""

    # Watermark configuration
    WATERMARK_TEXT = "GRADGEN.AI"
    WATERMARK_OPACITY = 0.35  # 35% opacity - visible but not overwhelming
    WATERMARK_FONT_SIZE_RATIO = 0.15  # 15% of image height (large but elegant)
    WATERMARK_SPACING_RATIO = 2.2  # More spacing for cleaner look

    @classmethod
    def add_watermark(
        cls,
        image_bytes: bytes,
        position: str = "bottom_right",
        opacity: float = None,
    ) -> bytes:
        """
        Add watermark to an image

        Args:
            image_bytes: Original image bytes
            position: Where to place watermark ("bottom_right", "bottom_left", "center", "diagonal")
            opacity: Override default opacity (0.0 to 1.0)

        Returns:
            Watermarked image bytes
        """
        try:
            # Load image
            image = Image.open(BytesIO(image_bytes))

            # Convert to RGBA if not already
            if image.mode != "RGBA":
                image = image.convert("RGBA")

            # Calculate font size based on image dimensions
            font_size = int(image.height * cls.WATERMARK_FONT_SIZE_RATIO)

            # Try to load elegant fonts in order of preference
            font_paths = [
                # macOS elegant fonts
                "/System/Library/Fonts/Supplemental/Futura.ttc",
                "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
                "/System/Library/Fonts/HelveticaNeue.ttc",
                "/System/Library/Fonts/SFNSText.ttf",
                # Linux elegant fonts
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                # Railway/common locations
                "/usr/share/fonts/google-noto/NotoSans-Bold.ttf",
                "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            ]

            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    logger.info(f"Using watermark font: {font_path}")
                    break
                except:
                    continue

            if font is None:
                # Last resort fallback
                font = ImageFont.load_default()
                logger.warning("Using default font for watermark")

            # Get text bounding box (using a temporary draw object)
            temp_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
            bbox = temp_draw.textbbox((0, 0), cls.WATERMARK_TEXT, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Calculate opacity (0-255)
            opacity_value = opacity if opacity is not None else cls.WATERMARK_OPACITY
            alpha = int(255 * opacity_value)

            # Create diagonal repeating pattern across entire image
            # Calculate spacing between watermarks
            spacing_x = int(text_width * cls.WATERMARK_SPACING_RATIO)
            spacing_y = int(text_height * cls.WATERMARK_SPACING_RATIO)

            # Rotate the entire watermark layer for diagonal effect
            # We'll create a larger canvas to accommodate rotation
            diagonal_size = int((image.width ** 2 + image.height ** 2) ** 0.5)
            rotated_layer = Image.new("RGBA", (diagonal_size, diagonal_size), (0, 0, 0, 0))
            rotated_draw = ImageDraw.Draw(rotated_layer)

            # Subtle shadow for depth (softer than harsh outline)
            shadow_offset = max(2, font_size // 40)
            shadow_alpha = int(alpha * 0.6)  # Shadow is slightly more transparent

            # Fill the rotated canvas with repeating watermarks
            for y_pos in range(-diagonal_size // 2, diagonal_size * 2, spacing_y):
                for x_pos in range(-diagonal_size // 2, diagonal_size * 2, spacing_x):
                    # Draw subtle shadow (bottom-right offset for depth)
                    rotated_draw.text(
                        (x_pos + shadow_offset, y_pos + shadow_offset),
                        cls.WATERMARK_TEXT,
                        fill=(0, 0, 0, shadow_alpha),
                        font=font
                    )

                    # Draw main white text with slight transparency
                    rotated_draw.text(
                        (x_pos, y_pos),
                        cls.WATERMARK_TEXT,
                        fill=(255, 255, 255, alpha),
                        font=font
                    )

            # Rotate the layer by 45 degrees (diagonal)
            rotated_layer = rotated_layer.rotate(45, expand=False, fillcolor=(0, 0, 0, 0))

            # Crop to original image size from center
            left = (diagonal_size - image.width) // 2
            top = (diagonal_size - image.height) // 2
            rotated_layer = rotated_layer.crop((left, top, left + image.width, top + image.height))

            # Composite onto watermark layer
            watermark_layer = rotated_layer

            # Composite watermark onto original image
            watermarked = Image.alpha_composite(image, watermark_layer)

            # Convert back to RGB if original was RGB
            if watermarked.mode == "RGBA":
                # Create white background
                background = Image.new("RGB", watermarked.size, (255, 255, 255))
                background.paste(watermarked, mask=watermarked.split()[3])  # Use alpha channel as mask
                watermarked = background

            # Save to bytes
            output = BytesIO()
            watermarked.save(output, format="PNG", quality=95)
            output.seek(0)

            logger.info(f"Watermark added successfully at position: {position}")
            return output.getvalue()

        except Exception as e:
            logger.error(f"Failed to add watermark: {str(e)}")
            # Return original image if watermarking fails
            return image_bytes

    @classmethod
    def remove_watermark_metadata(cls, image_bytes: bytes) -> bytes:
        """
        Remove watermark by re-encoding without watermark layer
        (This is a placeholder - actual watermark removal would require the original)

        For premium tier, we simply return the unwatermarked original image
        """
        # In practice, we store both watermarked and unwatermarked versions
        # This method would fetch the unwatermarked version from storage
        return image_bytes

    @classmethod
    def should_watermark(cls, tier: str) -> bool:
        """Determine if an image should be watermarked based on tier"""
        return tier == "free"


# Convenience function
def add_watermark_to_image(
    image_bytes: bytes,
    tier: str = "free",
    position: str = "bottom_right"
) -> bytes:
    """
    Add watermark to image if it's free tier

    Args:
        image_bytes: Image data
        tier: "free" or "premium"
        position: Watermark position

    Returns:
        Watermarked image (free tier) or original image (premium tier)
    """
    if WatermarkService.should_watermark(tier):
        return WatermarkService.add_watermark(image_bytes, position=position)
    return image_bytes
