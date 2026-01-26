import os
import codecs

def decode_gbk_bytes_as_utf8(text_with_gbk_bytes):
    """
    尝试将错误解码的文本重新解码
    当原始文本是GBK编码但被当成了UTF-8解码时，会产生乱码
    """
    try:
        # 将错误解码的字符串重新编码为字节，再以正确的编码解码
        # 乱码字符通常是由于GBK被误认为UTF-8导致的
        gbk_bytes = text_with_gbk_bytes.encode('iso-8859-1')  # 先转回字节
        decoded_text = gbk_bytes.decode('gbk', errors='ignore')  # 用GBK解码
        return decoded_text
    except:
        try:
            # 备用方法：使用cp936 (简体中文Windows编码)
            gbk_bytes = text_with_gbk_bytes.encode('iso-8859-1')
            decoded_text = gbk_bytes.decode('cp936', errors='ignore')
            return decoded_text
        except:
            # 如果都不行，返回原文本
            return text_with_gbk_bytes

def fix_file_encoding(file_path):
    """
    修复单个文件的中文编码问题
    """
    try:
        # 以二进制模式读取原始内容
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        # 尝试用UTF-8解码
        try:
            content = raw_content.decode('utf-8')
        except UnicodeDecodeError:
            # 如果UTF-8失败，尝试用GBK解码
            content = raw_content.decode('gbk')
        
        # 检查是否包含乱码字符（通常是中文被错误解码的结果）
        if any(ord(c) > 127 for c in content):
            # 检查是否有大量乱码字符
            chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
            unknown_chars = sum(1 for c in content if ord(c) > 255 and '\u4e00' > c or c > '\u9fff')
            
            # 如果乱码字符很多但中文字符很少，可能需要重新解码
            if unknown_chars > chinese_chars * 2 and unknown_chars > 10:
                # 尝试重新解码
                try:
                    content = decode_gbk_bytes_as_utf8(content)
                except:
                    pass  # 如果失败，使用原内容
        
        # 确保<head>标签中有UTF-8编码声明
        if '<head>' not in content and '<HEAD>' not in content:
            # 如果没有head标签，添加它
            if '<html>' in content:
                content = content.replace('<html>', '<html>\n<head>\n    <meta charset="UTF-8">\n</head>', 1)
            elif '<HTML>' in content:
                content = content.replace('<HTML>', '<HTML>\n<head>\n    <meta charset="UTF-8">\n</head>', 1)
            else:
                # 如果连html标签都没有，添加基本结构
                content = '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n</head>\n<body>\n' + content + '\n</body>\n</html>'
        else:
            # 如果有head标签，确保有charset声明
            if '<meta charset=' not in content and '<META CHARSET=' not in content:
                if '<head>' in content:
                    content = content.replace('<head>', '<head>\n    <meta charset="UTF-8">', 1)
                elif '<HEAD>' in content:
                    content = content.replace('<HEAD>', '<HEAD>\n    <meta charset="UTF-8">', 1)
                else:
                    # 在<html>标签后添加head部分
                    if '<html>' in content:
                        content = content.replace('<html>', '<html>\n<head>\n    <meta charset="UTF-8">\n</head>', 1)
                    elif '<HTML>' in content:
                        content = content.replace('<HTML>', '<HTML>\n<head>\n    <meta charset="UTF-8">\n</head>', 1)
        
        # 以UTF-8编码保存
        with open(file_path, 'w', encoding='utf-8', errors='strict') as f:
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
            if fix_file_encoding(file_path):
                fixed_count += 1
    
    return fixed_count, total_count

# 修复下载目录下的所有HTML文件
download_dir = 'downloaded_pages'
fixed, total = fix_all_html_files(download_dir)

print(f"\n中文编码修复完成!")
print(f"总文件数: {total}")
print(f"成功修复: {fixed}")
print(f"修复失败: {total - fixed}")

# 验证修复结果
if os.path.exists(os.path.join(download_dir, '17283878.html')):
    with open(os.path.join(download_dir, '17283878.html'), 'r', encoding='utf-8') as f:
        sample_content = f.read(1000)  # 读取前1000个字符作为样本
        print(f"\n修复后的示例文件头部内容:")
        # 显示开头部分，查找中文内容
        lines = sample_content.split('\n')
        for i, line in enumerate(lines[:20]):  # 检查前20行
            print(f"{i+1:2d}: {line}")
            if i > 15:  # 避免输出太多
                break
