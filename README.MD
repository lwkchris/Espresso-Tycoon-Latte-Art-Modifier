# Espresso Tycoon Custom Latte Art Tool

This tool allows you to convert any image into a custom latte art file for the game **Espresso Tycoon**. It processes images into the required 512x512 grayscale format and places them directly into your game save folders.

## ☕ Control Plane Parameters

The sidebar contains several sliders to "tune" how your art will look on the coffee:

| Parameter | Meaning |
| :--- | :--- |
| **Brightness** | Controls the overall intensity of the white foam. Higher values make the art "pop" more against dark coffee. |
| **Contrast** | Controls the sharpess between light and dark parts. High contrast makes the art look like a stencil; low contrast creates soft gradients. |
| **Curves Offset** | This is the "Darkness Gate." It subtracts brightness from the whole image. Increasing this will hide the darker background of your source image, leaving only the main subject. |
| **Zoom / Scale** | Controls how much of the image is captured. **100%** shows the full image fitted to the cup; **5%** is a extreme close-up. |

## 🖱️ Interactive Controls

* **Drag & Move:** Click and hold the **right preview window** to move your image around. This allows you to center your subject perfectly.
* **Mouse Wheel:** Scroll up or down while hovering over the app to zoom in and out instantly.
* **Preview on Coffee:** Toggles a simulated espresso background (#ffddb2 foam on #b26853 crema) so you can see how the art will look in-game before saving.

## 🚀 How to Use

1.  **Select Save Slot:** Choose the slot you are currently playing in the game (e.g., Save 1).
2.  **Select Image:** Load a JPG, PNG, or BMP.
3.  **Tune:** Adjust the sliders and drag the image until it looks right in the preview.
4.  **Send to Game:** Click the green button. The tool will generate a timestamped PNG and place it in the game's directory.
5.  **In-Game:** Go to your Coffee Machine editor in Espresso Tycoon, and your new art will appear in the "Custom" tab.