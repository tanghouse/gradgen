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
    WATERMARK_TEXT = "GradGen.AI"
    WATERMARK_OPACITY = 0.5  # 50% opacity for diagonal pattern
    WATERMARK_FONT_SIZE_RATIO = 0.12  # 12% of image height (very large)
    WATERMARK_SPACING_RATIO = 1.5  # Spacing between diagonal repeats

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

            # Try to load a good font, fall back to default if not available
            try:
                # Try common system fonts
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                except:
                    # Fallback to default PIL font
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

            # Draw outline for better visibility
            outline_offset = max(3, font_size // 30)

            # Fill the rotated canvas with repeating watermarks
            for y_pos in range(-diagonal_size // 2, diagonal_size * 2, spacing_y):
                for x_pos in range(-diagonal_size // 2, diagonal_size * 2, spacing_x):
                    # Draw black outline
                    for offset_x in [-outline_offset, 0, outline_offset]:
                        for offset_y in [-outline_offset, 0, outline_offset]:
                            if offset_x != 0 or offset_y != 0:
                                rotated_draw.text(
                                    (x_pos + offset_x, y_pos + offset_y),
                                    cls.WATERMARK_TEXT,
                                    fill=(0, 0, 0, alpha),
                                    font=font
                                )

                    # Draw main white text
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
