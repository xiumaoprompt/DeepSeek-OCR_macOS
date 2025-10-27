import sys
import os
import torch
from transformers import AutoTokenizer
import logging

# The sys.path modification is now handled by app.py, which passes down the project_root.
# We can directly import the custom model class.
from DeepSeek_OCR.modeling_deepseekocr import DeepseekOCRForCausalLM
from . import config_macos as config

logger = logging.getLogger(__name__)

class OCREngine:
    """
    A simplified OCR Engine that correctly loads the custom DeepSeek-OCR model
    and uses its built-in .infer() method.
    It's initialized with the project's root path to dynamically locate model files.
    """
    def __init__(self, project_root):
        print("Initializing OCR Engine...")
        self.project_root = project_root
        self.model_path = os.path.join(self.project_root, "DeepSeek-OCR")
        self.output_path = os.path.join(self.project_root, "output_macos")
        os.makedirs(self.output_path, exist_ok=True)

        self.device = self._get_device()
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _get_device(self):
        if config.DEVICE == "mps" and torch.backends.mps.is_available():
            print("MPS backend is available. Using MPS.")
            return torch.device("mps")
        else:
            print("MPS not available or not selected. Using CPU.")
            return torch.device("cpu")

    def _load_model(self):
        """
        Loads the tokenizer and the model using the custom class and dynamic paths.
        """
        if self.model is not None:
            print("Model already loaded.")
            return

        if not os.path.isdir(self.model_path):
            raise FileNotFoundError(
                f"Model directory not found at '{self.model_path}'. "
                f"Please ensure the 'DeepSeek-OCR' model folder exists at the project root."
            )

        try:
            print(f"Loading tokenizer from {self.model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            print("Tokenizer loaded successfully.")

            print(f"Loading model from {self.model_path} to {self.device}...")
            self.model = DeepseekOCRForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=torch.float32
            ).to(self.device)

            self.model.eval()
            print("Model loaded and set to evaluation mode successfully.")

        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            raise

    def infer(self, image_path: str, prompt: str):
        """
        Runs inference by calling the model's internal .infer() method.
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model or tokenizer is not loaded.")

        print("Calling model's internal .infer() method...")
        try:
            result_text = self.model.infer(
                tokenizer=self.tokenizer,
                prompt=prompt,
                image_file=image_path,
                output_path=self.output_path, # Use dynamically configured output path
                base_size=config.BASE_SIZE,
                image_size=config.IMAGE_SIZE,
                crop_mode=config.CROP_MODE,
                save_results=False,
                test_compress=False,
                eval_mode=True
            )
            print("Inference call complete.")
            return result_text
        except Exception as e:
            logger.error(f"An error occurred during model.infer(): {e}", exc_info=True)
            raise