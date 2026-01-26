import os
import re

def fix_html_encoding(file_path):
    """
    修复单个HTML文件的编码问题
    """
    try:
        # 尝试以UTF-8读取文件
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 检查是否存在<meta>编码标签
        meta_charset_pattern = r'<meta[^>]*charset\s*=\s*["\']?([^"\'\s/>]+)["\']?[^>]*/?>|<meta[^>]*charset\s*=\s*([a-zA-Z0-9\-]+)[^>]*>'
        
        # 查找现有的字符集声明
        existing_meta = re.search(meta_charset_pattern, content, re.IGNORECASE)
        
        if existing_meta:
            # 如果存在meta标签，替换为UTF-8
            content = re.sub(meta_charset_pattern, '<meta charset="UTF-8">', content, count=1, flags=re.IGNORECASE)
        else:
            # 如果不存在，插入meta标签到<head>部分
            head_match = re.search(r'<head[^>]*>', content, re.IGNORECASE)
            if head_match:
                head_end_pos = head_match.end()
                content = content[:head_end_pos] + '\n    <meta charset="UTF-8">\n' + content[head_end_pos:]
            else:
                # 如果没有<head>标签，在<html>标签后插入
                html_match = re.search(r'<html[^>]*>', content, re.IGNORECASE)
                if html_match:
                    html_end_pos = html_match.end()
                    content = content[:html_end_pos] + '\n<head>\n    <meta charset="UTF-8">\n</head>\n' + content[html_end_pos:]
        
        # 确保以UTF-8编码保存文件
        with open(file_path, 'w', encoding='utf-8', errors='strict') as f:
            f.write(content)
        
        print(f"✓ 已修复文件: {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ 修复文件失败 {file_path}: {str(e)}")
        return False

def fix_all_html_files(directory):
    """
    修复目录下所有的HTML文件
    """
    fixed_count = 0
    total_count = 0
    
    for filename in os.listdir(directory):
        if filename.lower().endswith('.html'):
            file_path = os.path.join(directory, filename)
            total_count += 1
            if fix_html_encoding(file_path):
                fixed_count += 1
    
    return fixed_count, total_count

# 修复下载目录下的所有HTML文件
download_dir = 'downloaded_pages'
fixed, total = fix_all_html_files(download_dir)

print(f"\n编码修复完成!")
print(f"总文件数: {total}")
print(f"成功修复: {fixed}")
print(f"修复失败: {total - fixed}")

# 验证修复结果，检查一个文件的内容
if os.path.exists(os.path.join(download_dir, '17283878.html')):
    with open(os.path.join(download_dir, '17283878.html'), 'r', encoding='utf-8') as f:
        sample_content = f.read(500)  # 读取前500个字符作为样本
        print(f"\n示例文件头部内容:")
        print(sample_content[:sample_content.find('</body>') if '</body>' in sample_content else 500])
