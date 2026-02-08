import re
import os

def split_novel(input_file, output_dir):
    # 1. 如果输出目录不存在，则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建输出目录: {output_dir}")

    # 2. 定义正则表达式
    # 解释：
    # ^         : 匹配行首
    # 第        : 字面量“第”
    # [...]     : 匹配集合，包含半角数字0-9、全角数字０-９、以及常见汉字数字
    # +         : 匹配前面的数字一次或多次
    # 章        : 字面量“章”
    # [\s　]    : 匹配半角空格(\s) 或 全角空格(　)
    # .*        : 匹配标题剩余的所有字符
    pattern = re.compile(r"^第[0-9０-９一二三四五六七八九十百千万零〇]+章[\s　].*")

    current_file = None
    chapter_count = 0

    try:
        # 3. 打开源文件 (注意编码，如果是日文系统生成的txt可能是 shift_jis，这里默认 utf-8)
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                
                # 4. 检查这一行是否是章节标题
                if pattern.match(stripped_line):
                    # 如果之前有打开的文件，先关闭它
                    if current_file:
                        current_file.close()
                    
                    # 提取文件名（去掉首尾空格）
                    filename = stripped_line
                    
                    # 5. 清理文件名中的非法字符 (Windows/Linux 文件名不允许 \ / : * ? " < > |)
                    # 将非法字符替换为下划线
                    invalid_chars = r'[\\/:*?"<>|]'
                    filename = re.sub(invalid_chars, '_', filename)
                    
                    # 拼接完整路径
                    file_path = os.path.join(output_dir, filename + ".txt")
                    
                    # 打开新文件写入
                    current_file = open(file_path, 'w', encoding='utf-8')
                    current_file.write(line) # 写入标题行
                    
                    chapter_count += 1
                    print(f"正在提取: {filename}")
                    
                else:
                    # 如果不是标题，且当前有打开的文件，则写入内容
                    if current_file:
                        current_file.write(line)

        print(f"\n处理完成！共拆分出 {chapter_count} 个章节，保存在 '{output_dir}' 文件夹中。")

    except FileNotFoundError:
        print(f"错误：找不到文件 '{input_file}'，请确认文件名是否正确。")
    except UnicodeDecodeError:
        print("错误：文件编码读取失败。请尝试将代码中的 encoding='utf-8' 改为 'gbk' 或 'shift_jis'。")
    finally:
        if current_file:
            current_file.close()

# --- 配置区域 ---
# 输入文件名
source_file = ''
# 输出文件夹名称
output_folder = 'chapters_output'

# 运行函数
if __name__ == '__main__':
    split_novel(source_file, output_folder)
