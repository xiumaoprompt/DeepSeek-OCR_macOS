
"""
Configuration for the DeepSeek-OCR macOS workflow.
"""

# The device to run the model on.
# Use "mps" for Apple Silicon GPU acceleration, or "cpu" for CPU.
DEVICE = "cpu"

# --- Image Processing Settings ---
# These are default values; the Gradio UI can override them dynamically.
# Size for the global view of the image
BASE_SIZE = 1024
# Size for the tiled local views of the image
IMAGE_SIZE = 640
# Whether to use the dynamic tiling mode ("Gundam" mode)
CROP_MODE = True

# --- Prompt Settings ---
# Default prompt for document processing
DEFAULT_PROMPT = "<image>\n<|grounding|>Convert the document to markdown."

