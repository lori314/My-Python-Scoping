import os
import argparse

# --- 配置 ---
# 要搜索的根目录，默认为当前脚本所在的目录
DEFAULT_PROJECT_DIRECTORY = '.' 
# 输出文件的名称
OUTPUT_FILENAME = 'project_code_snapshot.txt'
# 需要忽略的目录名称（精确匹配）
DIRECTORIES_TO_IGNORE = ['venv', '.venv', '__pycache__', '.git', '.vscode', '.idea']
# 需要忽略的文件扩展名
EXTENSIONS_TO_IGNORE = ['.pyc']

def collect_code_to_file(project_dir, output_file):
    """
    遍历指定目录，将所有非隐藏的.py文件内容整合到一个文件中。

    Args:
        project_dir (str): 项目的根目录路径。
        output_file (str): 输出文件的路径。
    """
    print(f"开始扫描项目目录: {os.path.abspath(project_dir)}")
    
    collected_files = 0
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # os.walk会递归地遍历目录树
        for root, dirs, files in os.walk(project_dir):
            
            # --- 过滤需要忽略的目录 ---
            # 从dirs列表中原地删除要忽略的目录，这样os.walk就不会进入这些目录
            dirs[:] = [d for d in dirs if d not in DIRECTORIES_TO_IGNORE and not d.startswith('.')]
            
            # --- 遍历当前目录下的所有文件 ---
            for filename in files:
                # 检查是否是隐藏文件
                if filename.startswith('.'):
                    continue
                
                # 检查文件扩展名是否需要忽略
                if any(filename.endswith(ext) for ext in EXTENSIONS_TO_IGNORE):
                    continue

                # 我们只关心Python文件
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, project_dir)
                    
                    print(f"  -> 正在添加: {relative_path}")
                    
                    # 写入文件头，标明文件路径
                    outfile.write("=" * 80 + "\n")
                    # 使用正斜杠 '/' 作为路径分隔符，以保持跨平台一致性
                    outfile.write(f"### 文件: {relative_path.replace(os.sep, '/')} ###\n")
                    outfile.write("=" * 80 + "\n\n")
                    
                    try:
                        # 读取源文件内容并写入
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                        
                        outfile.write("\n\n")
                        collected_files += 1
                    except Exception as e:
                        outfile.write(f"*** 无法读取文件: {e} ***\n\n")

    if collected_files > 0:
        print("-" * 40)
        print(f"成功！总共 {collected_files} 个Python文件已被整合到 '{os.path.abspath(output_file)}' 文件中。")
        print("你现在可以把这个文件的内容发给我了。")
    else:
        print("-" * 40)
        print(f"警告：在'{os.path.abspath(project_dir)}'目录中没有找到任何 .py 文件。")


if __name__ == "__main__":
    # 使用 argparse 来处理命令行参数，方便指定目录
    parser = argparse.ArgumentParser(
        description="将一个项目目录下的所有Python(.py)代码文件整合成一个单独的文本文件。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        'directory', 
        nargs='?', 
        default=DEFAULT_PROJECT_DIRECTORY,
        help=f"你想要扫描的项目根目录。\n(默认: '{DEFAULT_PROJECT_DIRECTORY}', 即脚本所在的当前目录)"
    )
    
    parser.add_argument(
        '-o', '--output',
        default=OUTPUT_FILENAME,
        help=f"指定输出文件的名称。\n(默认: '{OUTPUT_FILENAME}')"
    )
    
    args = parser.parse_args()
    
    # 检查指定的目录是否存在
    if not os.path.isdir(args.directory):
        print(f"错误：目录 '{args.directory}' 不存在。请提供一个有效的目录。")
    else:
        collect_code_to_file(args.directory, args.output)