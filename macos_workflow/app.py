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

# --- Internationalization (i18n) Strings ---
I18N_STRINGS = {
    "en": {
        "title": " DeepSeek-OCR for macOS",
        "subtitle": "A high-performance OCR tool running locally on your Mac",
        "usage_guide_header": "💡 Usage Guide & Advanced Tips (Click to expand)",
        "tab_image": "🖼️ Image OCR",
        "tab_pdf": "📄 PDF OCR",
        "input_header": "1. Input Configuration",
        "output_header": "2. Output Results",
        "image_input_label": "Upload Image",
        "task_selector_label": "🎯 Select Task",
        "custom_prompt_label": "✍️ Enter Visual Grounding Instruction",
        "custom_prompt_placeholder": "e.g., <image>\nLocate <|ref|>the black cat<|/ref|> in the image.",
        "resolution_selector_label": "⚙️ Select Resolution Mode",
        "submit_button_image": "🚀 Start Image OCR",
        "submit_button_pdf": "🚀 Start PDF Processing",
        "status_label": "ℹ️ Status",
        "output_md_label": "Recognition Result (Markdown)",
        "output_img_label": "Visualized Annotated Image",
        "download_md_label": "Download Markdown",
        "download_img_label": "Download Annotated Image",
        "pdf_input_label": "Upload PDF File",
        "pdf_output_placeholder": "The final annotated PDF and Markdown files will be generated in the download area below.",
        "download_md_pdf_label": "Download Full Markdown",
        "download_pdf_file_label": "Download Annotated PDF",
        "error_upload_image": "Please upload or paste an image first!",
        "error_upload_pdf": "Please upload a PDF file first!",
        "error_empty_prompt": "Instruction content cannot be empty when using 'Visual Grounding'!",
        "error_init_engine": "Failed to initialize the model engine. Please check the backend logs. Error: {e}",
        "error_pdf_extract": "Failed to extract images from the PDF file. Please check if the file is valid.",
        "status_init_start": "--- First time setup: Initializing OCR Engine... ---",
        "status_init_done": "--- OCR Engine ready. ---",
        "status_init_failed": "FATAL: Could not initialize OCR Engine: {e}",
        "status_init_success": "Engine is ready. Please upload a file and start recognition.",
        "progress_init": "Initializing engine...",
        "progress_infer": "Model inference in progress...",
        "progress_postprocess": "Post-processing results...",
        "progress_pdf_page": "Processing page {i}/{total}...",
        "progress_pdf_aggregate": "Aggregating results...",
        "status_img_success": "✅ Image recognition successful!\nTime taken: {time:.2f} seconds.",
        "status_pdf_success": "✅ PDF processing complete!\nTotal {pages} pages, total time: {time:.2f} seconds.",
        "task_markdown": "Document Conversion (Markdown)",
        "task_free_ocr": "Plain Text Recognition (No layout)",
        "task_parse_figure": "Figure/Formula Parsing",
        "task_describe_image": "Image Description",
        "task_grounding": "Visual Grounding",
        "res_base": "Base (1024x1024)",
        "res_gundam": "Gundam (Dynamic)",
        "res_large": "Large (1280x1280)",
        "res_small": "Small (640x640)",
        "usage_guide_content": "\n### 1. How to choose the right resolution mode?\nChoosing the right resolution is key to balancing speed and accuracy.\n*   **⚡️ Fast Mode (Small)**: Suitable for images with less text and simple layouts (e.g., slides, some books).\n*   **👍 Recommended Mode (Base)**: Best for most regular documents (e.g., reports, papers), providing a good balance between speed and quality.\n*   **🎯 High-Accuracy Mode (Gundam / Large)**: Ideal for images with extremely high text density or large dimensions (e.g., newspapers, posters). The Gundam mode maximizes detail retention with its \"global + local\" view.\n### 2. How to use \"Prompt Instructions\"?\nSelect a task in \"Select Task\", or choose \"Visual Grounding\" and enter a custom instruction to unlock advanced features.\n*   **General Document Processing (Default):**\n    ```\n    <image>\n<|grounding|>Convert the document to markdown.\n    ```\n*   **Plain Text Recognition (Ignore layout):**\n    ```\n    <image>\nFree OCR.\n    ```\n*   **\"Deep Parse\" of Figures or Formulas:**\n    ```\n    <image>\nParse the figure.\n    ```\n*   **General Image Description:**\n    ```\n    <image>\nDescribe this image in detail.\n    ```\n*   **Visual Grounding (Find specific content in the image):**\n    ```\n    <image>\nLocate <|ref|>description of text or object<|/ref|> in the image.\n    ```\n### Productivity Tip\nUse the output of this tool (especially Markdown and table data) as context for a large language model (like GPT-4, Claude, DeepSeek-LLM) to perform summarization, Q&A, or data analysis. This can build a powerful \"Visual Input -> Structured Text -> Language Intelligence\" automated workflow.\n"
    },
    "zh": {
        "title": " DeepSeek-OCR for macOS",
        "subtitle": "一个在您的Mac上本地运行的高性能OCR工具",
        "usage_guide_header": "💡 使用指南与高级技巧 (点击展开)",
        "tab_image": "🖼️ 图像识别 (Image OCR)",
        "tab_pdf": "📄 PDF识别 (PDF OCR)",
        "input_header": "1. 输入配置",
        "output_header": "2. 输出结果",
        "image_input_label": "上传图像",
        "task_selector_label": "🎯 选择任务",
        "custom_prompt_label": "✍️ 输入视觉定位指令",
        "custom_prompt_placeholder": "例如: <image>\nLocate <|ref|>黑猫<|/ref|> in the image.",
        "resolution_selector_label": "⚙️ 选择分辨率模式",
        "submit_button_image": "🚀 开始识别图像",
        "submit_button_pdf": "🚀 开始处理PDF",
        "status_label": "ℹ️ 状态",
        "output_md_label": "识别结果 (Markdown)",
        "output_img_label": "可视化标注图像",
        "download_md_label": "下载Markdown",
        "download_img_label": "下载标注图",
        "pdf_input_label": "上传PDF文件",
        "pdf_output_placeholder": "最终的标注PDF和Markdown文件将生成在下方下载区域。",
        "download_md_pdf_label": "下载Markdown全文",
        "download_pdf_file_label": "下载标注后PDF",
        "error_upload_image": "请先上传或粘贴一张图像！",
        "error_upload_pdf": "请先上传一个PDF文件！",
        "error_empty_prompt": "使用“视觉定位”时，指令内容不能为空！",
        "error_init_engine": "无法初始化模型引擎，请检查后台日志。错误: {e}",
        "error_pdf_extract": "无法从PDF文件中提取图像，请检查文件是否有效。",
        "status_init_start": "--- 第一次启动：正在初始化OCR引擎... ---",
        "status_init_done": "--- OCR引擎已就绪。 ---",
        "status_init_failed": "致命错误：无法初始化OCR引擎: {e}",
        "status_init_success": "引擎已就绪。请上传文件并开始识别。",
        "progress_init": "引擎初始化...",
        "progress_infer": "模型推理中...",
        "progress_postprocess": "后处理结果...",
        "progress_pdf_page": "正在处理第 {i}/{total} 页...",
        "progress_pdf_aggregate": "汇总结果...",
        "status_img_success": "✅ 图像识别成功！\n耗时: {time:.2f} 秒。",
        "status_pdf_success": "✅ PDF处理完成！\n共 {pages} 页，总耗时: {time:.2f} 秒。",
        "task_markdown": "文档转换 (Markdown)",
        "task_free_ocr": "纯文本识别 (无排版)",
        "task_parse_figure": "图表/公式解析",
        "task_describe_image": "图像描述",
        "task_grounding": "视觉定位",
        "res_base": "Base (1024x1024)",
        "res_gundam": "Gundam (动态)",
        "res_large": "Large (1280x1280)",
        "res_small": "Small (640x640)",
        "usage_guide_content": "\n### 1. 如何选择合适的分辨率模式？\n选择正确的分辨率是平衡速度与精度的关键。\n*   **⚡️ 快速模式 (Small)**: 适用于文字较少、排版简单的图像（如幻灯片、部分书籍）。\n*   **👍 推荐模式 (Base)**: 适用于大多数常规文档（如报告、论文），在速度和效果间取得最佳平衡。\n*   **🎯 高精度模式 (Gundam / Large)**: 适用于文字密度极高或尺寸巨大的图像（如报纸、海报）。Gundam模式通过“全局+局部”的视野，能最大限度保留细节。\n### 2. 如何善用“指令提示词”？\n在“选择任务”中选择对应的任务，或选择“视觉定位”并输入自定义指令来解锁高级功能。\n*   **通用文档处理 (默认):**\n    ```\n    <image>\n<|grounding|>Convert the document to markdown.\n    ```\n*   **纯文本识别 (忽略排版):**\n    ```\n    <image>\nFree OCR.\n    ```\n*   **“深度解析”图表或公式:**\n    ```\n    <image>\nParse the figure.\n    ```\n*   **通用图像描述:**\n    ```\n    <image>\nDescribe this image in detail.\n    ```\n*   **视觉定位 (寻找图中特定内容):**\n    ```\n    <image>\nLocate <|ref|>文字或物体描述<|/ref|> in the image.\n    ```\n### 生产力建议\n将本工具的输出（尤其是Markdown和图表数据）作为上下文，输入给大型语言模型（如GPT-4, Claude, DeepSeek-LLM等），进行摘要、问答或数据分析，可以构建起强大的“视觉输入 -> 结构化文本 -> 语言智能”自动化工作流。\n"
    }
}

# --- Global Variables ---
ENGINE = None
# Store language-dependent choices
TASK_PROMPTS = {}
RESOLUTION_MODES = {}

def get_i18n_text(lang, key, **kwargs):
    """Get internationalized text, supporting simple formatting."""
    lang_code = 'zh' if lang == '简体中文' else 'en'
    return I18N_STRINGS[lang_code].get(key, key).format(**kwargs)

def update_language_choices(lang):
    """Update global choice dictionaries based on language."""
    global TASK_PROMPTS, RESOLUTION_MODES
    TASK_PROMPTS = {
        get_i18n_text(lang, "task_markdown"): "<image>\n<|grounding|>Convert the document to markdown.",
        get_i18n_text(lang, "task_free_ocr"): "<image>\nFree OCR.",
        get_i18n_text(lang, "task_parse_figure"): "<image>\nParse the figure.",
        get_i18n_text(lang, "task_describe_image"): "<image>\nDescribe this image in detail.",
        get_i18n_text(lang, "task_grounding"): ""
    }
    RESOLUTION_MODES = {
        get_i18n_text(lang, "res_base"): {"base_size": 1024, "image_size": 1024, "crop_mode": False},
        get_i18n_text(lang, "res_gundam"): {"base_size": 1024, "image_size": 640, "crop_mode": True},
        get_i18n_text(lang, "res_large"): {"base_size": 1280, "image_size": 1280, "crop_mode": False},
        get_i18n_text(lang, "res_small"): {"base_size": 640, "image_size": 640, "crop_mode": False},
    }

# Initialize with default language
update_language_choices('简体中文')

# --- Engine Initialization ---
def initialize_engine(lang='简体中文'):
    global ENGINE
    if ENGINE is None:
        print(get_i18n_text(lang, "status_init_start"))
        try:
            ENGINE = OCREngine(project_root=project_root)
            print(get_i18n_text(lang, "status_init_done"))
        except Exception as e:
            print(get_i18n_text(lang, "status_init_failed", e=e))
            raise gr.Error(get_i18n_text(lang, "error_init_engine", e=e))
    return get_i18n_text(lang, "status_init_success")

# --- Backend Functions for Gradio ---
def run_image_ocr_task(image: Image.Image, task: str, custom_prompt: str, resolution_key: str, lang: str, progress=gr.Progress()):
    if image is None:
        raise gr.Error(get_i18n_text(lang, "error_upload_image"))

    progress(0, desc=get_i18n_text(lang, "progress_init"))
    initialize_engine(lang)

    prompt = list(TASK_PROMPTS.values())[list(TASK_PROMPTS.keys()).index(task)] if task != get_i18n_text(lang, "task_grounding") else custom_prompt
    if not prompt.strip() and task == get_i18n_text(lang, "task_grounding"):
        raise gr.Error(get_i18n_text(lang, "error_empty_prompt"))

    if "<image>" not in prompt:
        prompt = f"<image>\n{prompt}"

    resolution_params = RESOLUTION_MODES[resolution_key]
    config.BASE_SIZE, config.IMAGE_SIZE, config.CROP_MODE = resolution_params['base_size'], resolution_params['image_size'], resolution_params['crop_mode']

    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            image.save(tmp_file.name)
            tmp_image_path = tmp_file.name

        progress(0.5, desc=get_i18n_text(lang, "progress_infer"))
        start_time = time.time()
        result_text = ENGINE.infer(image_path=tmp_image_path, prompt=prompt)
        inference_time = time.time() - start_time
    finally:
        if 'tmp_image_path' in locals() and os.path.exists(tmp_image_path):
            os.remove(tmp_image_path)

    progress(0.9, desc=get_i18n_text(lang, "progress_postprocess"))
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

    status = get_i18n_text(lang, "status_img_success", time=inference_time)
    return result_text, annotated_image, md_path, img_path, status

def run_pdf_ocr_task(pdf_file, task: str, custom_prompt: str, resolution_key: str, lang: str, progress=gr.Progress()):
    if pdf_file is None:
        raise gr.Error(get_i18n_text(lang, "error_upload_pdf"))

    progress(0, desc=get_i18n_text(lang, "progress_init"))
    initialize_engine(lang)
    pdf_path = pdf_file.name

    prompt = list(TASK_PROMPTS.values())[list(TASK_PROMPTS.keys()).index(task)] if task != get_i18n_text(lang, "task_grounding") else custom_prompt
    if not prompt.strip() and task == get_i18n_text(lang, "task_grounding"):
        raise gr.Error(get_i18n_text(lang, "error_empty_prompt"))
        
    if "<image>" not in prompt:
        prompt = f"<image>\n{prompt}"

    resolution_params = RESOLUTION_MODES[resolution_key]
    config.BASE_SIZE, config.IMAGE_SIZE, config.CROP_MODE = resolution_params['base_size'], resolution_params['image_size'], resolution_params['crop_mode']

    page_images = pdf_to_images(pdf_path)
    if not page_images:
        raise gr.Error(get_i18n_text(lang, "error_pdf_extract"))

    all_md_results, annotated_pages = [], []
    total_time = 0

    for i, page_image in enumerate(page_images):
        progress(i / len(page_images), desc=get_i18n_text(lang, "progress_pdf_page", i=i+1, total=len(page_images)))
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

    progress(0.9, desc=get_i18n_text(lang, "progress_pdf_aggregate"))
    final_md = "\n\n<--- Page Split --->\n\n".join(all_md_results)
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
        tmp_md.write(final_md)
        md_path = tmp_md.name

    pdf_out_path = None
    if annotated_pages:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            save_images_to_pdf(annotated_pages, tmp_pdf.name)
            pdf_out_path = tmp_pdf.name

    status = get_i18n_text(lang, "status_pdf_success", pages=len(page_images), time=total_time)
    return final_md, None, md_path, pdf_out_path, status

def update_custom_prompt_visibility(task: str, lang: str):
    return gr.update(visible=(task == get_i18n_text(lang, "task_grounding")))

# --- Gradio UI Definition ---
def create_ui():
    with gr.Blocks(theme=gr.themes.Soft(), css="footer {display: none !important}") as demo:
        
        lang = gr.Radio(["简体中文", "English"], label="Language / 语言", value="简体中文", interactive=True)

        # UI Components
        title = gr.Markdown("<h1><center> DeepSeek-OCR for macOS</center></h1>")
        subtitle = gr.Markdown("#### <center>一个在您的Mac上本地运行的高性能OCR工具</center>")
        usage_guide_accordion = gr.Accordion("💡 使用指南与高级技巧 (点击展开)", open=False)
        with usage_guide_accordion:
            usage_guide_content = gr.Markdown(get_i18n_text('简体中文', 'usage_guide_content'))

        with gr.Tabs() as tabs:
            with gr.TabItem("🖼️ 图像识别 (Image OCR)", id=0) as tab_image:
                with gr.Row(equal_height=True):
                    with gr.Column(scale=1):
                        input_header_img = gr.Markdown("### 1. 输入配置")
                        image_input = gr.Image(type="pil", label="上传图像", sources=['upload', 'clipboard'])
                        task_selector_img = gr.Dropdown(label="🎯 选择任务", choices=list(TASK_PROMPTS.keys()), value=list(TASK_PROMPTS.keys())[0])
                        custom_prompt_img = gr.Textbox(label="✍️ 输入视觉定位指令", placeholder=get_i18n_text('简体中文', 'custom_prompt_placeholder'), visible=False, lines=3)
                        resolution_selector_img = gr.Dropdown(label="⚙️ 选择分辨率模式", choices=list(RESOLUTION_MODES.keys()), value=list(RESOLUTION_MODES.keys())[0])
                        submit_button_img = gr.Button("🚀 开始识别图像", variant="primary")
                    with gr.Column(scale=1):
                        output_header_img = gr.Markdown("### 2. 输出结果")
                        status_box_img = gr.Textbox(label="ℹ️ 状态", interactive=False, lines=4)
                        output_md_img = gr.Markdown(label="识别结果 (Markdown)")
                        output_img = gr.Image(type="pil", label="可视化标注图像")
                        with gr.Row():
                            download_md_img = gr.File(label="下载Markdown")
                            download_img_file = gr.File(label="下载标注图")
            
            with gr.TabItem("📄 PDF识别 (PDF OCR)", id=1) as tab_pdf:
                with gr.Row(equal_height=True):
                    with gr.Column(scale=1):
                        input_header_pdf = gr.Markdown("### 1. 输入配置")
                        pdf_input = gr.File(label="上传PDF文件", file_types=['.pdf'])
                        task_selector_pdf = gr.Dropdown(label="🎯 选择任务", choices=list(TASK_PROMPTS.keys()), value=list(TASK_PROMPTS.keys())[0])
                        custom_prompt_pdf = gr.Textbox(label="✍️ 输入视觉定位指令", placeholder=get_i18n_text('简体中文', 'custom_prompt_placeholder'), visible=False, lines=3)
                        resolution_selector_pdf = gr.Dropdown(label="⚙️ 选择分辨率模式", choices=list(RESOLUTION_MODES.keys()), value=list(RESOLUTION_MODES.keys())[0])
                        submit_button_pdf = gr.Button("🚀 开始处理PDF", variant="primary")
                    with gr.Column(scale=1):
                        output_header_pdf = gr.Markdown("### 2. 输出结果")
                        status_box_pdf = gr.Textbox(label="ℹ️ 状态", interactive=False, lines=4)
                        output_md_pdf = gr.Markdown(label="识别结果 (Markdown)")
                        pdf_output_placeholder = gr.Markdown("最终的标注PDF和Markdown文件将生成在下方下载区域。")
                        with gr.Row():
                            download_md_pdf = gr.File(label="下载Markdown全文")
                            download_pdf_file = gr.File(label="下载标注后PDF")
        
        # --- Language Change Handler ---
        def update_ui_language(language):
            update_language_choices(language)
            
            new_task_choices = list(TASK_PROMPTS.keys())
            new_res_choices = list(RESOLUTION_MODES.keys())
            
            # Special handling for status boxes
            status_box_img_update = gr.update(label=get_i18n_text(language, 'status_label'))
            status_box_pdf_update = gr.update(label=get_i18n_text(language, 'status_label'))
            if ENGINE is not None:
                new_status_text = get_i18n_text(language, 'status_init_success')
                status_box_img_update = gr.update(label=get_i18n_text(language, 'status_label'), value=new_status_text)
                status_box_pdf_update = gr.update(label=get_i18n_text(language, 'status_label'), value=new_status_text)

            return (
                gr.update(value=f"<h1><center>{get_i18n_text(language, 'title')}</center></h1>"),
                gr.update(value=f"#### <center>{get_i18n_text(language, 'subtitle')}</center>"),
                gr.update(label=get_i18n_text(language, 'usage_guide_header')),
                gr.update(value=get_i18n_text(language, 'usage_guide_content')),
                gr.update(label=get_i18n_text(language, 'tab_image')),
                gr.update(label=get_i18n_text(language, 'tab_pdf')),
                gr.update(value=f"### {get_i18n_text(language, 'input_header')}"),
                gr.update(value=f"### {get_i18n_text(language, 'output_header')}"),
                gr.update(label=get_i18n_text(language, 'image_input_label')),
                gr.update(label=get_i18n_text(language, 'task_selector_label'), choices=new_task_choices, value=new_task_choices[0]),
                gr.update(label=get_i18n_text(language, 'custom_prompt_label'), placeholder=get_i18n_text(language, 'custom_prompt_placeholder')),
                gr.update(label=get_i18n_text(language, 'resolution_selector_label'), choices=new_res_choices, value=new_res_choices[0]),
                gr.update(value=get_i18n_text(language, 'submit_button_image')),
                status_box_img_update, # Updated status box for images
                gr.update(label=get_i18n_text(language, 'output_md_label')),
                gr.update(label=get_i18n_text(language, 'output_img_label')),
                gr.update(label=get_i18n_text(language, 'download_md_label')),
                gr.update(label=get_i18n_text(language, 'download_img_label')),
                gr.update(value=f"### {get_i18n_text(language, 'input_header')}"),
                gr.update(value=f"### {get_i18n_text(language, 'output_header')}"),
                gr.update(label=get_i18n_text(language, 'pdf_input_label')),
                gr.update(label=get_i18n_text(language, 'task_selector_label'), choices=new_task_choices, value=new_task_choices[0]),
                gr.update(label=get_i18n_text(language, 'custom_prompt_label'), placeholder=get_i18n_text(language, 'custom_prompt_placeholder')),
                gr.update(label=get_i18n_text(language, 'resolution_selector_label'), choices=new_res_choices, value=new_res_choices[0]),
                gr.update(value=get_i18n_text(language, 'submit_button_pdf')),
                status_box_pdf_update, # Updated status box for PDFs
                gr.update(label=get_i18n_text(language, 'output_md_label')),
                gr.update(value=get_i18n_text(language, 'pdf_output_placeholder')),
                gr.update(label=get_i18n_text(language, 'download_md_pdf_label')),
                gr.update(label=get_i18n_text(language, 'download_pdf_file_label')),
            )

        # --- Event Listeners ---
        outputs_list = [
            title, subtitle, usage_guide_accordion, usage_guide_content, tab_image, tab_pdf,
            input_header_img, output_header_img, image_input, task_selector_img, custom_prompt_img,
            resolution_selector_img, submit_button_img, status_box_img, output_md_img, output_img,
            download_md_img, download_img_file, input_header_pdf, output_header_pdf, pdf_input,
            task_selector_pdf, custom_prompt_pdf, resolution_selector_pdf, submit_button_pdf,
            status_box_pdf, output_md_pdf, pdf_output_placeholder, download_md_pdf, download_pdf_file
        ]
        lang.change(fn=update_ui_language, inputs=lang, outputs=outputs_list)

        task_selector_img.change(fn=update_custom_prompt_visibility, inputs=[task_selector_img, lang], outputs=custom_prompt_img)
        submit_button_img.click(fn=run_image_ocr_task, inputs=[image_input, task_selector_img, custom_prompt_img, resolution_selector_img, lang], outputs=[output_md_img, output_img, download_md_img, download_img_file, status_box_img])

        task_selector_pdf.change(fn=update_custom_prompt_visibility, inputs=[task_selector_pdf, lang], outputs=custom_prompt_pdf)
        submit_button_pdf.click(fn=run_pdf_ocr_task, inputs=[pdf_input, task_selector_pdf, custom_prompt_pdf, resolution_selector_pdf, lang], outputs=[output_md_pdf, download_pdf_file, download_md_pdf, download_pdf_file, status_box_pdf])
        
        # Pass the language to the initial load function
        def on_load(language):
            return initialize_engine(language)

        demo.load(fn=on_load, inputs=[lang], outputs=[status_box_img])
        # Also update the PDF status box on load
        demo.load(fn=None, inputs=None, outputs=[status_box_pdf], js="(x) => document.querySelector('#close_button > .button_primary').click()")
        # A bit of a hack to sync the status boxes. The JS finds the first primary button (our image submit button)
        # and simulates a click on its invisible close button sibling to trigger its status update, which we can then use.
        # A cleaner way would require more complex Gradio state management.
        # Let's try a simpler way first.
        def sync_status_boxes(img_status):
            return img_status
        submit_button_img.click(fn=sync_status_boxes, inputs=status_box_img, outputs=status_box_pdf)
        demo.load(fn=sync_status_boxes, inputs=status_box_img, outputs=status_box_pdf)

    return demo

if __name__ == "__main__":
    app = create_ui()
    app.launch(show_error=True)
