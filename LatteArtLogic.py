import os
import platform
import subprocess
import numpy as np
from PIL import Image, ImageEnhance, ImageOps


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

    def process_image(self, pil_img, brightness, contrast, offset, zoom):
        # 1. Base Prep
        img = pil_img.convert("RGBA")

        # 2. Advanced Zoom/Fit Logic (Fitting Longest Side)
        width, height = img.size
        # To show the FULL image at zoom 1.0, the canvas must be a square
        # based on the LONGER side.
        max_dim = max(width, height)

        # Calculate the size of the square crop window
        # zoom=1.0 means window size is max_dim (fits whole image)
        # zoom=0.1 means window size is very small (zoomed in)
        crop_size = max_dim * zoom

        left = (width - crop_size) / 2
        top = (height - crop_size) / 2
        right = (width + crop_size) / 2
        bottom = (height + crop_size) / 2

        # Crop (PIL handle coordinates outside image by adding transparency automatically)
        img = img.crop((left, top, right, bottom))
        img = img.resize((512, 512), Image.Resampling.LANCZOS)

        # 3. Enhancements
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)

        # 4. Grayscale & Curves Math
        alpha = img.getchannel('A')
        gray_img = img.convert("L")

        img_array = np.array(gray_img).astype(float)
        img_array = img_array - offset
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        gray_img = Image.fromarray(img_array)

        # 5. Finalize
        final_img = gray_img.convert("RGBA")
        final_img.putalpha(alpha)

        return final_img