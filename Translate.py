import os
import time
from openai import OpenAI

# ================= 配置区域 =================
API_KEY = ""
# 替换为你的推理接入点 ID (Endpoint ID)
MODEL_ID = "" 
BASE_URL = ""

INPUT_FOLDER = ""
OUTPUT_FOLDER = ""
# ===========================================

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    # 如果网络波动较大，可以适当增加超时时间（默认通常是 600秒，一般足够）
    timeout=300.0 
)

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
            # 确保 max_tokens 足够大，或者直接不传该参数让模型自动处理
            # max_tokens=4096 
        )
        duration = time.time() - start_time
        print(f"  -> 翻译完成，耗时 {duration:.2f} 秒")
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"  [Error] API 请求失败: {e}")
        return None

def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.txt')]
    print(f"找到 {len(files)} 个文件待处理...")

    for filename in files:
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"CN_{filename}")
        
        print(f"正在处理: {filename}")
        
        # 1. 读取文件 (包含编码容错)
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

        # 2. 执行翻译
        translated_text = translate_full_text(content)

        # 3. 保存结果
        if translated_text:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            print(f"  -> 已保存至: {output_path}\n")
        else:
            print(f"  -> 翻译失败，未保存: {filename}\n")
            
        # 避免并发过高触发 QPS 限制，简单休眠一下
        time.sleep(1)

if __name__ == "__main__":
    main()
