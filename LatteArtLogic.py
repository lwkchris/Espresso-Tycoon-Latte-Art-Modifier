import os
import platform
import subprocess
import numpy as np
from PIL import Image, ImageEnhance


class LatteArt:
    def __init__(self):
        if platform.system() == "Windows":
            self.base_path = os.path.expandvars(r'%appdata%\..\LocalLow\DreamWay Games\Espresso Tycoon\GameState')
        else:
            self.base_path = os.path.expanduser(
                "~/Library/Application Support/DreamWay Games/Espresso Tycoon/GameState")

        self.save_slots = {
            "Auto Save": "Save_0", "Save 1": "Save_1", "Save 2": "Save_2",
            "Save 3": "Save_3", "Save 4": "Save_4", "Save 5": "Save_5"
        }

    def get_save_path(self, slot_key):
        return os.path.join(self.base_path, self.save_slots[slot_key], "CustomLatteArts")

    def open_folder(self, path):
        os.makedirs(path, exist_ok=True)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

    def process_image(self, pil_img, brightness, contrast, offset, zoom, off_x=0, off_y=0):
        # 1. Convert to RGBA
        img = pil_img.convert("RGBA")
        width, height = img.size

        # 2. Logic to fit longest side
        max_dim = max(width, height)
        crop_size = max_dim * zoom

        # Calculate center with user drag offsets
        # We multiply by zoom so the dragging feels consistent at different zoom levels
        left = (width - crop_size) / 2 + (off_x * crop_size)
        top = (height - crop_size) / 2 + (off_y * crop_size)
        right = left + crop_size
        bottom = top + crop_size

        # 3. Crop and Resize (PIL handles 'out of bounds' by adding transparency)
        img = img.crop((left, top, right, bottom))
        img = img.resize((512, 512), Image.Resampling.LANCZOS)

        # 4. Enhancements
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)

        # 5. Apply Curve Offset (Grayscale logic)
        alpha = img.getchannel('A')
        gray_img = img.convert("L")
        img_array = np.array(gray_img).astype(float)
        img_array = np.clip(img_array - offset, 0, 255).astype(np.uint8)
        gray_img = Image.fromarray(img_array)

        # 6. Finalize
        final_img = gray_img.convert("RGBA")
        final_img.putalpha(alpha)

        return final_img