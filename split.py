import re
import os

def split_novel_chapters(file_path):
   
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print("UTF-8 读取失败，尝试使用 GBK 编码...")
        with open(file_path, 'r', encoding='gbk') as f:
            content = f.read()

  
    pattern = r'(第\s*\d+\s*[话話])'

    # 4. 使用正则分割内容
    # split 后的列表结构通常为: [前言/空, '第1话', '内容...', '第2话', '内容...', ...]
    parts = re.split(pattern, content)

    # 移除列表开头可能的空字符串或非章节的前言内容（如果第一章前有内容，可选择保留）
    if len(parts) > 0 and not re.match(pattern, parts[0]):
        parts.pop(0)

    # 计算章节数量
    # 因为列表是 [标题, 内容, 标题, 内容...]，所以总长度除以 2 即为话数
    total_chapters = len(parts) // 2
    print(f"分析完成，共发现 {total_chapters} 话。")

    # 5. 创建保存目录
    output_dir = "小说分章"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 6. 循环保存每一话
    print("开始导出...")
    for i in range(0, len(parts) - 1, 2):
        chapter_title = parts[i].strip()   # 例如：第1話
        chapter_content = parts[i+1]       # 章节内容
        
        # 提取数字用于生成统一的文件名 "第n话.txt"
        # 无论原文是"第1話"还是"第 1 话"，都提取出数字 1
        num_match = re.search(r'\d+', chapter_title)
        if num_match:
            chapter_num = num_match.group()
            # 生成文件名：第n话.txt
            file_name = f"第{chapter_num}话.txt"
            
            # 拼接完整路径
            save_path = os.path.join(output_dir, file_name)
            
            # 写入文件
            with open(save_path, 'w', encoding='utf-8') as out_file:
                # 可以选择把标题也写进文件开头
                out_file.write(chapter_title + "\n" + chapter_content)
            
            print(f"已保存: {file_name}")

    print("全部处理完毕！")


if __name__ == '__main__':
   
    input_filename = ''
    split_novel_chapters(input_filename)
