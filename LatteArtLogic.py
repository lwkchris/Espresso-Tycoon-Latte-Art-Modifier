import os
import platform
import subprocess
import numpy as np
from PIL import Image, ImageEnhance

class LatteArt:
    def __init__(self):
        # Determine the game's save path based on the Operating System
        if platform.system() == "Windows":
            self.base_path = os.path.expandvars(r'%appdata%\..\LocalLow\DreamWay Games\Espresso Tycoon\GameState')
        else:
            self.base_path = os.path.expanduser(
                "~/Library/Application Support/DreamWay Games/Espresso Tycoon/GameState")

        # Mapping UI names to game folder names
        self.save_slots = {
            "Auto Save": "Save_0",
            "Save 1": "Save_1",
            "Save 2": "Save_2",
            "Save 3": "Save_3",
            "Save 4": "Save_4",
            "Save 5": "Save_5"
        }

    def get_save_path(self, slot_key):
        """Returns the full path to the CustomLatteArts folder for a specific slot."""
        return os.path.join(self.base_path, self.save_slots[slot_key], "CustomLatteArts")

    def open_folder(self, path):
        """Opens the target folder in the system file explorer."""
        os.makedirs(path, exist_ok=True)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

    def process_image(self, pil_img, brightness, contrast, offset, zoom, off_x=0, off_y=0):
        """
        Processes the raw image into a format compatible with Espresso Tycoon.
        The game requires a 512x512 PNG where the alpha channel and luma determine depth.
        """
        img = pil_img.convert("RGBA")
        width, height = img.size

        # Fit logic: Use the longest side as the base for zooming
        max_dim = max(width, height)
        crop_size = max_dim * zoom

        # Calculate crop boundaries based on mouse drag offsets (off_x, off_y)
        left = (width - crop_size) / 2 + (off_x * crop_size)
        top = (height - crop_size) / 2 + (off_y * crop_size)
        right = left + crop_size
        bottom = top + crop_size

        # Crop the image and resize to the game's required 512x512 resolution
        img = img.crop((left, top, right, bottom))
        img = img.resize((512, 512), Image.Resampling.LANCZOS)

        # Apply standard image enhancements
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)

        # Espresso Tycoon uses Grayscale values to determine where milk foam is thick/thin
        alpha = img.getchannel('A')
        gray_img = img.convert("L")
        img_array = np.array(gray_img).astype(float)

        # 'Offset' effectively cuts off the darker parts of the image, turning them transparent/coffee-colored
        img_array = np.clip(img_array - offset, 0, 255).astype(np.uint8)
        gray_img = Image.fromarray(img_array)

        # Re-attach original alpha channel to the processed grayscale image
        final_img = gray_img.convert("RGBA")
        final_img.putalpha(alpha)

        return final_img