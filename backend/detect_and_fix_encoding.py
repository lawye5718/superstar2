import os
import chardet
import codecs

def fix_file_encoding_with_detection(file_path):
    """
    使用编码检测来修复单个文件的编码问题
    """
    try:
        # 读取文件的原始二进制内容
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # 检测编码
        detected_encoding = chardet.detect(raw_data)
        confidence = detected_encoding['confidence']
        encoding = detected_encoding['encoding']
        
        print(f"检测到文件 {file_path} 的编码: {encoding} (置信度: {confidence:.2f})")
        
        # 如果置信度太低，我们可能需要尝试其他编码
        if confidence < 0.5:
            # 对于中文内容，通常可能是gbk或gb2312
            encodings_to_try = ['gbk', 'gb2312', 'utf-8', 'big5']
            content = None
            for enc in encodings_to_try:
                try:
                    content = raw_data.decode(enc)
                    print(f"  尝试使用 {enc} 编码成功")
                    encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                print(f"  无法解码文件 {file_path}，使用原始内容")
                return False
        else:
            # 使用检测到的编码解码
            content = raw_data.decode(encoding)
        
        # 修复HTML头部，确保有适当的字符集声明
        if '<meta charset=' not in content.lower():
            # 查找<head>标签
            if '<head>' in content or '<HEAD>' in content:
                if '<head>' in content:
                    content = content.replace('<head>', '<head>\n    <meta charset="UTF-8">', 1)
                else:
                    content = content.replace('<HEAD>', '<HEAD>\n    <meta charset="UTF-8">', 1)
            else:
                # 如果没有head标签，查找<html>标签
                if '<html>' in content or '<HTML>' in content:
                    if '<html>' in content:
                        content = content.replace('<html>', '<html>\n<head>\n    <meta charset="UTF-8">\n</head>', 1)
                    else:
                        content = content.replace('<HTML>', '<HTML>\n<head>\n    <meta charset="UTF-8">\n</head>', 1)
                else:
                    # 如果都没有，添加完整的HTML结构
                    content = f'<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n</head>\n<body>\n{content}\n</body>\n</html>'
        
        # 以UTF-8编码保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ 已修复文件编码: {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ 修复文件失败 {file_path}: {str(e)}")
        return False

def fix_all_html_files(directory):
    """
    修复目录下所有HTML文件的编码问题
    """
    fixed_count = 0
    total_count = 0
    
    for filename in os.listdir(directory):
        if filename.lower().endswith('.html'):
            file_path = os.path.join(directory, filename)
            total_count += 1
            if fix_file_encoding_with_detection(file_path):
                fixed_count += 1
    
    return fixed_count, total_count

# 修复下载目录下的所有HTML文件
download_dir = 'downloaded_pages'
fixed, total = fix_all_html_files(download_dir)

print(f"\n编码检测与修复完成!")
print(f"总文件数: {total}")
print(f"成功修复: {fixed}")
print(f"修复失败: {total - fixed}")

# 验证修复结果
if os.path.exists(os.path.join(download_dir, '17283878.html')):
    # 重新检测这个文件
    with open(os.path.join(download_dir, '17283878.html'), 'rb') as f:
        raw_data = f.read()
    detected_encoding = chardet.detect(raw_data)
    print(f"\n验证修复后的文件编码: {detected_encoding}")
    
    # 读取并显示部分内容
    with open(os.path.join(download_dir, '17283878.html'), 'r', encoding='utf-8') as f:
        sample_content = f.read(1000)
        print("\n修复后的示例内容:")
        lines = sample_content.split('\n')
        for i, line in enumerate(lines[:20]):
            # 只显示前100个字符以避免输出过长
            print(f"{i+1:2d}: {line[:100]}{'...' if len(line) > 100 else ''}")
            if i >= 10:  # 限制输出行数
                break
