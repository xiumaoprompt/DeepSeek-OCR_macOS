# DeepSeek-OCR for macOS

This project provides a user-friendly Gradio web interface to run the powerful [DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR) model locally on your Mac, with optimizations for both Apple Silicon (MPS) and Intel CPUs.

It allows you to perform high-quality OCR on images and PDFs directly on your machine, without needing a powerful cloud GPU.

![App Screenshot](https://raw.githubusercontent.com/your-username/your-repo-name/main/docs/screenshot.png) 
*(Note: You will need to upload a screenshot to a `docs` folder in your repo and replace the link above)*

## ✨ Features

- ** macOS Optimized**: Runs efficiently on Apple Silicon (M1/M2/M3) and Intel-based Macs.
- **🖼️ Gradio UI**: Easy-to-use web interface for OCR tasks.
- **📄 Image & PDF Support**: Process single images or entire PDF documents.
- **⚙️ Adjustable Modes**: Choose from different resolution modes to balance speed and accuracy.
- **🎯 Advanced Tasks**: Supports not just Markdown conversion, but also table/figure parsing, image description, and visual localization.
- **📦 Portable & Local**: No hardcoded paths. All processing is done 100% on your local machine.

## 🚀 Getting Started

### Prerequisites

- A Mac with Python 3.10 or newer.
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) for cloning the repository.

### 1. Clone This Repository

Open your terminal and run the following command:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
*(Note: Replace `your-username/your-repo-name` with your actual GitHub repository path after you create it.)*

### 2. Download the DeepSeek-OCR Model

This project requires the original model files from Hugging Face.

```bash
# Make sure you have git-lfs installed (https://git-lfs.com)
git lfs install

# Clone the model repository
git clone https://huggingface.co/deepseek-ai/DeepSeek-OCR
```

This will download the model into a `DeepSeek-OCR` folder in your project directory.

### 3. Apply the macOS Patch

The original model code is designed for Linux with NVIDIA GPUs. We need to replace one file to make it work on macOS.

**Copy the patched file from this repository into the model folder:**

```bash
cp macos_workflow/patched_modeling_deepseekocr.py DeepSeek-OCR/modeling_deepseekocr.py
```
This command overwrites the original model script with the one optimized for macOS. **This step is crucial.**

### 4. Install Dependencies

Install all the necessary Python libraries using the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Run the Application

You are all set! Launch the Gradio web app with this command:

```bash
python -m macos_workflow.app
```

Open your web browser and go to the local URL shown in the terminal (usually `http://127.0.0.1:7860`).

## 🤝 How to Contribute

Contributions are welcome! If you have ideas for improvements or find a bug, please open an issue or submit a pull request.