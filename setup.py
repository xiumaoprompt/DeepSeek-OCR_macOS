
import os
import shutil
import subprocess
import sys

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "macos_workflow", "config_macos.py")
PATCH_SOURCE_PATH = os.path.join(PROJECT_ROOT, "macos_workflow", "patched_modeling_deepseekocr.py")

# --- Helper Functions ---

def print_color(text, color="green"):
    """Prints text in a given color."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "end": "\033[0m",
    }
    print(f"{colors.get(color, colors['green'])}{text}{colors['end']}")

def get_model_path_from_user():
    """Prompts the user to provide the path to the DeepSeek-OCR model directory."""
    print_color("\n--- DeepSeek-OCR for macOS Setup ---", "blue")
    print("此脚本将帮助您配置运行环境。")
    
    while True:
        print("\n步骤 1: 请提供您从Hugging Face下载的 'DeepSeek-OCR' 模型文件夹的路径。")
        user_path = input("您可以直接将文件夹拖拽到此窗口，然后按回车键: ").strip()

        # Handle paths wrapped in quotes (common when dragging from Finder)
        if user_path.startswith(("'", '"')) and user_path.endswith(("'", '"')):
            user_path = user_path[1:-1]

        # Validate the path
        model_file_check = os.path.join(user_path, "modeling_deepseekocr.py")
        config_file_check = os.path.join(user_path, "config.json")

        if os.path.isdir(user_path) and os.path.basename(user_path) == "DeepSeek-OCR" and os.path.exists(model_file_check) and os.path.exists(config_file_check):
            print_color(f"✅ 路径验证成功: {user_path}")
            return user_path
        else:
            print_color("❌ 路径无效。", "red")
            print("请确保您提供的是完整的 'DeepSeek-OCR' 文件夹路径，且其中包含 'modeling_deepseekocr.py' 和 'config.json' 文件。")

def apply_patch(model_path):
    """Copies the patched modeling file into the user's model directory."""
    print("\n步骤 2: 应用macOS兼容性补丁...")
    target_file = os.path.join(model_path, "modeling_deepseekocr.py")
    backup_file = os.path.join(model_path, "modeling_deepseekocr.py.backup")

    try:
        # Back up the original file if it exists and a backup doesn't already exist
        if os.path.exists(target_file) and not os.path.exists(backup_file):
            shutil.copy2(target_file, backup_file)
            print(f"  - 已备份原始文件到: {backup_file}")
        
        # Copy our patched file
        shutil.copy2(PATCH_SOURCE_PATH, target_file)
        print_color("  - ✅ 成功应用补丁文件。", "green")
        return True
    except Exception as e:
        print_color(f"  - ❌ 应用补丁失败: {e}", "red")
        return False

def create_symlink(model_path):
    """Creates the necessary symlink for Python importing."""
    print("\n步骤 3: 创建Python导入所需的软链接...")
    original_name = os.path.basename(model_path) # Should be "DeepSeek-OCR"
    symlink_name = original_name.replace('-', '_') # Becomes "DeepSeek_OCR"
    
    # Ensure we are in the correct directory to create the symlink
    parent_dir = os.path.dirname(model_path)
    
    try:
        # Create __init__.py to ensure the directory is treated as a package
        init_path = os.path.join(model_path, "__init__.py")
        if not os.path.exists(init_path):
            open(init_path, 'a').close()
            print(f"  - 已创建: {init_path}")

        # Create the symlink
        symlink_path = os.path.join(parent_dir, symlink_name)
        if not os.path.lexists(symlink_path):
            os.symlink(original_name, symlink_path, target_is_directory=True)
            print_color(f"  - ✅ 成功创建软链接: {symlink_path} -> {original_name}")
        else:
            print_color(f"  - 软链接已存在，跳过创建。", "yellow")
        return True
    except Exception as e:
        print_color(f"  - ❌ 创建软链接失败: {e}", "red")
        print("  - 请检查您是否具有在此目录创建链接的权限。\n")
        return False

def update_config_file(model_path):
    """Updates the config_macos.py file with the correct model path."""
    print("\n步骤 4: 更新工作流配置文件...")
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.strip().startswith("MODEL_PATH"):
                new_lines.append(f'MODEL_PATH = "{model_path}"\n')
            else:
                new_lines.append(line)
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print_color(f"  - ✅ 成功更新配置文件: {CONFIG_PATH}")
        return True
    except Exception as e:
        print_color(f"  - ❌ 更新配置文件失败: {e}", "red")
        return False

# --- Main Execution ---

if __name__ == "__main__":
    model_dir = get_model_path_from_user()
    
    if not apply_patch(model_dir):
        sys.exit(1)
        
    if not create_symlink(model_dir):
        sys.exit(1)

    if not update_config_file(model_dir):
        sys.exit(1)

    print_color("\n🎉 全部设置已成功完成!", "blue")
    print("您现在可以启动Gradio应用了:")
    print_color("\n    python -m macos_workflow.app\n", "yellow")
