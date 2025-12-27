import os
import datetime
import customtkinter as ctk
from LatteArtLogic import LatteArt
from PIL import Image, ImageEnhance
from tkinter import filedialog, messagebox

default_bright = 1.8
default_contrast = 2.4
default_offset = 20
default_zoom = 1.0


class LatteArtUI(ctk.CTk):
    def __init__(self, logic_engine):
        super().__init__()
        self.logic = logic_engine

        self.title("Espresso Tycoon Custom Latte Art Tool")
        self.geometry("1150x800")

        self.raw_image = None
        self.processed_image = None

        # Dictionary to store percentage labels
        self.perc_labels = {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Call the setup methods
        self.setup_sidebar()
        self.setup_previews()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Latte Art Editor", font=("Arial", 22, "bold")).pack(pady=20)

        # Sliders with Percentages
        self.bright_slider = self.create_slider("Brightness", 0.5, 3.0, default_bright)
        self.contrast_slider = self.create_slider("Contrast", 0.5, 3.0, default_contrast)
        self.offset_slider = self.create_slider("Curves Offset", 0, 150, default_offset)
        self.zoom_slider = self.create_slider("Zoom / Scale", 1.0, 0.1, default_zoom)

        # Coffee Preview Toggle
        self.coffee_bg_var = ctk.BooleanVar(value=False)
        self.coffee_switch = ctk.CTkSwitch(
            self.sidebar,
            text="Preview on Coffee",
            variable=self.coffee_bg_var,
            command=self.update_preview
        )
        self.coffee_switch.pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Reset Defaults", fg_color="gray40", command=self.reset_settings).pack(pady=10)

        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=20)

        # Slot Selector
        ctk.CTkLabel(self.sidebar, text="Select Save Slot:", font=("Arial", 14, "bold")).pack(pady=5)
        self.slot_dropdown = ctk.CTkOptionMenu(self.sidebar, values=list(self.logic.save_slots.keys()))
        self.slot_dropdown.set("Auto Save")
        self.slot_dropdown.pack(pady=10, padx=20, fill="x")

        # Action Buttons
        ctk.CTkButton(self.sidebar, text="- Select Image -", command=self.load_image).pack(pady=10, padx=20, fill="x")
        self.send_btn = ctk.CTkButton(self.sidebar, text="- Send to Game -", state="disabled",
                                      fg_color="#2ecc71", hover_color="#27ae60", command=self.confirm_and_save)
        self.send_btn.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="📁 Open Save Folder", fg_color="transparent",
                      border_width=1, command=self.handle_open_folder).pack(pady=20, padx=20, fill="x")

    def setup_previews(self):
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.preview_frame.grid_columnconfigure((0, 1), weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.preview_frame, text="Original Source").grid(row=0, column=0, pady=10)
        ctk.CTkLabel(self.preview_frame, text="Processed (512x512 PNG)").grid(row=0, column=1, pady=10)

        self.original_label = ctk.CTkLabel(self.preview_frame, text="No image", fg_color="gray20", corner_radius=10)
        self.original_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.processed_label = ctk.CTkLabel(self.preview_frame, text="No image", fg_color="gray20", corner_radius=10)
        self.processed_label.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    def create_slider(self, label, min_val, max_val, start_val):
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=20)

        ctk.CTkLabel(header_frame, text=label).pack(side="left")

        perc_label = ctk.CTkLabel(header_frame, text="0%", font=("Arial", 10, "italic"), text_color="#ffddb2")
        perc_label.pack(side="right")
        self.perc_labels[label] = perc_label

        slider = ctk.CTkSlider(
            self.sidebar,
            from_=min_val,
            to=max_val,
            command=lambda v, l=label: self.on_slider_move(v, l)
        )
        slider.set(start_val)
        slider.pack(pady=(0, 15), padx=20, fill="x")

        # Set initial text
        self.update_perc_text(label, start_val, min_val, max_val)
        return slider

    def on_slider_move(self, value, label):
        # Ranges for percentage calculation
        ranges = {
            "Brightness": (0.5, 3.0),
            "Contrast": (0.5, 3.0),
            "Curves Offset": (0, 150),
            "Zoom / Scale": (1.0, 0.1)
        }
        m_val, x_val = ranges[label]
        self.update_perc_text(label, value, m_val, x_val)
        self.update_preview()

    def update_perc_text(self, label, value, min_v, max_v):
        if label == "Zoom / Scale":
            percentage = int(value * 100)
        else:
            percentage = int(((value - min_v) / (max_v - min_v)) * 100)
        self.perc_labels[label].configure(text=f"{percentage}%")

    def update_preview(self, _=None):
        if self.raw_image:
            self.processed_image = self.logic.process_image(
                self.raw_image,
                self.bright_slider.get(),
                self.contrast_slider.get(),
                self.offset_slider.get(),
                self.zoom_slider.get()
            )

            display_img = self.processed_image.copy()

            if self.coffee_bg_var.get():
                coffee_rgb = (178, 104, 83)
                milk_base_rgb = (255, 221, 178)  # Your specific Milk Color
                background = Image.new("RGBA", display_img.size, coffee_rgb + (255,))

                luma_mask = display_img.convert("L")
                threshold = 180
                luma_mask = luma_mask.point(lambda p: 0 if p < threshold else p)
                luma_mask = ImageEnhance.Contrast(luma_mask).enhance(1.3)

                tint_factor = 0.85
                final_foam_color = tuple(
                    int(milk_base_rgb[i] * tint_factor + coffee_rgb[i] * (1 - tint_factor))
                    for i in range(3)
                )

                milk_layer = Image.new("RGBA", display_img.size, final_foam_color + (255,))
                background.paste(milk_layer, (0, 0), luma_mask)
                display_img = background

            self.processed_label.configure(
                image=ctk.CTkImage(display_img, size=(400, 400)),
                text=""
            )

    def reset_settings(self):
        self.bright_slider.set(default_bright)
        self.contrast_slider.set(default_contrast)
        self.offset_slider.set(default_offset)
        self.zoom_slider.set(default_zoom)
        self.update_perc_text("Brightness", default_bright, 0.5, 3.0)
        self.update_perc_text("Contrast", default_contrast, 0.5, 3.0)
        self.update_perc_text("Curves Offset", default_offset, 0, 150)
        self.update_perc_text("Zoom / Scale", default_zoom, 1.0, 0.1)
        self.update_preview()

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.raw_image = Image.open(path)
            orig_p = self.raw_image.copy()
            orig_p.thumbnail((400, 400))
            self.original_label.configure(image=ctk.CTkImage(orig_p, size=orig_p.size), text="")
            self.update_preview()
            self.send_btn.configure(state="normal")

    def handle_open_folder(self):
        path = self.logic.get_save_path(self.slot_dropdown.get())
        self.logic.open_folder(path)

    def confirm_and_save(self):
        if not self.processed_image: return
        target_dir = self.logic.get_save_path(self.slot_dropdown.get())
        try:
            os.makedirs(target_dir, exist_ok=True)
            if messagebox.askyesno("Confirm", f"Send to {self.slot_dropdown.get()}?"):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"Art_{timestamp}.png"
                self.processed_image.save(os.path.join(target_dir, filename), "PNG")
                messagebox.showinfo("Done", f"Latte Art Sent!\nSaved as: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


if __name__ == "__main__":
    engine = LatteArt()
    app = LatteArtUI(engine)
    app.mainloop()