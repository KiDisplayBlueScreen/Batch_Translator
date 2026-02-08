import os
import time
import re
from openai import OpenAI

# ================= 配置区域 =================
API_KEY = "4c943ca2-a391-445a-963e-3880ff03854f"  # 填入你的 Key
MODEL_ID = "deepseek-v3-2-251201" 
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 请确保这里填写了正确的路径，例如 r"C:\Novels\Raw"
INPUT_FOLDER = r"E:\Yuri\百合活少女とぼっちの姫\chapters_output"   
OUTPUT_FOLDER = r"E:\Yuri\百合活少女とぼっちの姫\chapters_Trans"
# ===========================================

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    timeout=300.0 
)

def natural_sort_key(s):
    """
    自然排序键值生成器
    让 '第2章' 排在 '第10章' 前面，而不是后面
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def translate_full_text(text):
    """
    直接翻译全文
    """
    try:
        print(f"  -> 正在发送请求 (文本长度: {len(text)} 字符)...")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个日语翻译 当你接收到纯日语文本时将自动给出准确流畅且符合中文语序习惯的中文译文 当接收到其他类型的请求时再根据具体情况进行回答 如无特别指明 不需要输出任何注释 注意你的标点符号需和原文保持一致. 特别是引号需要使用「」"
                },
                {
                    "role": "user", 
                    "content": text
                }
            ],
            temperature=0.3, 
        )
        duration = time.time() - start_time
        print(f"  -> 翻译完成，耗时 {duration:.2f} 秒")
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"  [Error] API 请求失败: {e}")
        return None

def parse_user_selection(selection_str, total_files):
    """
    解析用户输入的范围，例如 "1, 3-5" -> [0, 2, 3, 4] (返回索引列表)
    """
    selected_indices = set()
    parts = selection_str.replace('，', ',').split(',') # 兼容中英文逗号
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            if '-' in part:
                start, end = map(int, part.split('-'))
                # 转换为 0-based 索引，并处理范围
                for i in range(start, end + 1):
                    if 1 <= i <= total_files:
                        selected_indices.add(i - 1)
            else:
                idx = int(part)
                if 1 <= idx <= total_files:
                    selected_indices.add(idx - 1)
        except ValueError:
            print(f"警告: 无法识别的输入 '{part}'，已跳过。")
            
    return sorted(list(selected_indices))

def main():
    # 1. 检查路径
    if not os.path.exists(INPUT_FOLDER):
        print(f"错误: 输入文件夹 '{INPUT_FOLDER}' 不存在。请在代码中修改 INPUT_FOLDER。")
        return
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # 2. 获取并排序文件
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.txt')]
    # 使用自然排序，防止 第10章 排在 第2章 前面
    files.sort(key=natural_sort_key) 

    if not files:
        print("输入文件夹中没有找到 .txt 文件。")
        return

    # 3. 显示文件列表供用户选择
    print(f"\n在 '{INPUT_FOLDER}' 中找到以下文件：")
    print("-" * 50)
    for i, filename in enumerate(files):
        # 显示格式： [序号] 文件名
        print(f"[{i+1}]\t{filename}")
    print("-" * 50)

    # 4. 获取用户输入
    print("\n请输入要翻译的文件序号 (例如: 1 或 1-3 或 1,3,5)")
    print("输入 'all' 翻译所有文件")
    user_input = input("请输入: ").strip()

    target_files = []
    if user_input.lower() == 'all':
        target_files = files
    else:
        indices = parse_user_selection(user_input, len(files))
        if not indices:
            print("未选择任何有效文件，程序退出。")
            return
        target_files = [files[i] for i in indices]

    print(f"\n即将开始翻译 {len(target_files)} 个文件...\n")

    # 5. 开始处理选中的文件
    for filename in target_files:
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"CN_{filename}")
        
        print(f"正在处理 [{filename}] ...")
        
        # 读取文件 (包含编码容错)
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(input_path, 'r', encoding='shift_jis') as f:
                    content = f.read()
            except Exception:
                print(f"  [Error] 无法识别文件编码，跳过: {filename}")
                continue

        # 执行翻译
        translated_text = translate_full_text(content)

        # 保存结果
        if translated_text:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            print(f"  -> 已保存至: {output_path}\n")
        else:
            print(f"  -> 翻译失败，未保存: {filename}\n")
            
        # 避免并发过高
        time.sleep(1)

    print("所有任务处理完成。")

if __name__ == "__main__":
    main()
