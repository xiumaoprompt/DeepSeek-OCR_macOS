[![简体中文](https://img.shields.io/badge/语言-简体中文-blue.svg)](README.md) [![English](https://img.shields.io/badge/Language-English-blue.svg)](README_en.md)

# DeepSeek-OCR for macOS (Apple Silicon/Intel)

本项目提供了一个专为 macOS 用户设计的、开箱即用的 DeepSeek-OCR 工作流，让你可以在自己的 Mac 上本地运行强大的 [DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR) 模型。

项目内置 Gradio Web 界面，默认在 CPU 上稳定运行（Apple Silicon 与 Intel 均已验证）。同时提供 Apple Silicon 的 MPS（GPU）实验性支持。让你无需 CUDA，即可在本地完成图像与 PDF 的高质量 OCR。

## ✨ 功能特性

- ** macOS 兼容**: 在 Apple Silicon 与 Intel 的 CPU 上稳定运行；提供 MPS（Apple GPU）实验性支持，性能因机型/系统/库版本而异。
- **🚀 一键式安装**: 提供自动化配置脚本 (`setup.py`)，引导用户完成所有环境配置。
- **🖼️ 便捷 Gradio 界面**: 提供简单易用的 Web 界面，轻松上传文件并进行 OCR。
- **📄 图像与 PDF 支持**: 支持处理单个图像或完整的 PDF 文档。
- **⚙️ 多种识别模式**: 可在不同分辨率模式间切换，以平衡速度与精度。
- **🎯 强大的 OCR 任务**: 不仅支持将文档转换为 Markdown，还支持表格/公式识别、图像描述等高级功能。
- **📦 纯本地化运行**: 所有计算都在你的本地机器上完成，确保数据隐私和安全。

## 🚀 快速开始

### 环境要求

- 一台 macOS 系统的电脑。
- **Python 3.12.x** (推荐使用 `3.12.11` 以获得最佳兼容性)。
- [Git](https://git-scm.com/book/zh/v2/起步-安装-Git) (用于克隆代码仓库)。

### 步骤 1: 克隆本项目

打开“终端” (Terminal) 应用，运行以下命令：

```bash
git clone https://github.com/xiumaoprompt/DeepSeek-OCR_macOS.git
cd DeepSeek-OCR_macOS
```

### 步骤 2: 下载 DeepSeek-OCR 模型

本项目需要依赖 Hugging Face 上的原始模型文件。

```bash
# 确保你已经安装了 git-lfs (https://git-lfs.com)
git lfs install

# 克隆模型仓库
git clone https://huggingface.co/deepseek-ai/DeepSeek-OCR
```

这会将模型文件下载到你项目目录下的 `DeepSeek-OCR` 文件夹中。

### 步骤 3: 运行自动化配置脚本 (核心)

这是最关键的一步！项目提供了一个自动化脚本 `setup.py` 来为你完成所有繁琐的配置。

在终端中运行以下命令：

```bash
python setup.py
```

脚本将会引导你完成以下操作：
1.  **验证模型路径**：它会请你将下载好的 `DeepSeek-OCR` 文件夹拖入终端，以确认路径。
2.  **应用 macOS 补丁**：自动将 `modeling_deepseekocr.py` 替换为适配 macOS 的版本。
3.  **创建符号链接**：解决 Python 的模块导入问题。
4.  **更新配置文件**：将你的模型路径写入项目配置中。

整个过程完全自动化，你只需要根据提示操作即可。

### 步骤 4: 安装依赖

使用 `pip` 安装所有必需的 Python 库。

```bash
pip install -r requirements.txt
```

### 步骤 5: 启动应用

所有准备工作都已完成！现在启动 Gradio 应用：

```bash
python -m macos_workflow.app
```

脚本启动后，在浏览器中打开终端里显示的本地网址 (通常是 `http://127.0.0.1:7860`)，即可开始使用。

## 🤝 如何贡献

欢迎任何形式的贡献！如果你有任何改进建议或发现了 Bug，请随时提交 Issue 或 Pull Request。
