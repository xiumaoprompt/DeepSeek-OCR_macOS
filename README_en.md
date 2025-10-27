# DeepSeek-OCR for macOS (Apple Silicon/Intel)

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README_en.md)

This project provides a ready-to-use workflow designed for macOS users to run the powerful [DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR) model locally on their own Mac.

It includes a Gradio-powered web interface and is optimized for both Apple Silicon (M1/M2/M3/M4) and Intel CPUs, allowing you to perform high-quality OCR on images and PDF documents locally, without requiring any external GPU or cloud service.(Experimental MPS support is available for Apple Silicon users.)

## ✨ Features

- ** macOS Compatible**: Verified to run stably on both Apple Silicon and Intel Macs. Experimental MPS (Apple GPU) support is available, though performance may vary depending on the hardware and system environment.
- **🚀 One-Click Setup**: Provides an automated configuration script (`setup.py`) to guide users through the entire environment setup.
- **🖼️ Convenient Gradio UI**: Offers a simple and easy-to-use web interface for uploading files and performing OCR.
- **📄 Image & PDF Support**: Supports processing of single images or entire PDF documents.
- **⚙️ Multiple Recognition Modes**: Allows switching between different resolution modes to balance speed and accuracy.
- **🎯 Powerful OCR Tasks**: Supports not only converting documents to Markdown but also advanced features like table/formula recognition and image description.
- **📦 Purely Local**: All computations are done on your local machine, ensuring data privacy and security.

## 🚀 Getting Started

### Prerequisites

- A computer running macOS.
- **Python 3.12.x** (version `3.12.11` is recommended for best compatibility).
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) for cloning the repository.

### Step 1: Clone This Repository

Open the Terminal app and run the following command:

```bash
git clone https://github.com/xiumaoprompt/DeepSeek-OCR_macOS.git
cd DeepSeek-OCR_macOS
```

### Step 2: Download the DeepSeek-OCR Model

This project requires the original model files from Hugging Face.

```bash
# Make sure you have git-lfs installed (https://git-lfs.com)
git lfs install

# Clone the model repository
git clone https://huggingface.co/deepseek-ai/DeepSeek-OCR
```

This will download the model files into a `DeepSeek-OCR` folder within your project directory.

### Step 3: Run the Automated Setup Script (Core Step)

This is the most crucial step! We provide an automated script, `setup.py`, to handle all the tedious configurations for you.

Run the following command in your terminal:

```bash
python setup.py
```

The script will guide you through the following operations:
1.  **Validate Model Path**: It will ask you to drag and drop the downloaded `DeepSeek-OCR` folder into the terminal to confirm its path.
2.  **Apply macOS Patch**: Automatically replaces `modeling_deepseekocr.py` with a version compatible with macOS.
3.  **Create Symbolic Link**: Resolves Python's module import issues.
4.  **Update Configuration**: Writes your model path into the project's configuration file.

The entire process is automated; you just need to follow the prompts.

### Step 4: Install Dependencies

Install all necessary Python libraries using `pip`.

```bash
pip install -r pip-requirements.txt
```
*(Note: The filename is `pip-requirements.txt`)*

### Step 5: Launch the Application

All preparations are complete! Now, launch the Gradio application:

```bash
python -m macos_workflow.app
```

After the script starts, open your web browser and navigate to the local URL shown in the terminal (usually `http://127.0.0.1:7860`) to start using the tool.

## 🤝 How to Contribute

Contributions of any kind are welcome! If you have ideas for improvements or find a bug, please feel free to open an issue or submit a pull request.
