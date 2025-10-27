import gradio as gr
import os
import tempfile
import time
from PIL import Image

# Ensure the root path is added so we can import our modules
import sys
import os

# Dynamically determine the project root directory.
# This script is in 'macos_workflow', and the project root is the parent directory.
_current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(_current_dir)

# Add the project root to the Python path to allow for module imports
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import our workflow components
from macos_workflow.ocr_engine_macos import OCREngine
from macos_workflow import config_macos as config
from macos_workflow.utils import re_match, draw_bounding_boxes, pdf_to_images, save_images_to_pdf

# --- Global Variables ---
ENGINE = None

# --- Task and Prompt Mapping ---
TASK_PROMPTS = {
    "文档转换 (Markdown)": "<image>\n<|grounding|>Convert the document to markdown.",
    "纯文本识别 (无排版)": "<image>\nFree OCR.",
    "图表/公式解析": "<image>\nParse the figure.",
    "图像描述": "<image>\nDescribe this image in detail.",
    "视觉定位": ""  # Renamed from "自定义指令"
}

RESOLUTION_MODES = {
    "Base (1024x1024)": {"base_size": 1024, "image_size": 1024, "crop_mode": False},
    "Gundam (动态)": {"base_size": 1024, "image_size": 640, "crop_mode": True},
    "Large (1280x1280)": {"base_size": 1280, "image_size": 1280, "crop_mode": False},
    "Small (640x640)": {"base_size": 640, "image_size": 640, "crop_mode": False},
}

USAGE_GUIDE = """
### 1. 如何选择合适的分辨率模式？

选择正确的分辨率是平衡速度与精度的关键。

*   **⚡️ 快速模式 (Small)**: 适用于文字较少、排版简单的图像（如幻灯片、部分书籍）。
*   **👍 推荐模式 (Base)**: 适用于大多数常规文档（如报告、论文），在速度和效果间取得最佳平衡。
*   **🎯 高精度模式 (Gundam / Large)**: 适用于文字密度极高或尺寸巨大的图像（如报纸、海报）。Gundam模式通过“全局+局部”的视野，能最大限度保留细节。

### 2. 如何善用“指令提示词”？

在“选择任务”中选择对应的任务，或选择“视觉定位”并输入自定义指令来解锁高级功能。

*   **通用文档处理 (默认):**
    ```
    <image>\n<|grounding|>Convert the document to markdown.
    ```
*   **纯文本识别 (忽略排版):**
    ```
    <image>\nFree OCR.
    ```
*   **“深度解析”图表或公式:**
    ```
    <image>\nParse the figure.
    ```
*   **通用图像描述:**
    ```
    <image>\nDescribe this image in detail.
    ```
*   **视觉定位 (寻找图中特定内容):**
    ```
    <image>\nLocate <|ref|>文字或物体描述<|/ref|> in the image.
    ```

### 生产力建议

将本工具的输出（尤其是Markdown和图表数据）作为上下文，输入给大型语言模型（如GPT-4, Claude, DeepSeek-LLM等），进行摘要、问答或数据分析，可以构建起强大的“视觉输入 -> 结构化文本 -> 语言智能”自动化工作流。
"""

def initialize_engine():
    """Initializes the OCREngine if it hasn't been already."""
    global ENGINE
    if ENGINE is None:
        print("--- First time setup: Initializing OCR Engine... ---")
        try:
            ENGINE = OCREngine(project_root=project_root)
            print("--- OCR Engine ready. ---")
        except Exception as e:
            print(f"FATAL: Could not initialize OCR Engine: {e}")
            raise gr.Error(f"无法初始化模型引擎，请检查后台日志。错误: {e}")
    return "引擎已就绪。请上传文件并开始识别。"

# --- Backend Functions for Gradio ---

def run_image_ocr_task(image: Image.Image, task: str, custom_prompt: str, resolution_key: str, progress=gr.Progress()):
    """The main function for the Image OCR tab."""
    if image is None:
        raise gr.Error("请先上传或粘贴一张图像！")

    progress(0, desc="引擎初始化...")
    initialize_engine()

    prompt = TASK_PROMPTS.get(task, config.DEFAULT_PROMPT) if task != "视觉定位" else custom_prompt
    if not prompt.strip():
        raise gr.Error("使用“视觉定位”时，指令内容不能为空！")

    if "<image>" not in prompt:
        prompt = f"<image>\n{prompt}"

    resolution_params = RESOLUTION_MODES.get(resolution_key, RESOLUTION_MODES["Base (1024x1024)"])
    config.BASE_SIZE, config.IMAGE_SIZE, config.CROP_MODE = resolution_params['base_size'], resolution_params['image_size'], resolution_params['crop_mode']

    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            image.save(tmp_file.name)
            tmp_image_path = tmp_file.name

        progress(0.5, desc="模型推理中...")
        start_time = time.time()
        result_text = ENGINE.infer(image_path=tmp_image_path, prompt=prompt)
        inference_time = time.time() - start_time

    finally:
        if 'tmp_image_path' in locals() and os.path.exists(tmp_image_path):
            os.remove(tmp_image_path)

    progress(0.9, desc="后处理结果...")
    matches_ref, _, _ = re_match(result_text)
    annotated_image = draw_bounding_boxes(image, matches_ref, tempfile.gettempdir()) if matches_ref else None

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
        tmp_md.write(result_text)
        md_path = tmp_md.name

    img_path = None
    if annotated_image:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
            annotated_image.save(tmp_img.name)
            img_path = tmp_img.name

    status = f"✅ 图像识别成功！\n耗时: {inference_time:.2f} 秒。"
    return result_text, annotated_image, md_path, img_path, status

def run_pdf_ocr_task(pdf_file, task: str, custom_prompt: str, resolution_key: str, progress=gr.Progress()):
    """The main function for the PDF OCR tab."""
    if pdf_file is None:
        raise gr.Error("请先上传一个PDF文件！")

    progress(0, desc="引擎初始化...")
    initialize_engine()
    pdf_path = pdf_file.name

    prompt = TASK_PROMPTS.get(task, config.DEFAULT_PROMPT) if task != "视觉定位" else custom_prompt
    if not prompt.strip():
        raise gr.Error("使用“视觉定位”时，指令内容不能为空！")
        
    if "<image>" not in prompt:
        prompt = f"<image>\n{prompt}"

    resolution_params = RESOLUTION_MODES.get(resolution_key, RESOLUTION_MODES["Base (1024x1024)"])
    config.BASE_SIZE, config.IMAGE_SIZE, config.CROP_MODE = resolution_params['base_size'], resolution_params['image_size'], resolution_params['crop_mode']

    page_images = pdf_to_images(pdf_path)
    if not page_images:
        raise gr.Error("无法从PDF文件中提取图像，请检查文件是否有效。")

    all_md_results, annotated_pages = [], []
    total_time = 0

    for i, page_image in enumerate(page_images):
        progress(i / len(page_images), desc=f"正在处理第 {i+1}/{len(page_images)} 页...")
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                page_image.save(tmp_file.name)
                tmp_image_path = tmp_file.name
            
            start_time = time.time()
            result_text = ENGINE.infer(image_path=tmp_image_path, prompt=prompt)
            total_time += (time.time() - start_time)

            all_md_results.append(result_text)
            matches_ref, _, _ = re_match(result_text)
            annotated_page = draw_bounding_boxes(page_image, matches_ref, tempfile.gettempdir()) if matches_ref else page_image
            annotated_pages.append(annotated_page)

        finally:
            if 'tmp_image_path' in locals() and os.path.exists(tmp_image_path):
                os.remove(tmp_image_path)

    progress(0.9, desc="汇总结果...")
    final_md = "\n\n<--- Page Split --->\n\n".join(all_md_results)
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
        tmp_md.write(final_md)
        md_path = tmp_md.name

    pdf_out_path = None
    if annotated_pages:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            save_images_to_pdf(annotated_pages, tmp_pdf.name)
            pdf_out_path = tmp_pdf.name

    status = f"✅ PDF处理完成！\n共 {len(page_images)} 页，总耗时: {total_time:.2f} 秒。"
    # For the PDF tab, the main visual output is the downloadable PDF, not an image viewer.
    return final_md, None, md_path, pdf_out_path, status

def update_custom_prompt_visibility(task: str):
    return gr.update(visible=(task == "视觉定位"))

# --- Gradio UI Definition ---
def create_ui():
    with gr.Blocks(theme=gr.themes.Soft(), css="footer {display: none !important}") as demo:
        gr.Markdown("<h1><center> DeepSeek-OCR for macOS</center></h1>")
        gr.Markdown("#### <center>一个在您的Mac上本地运行的高性能OCR工具</center>")

        with gr.Accordion("💡 使用指南与高级技巧 (点击展开)", open=False):
            gr.Markdown(USAGE_GUIDE)

        with gr.Tabs() as tabs:
            with gr.TabItem("🖼️ 图像识别 (Image OCR)", id=0):
                with gr.Row(equal_height=True):
                    with gr.Column(scale=1):
                        gr.Markdown("### 1. 输入配置")
                        image_input = gr.Image(type="pil", label="上传图像", sources=['upload', 'clipboard'])
                        task_selector_img = gr.Dropdown(label="🎯 选择任务", choices=list(TASK_PROMPTS.keys()), value="文档转换 (Markdown)")
                        custom_prompt_img = gr.Textbox(label="✍️ 输入视觉定位指令", placeholder="例如: <image>\nLocate <|ref|>the black cat<|/ref|> in the image.", visible=False, lines=3)
                        resolution_selector_img = gr.Dropdown(label="⚙️ 选择分辨率模式", choices=list(RESOLUTION_MODES.keys()), value="Base (1024x1024)")
                        submit_button_img = gr.Button("🚀 开始识别图像", variant="primary")
                    with gr.Column(scale=1):
                        gr.Markdown("### 2. 输出结果")
                        status_box_img = gr.Textbox(label="ℹ️ 状态", interactive=False, lines=4)
                        output_md_img = gr.Markdown(label="识别结果 (Markdown)")
                        output_img = gr.Image(type="pil", label="可视化标注图像")
                        with gr.Row():
                            download_md_img = gr.File(label="下载Markdown")
                            download_img_file = gr.File(label="下载标注图")
            
            with gr.TabItem("📄 PDF识别 (PDF OCR)", id=1):
                with gr.Row(equal_height=True):
                    with gr.Column(scale=1):
                        gr.Markdown("### 1. 输入配置")
                        pdf_input = gr.File(label="上传PDF文件", file_types=['.pdf'])
                        task_selector_pdf = gr.Dropdown(label="🎯 选择任务", choices=list(TASK_PROMPTS.keys()), value="文档转换 (Markdown)")
                        custom_prompt_pdf = gr.Textbox(label="✍️ 输入视觉定位指令", placeholder="例如: <image>\nLocate <|ref|>the title<|/ref|> in the image.", visible=False, lines=3)
                        resolution_selector_pdf = gr.Dropdown(label="⚙️ 选择分辨率模式", choices=list(RESOLUTION_MODES.keys()), value="Base (1024x1024)")
                        submit_button_pdf = gr.Button("🚀 开始处理PDF", variant="primary")
                    with gr.Column(scale=1):
                        gr.Markdown("### 2. 输出结果")
                        status_box_pdf = gr.Textbox(label="ℹ️ 状态", interactive=False, lines=4)
                        output_md_pdf = gr.Markdown(label="识别结果 (Markdown)")
                        # For PDF, we show a download button for the annotated PDF instead of an image component
                        gr.Markdown("最终的标注PDF和Markdown文件将生成在下方下载区域。")
                        with gr.Row():
                            download_md_pdf = gr.File(label="下载Markdown全文")
                            download_pdf_file = gr.File(label="下载标注后PDF")

        # --- Event Listeners ---
        # Image Tab
        task_selector_img.change(fn=update_custom_prompt_visibility, inputs=task_selector_img, outputs=custom_prompt_img)
        submit_button_img.click(fn=run_image_ocr_task, inputs=[image_input, task_selector_img, custom_prompt_img, resolution_selector_img], outputs=[output_md_img, output_img, download_md_img, download_img_file, status_box_img])

        # PDF Tab
        task_selector_pdf.change(fn=update_custom_prompt_visibility, inputs=task_selector_pdf, outputs=custom_prompt_pdf)
        submit_button_pdf.click(fn=run_pdf_ocr_task, inputs=[pdf_input, task_selector_pdf, custom_prompt_pdf, resolution_selector_pdf], outputs=[output_md_pdf, download_pdf_file, download_md_pdf, download_pdf_file, status_box_pdf])
        
        # Initialize the engine once the UI is loaded
        demo.load(fn=initialize_engine, outputs=[status_box_img])

    return demo

if __name__ == "__main__":
    app = create_ui()
    app.launch(show_error=True)
