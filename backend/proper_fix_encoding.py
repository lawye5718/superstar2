import os
import codecs

def fix_gbk_utf8_mismatch(file_path):
    """
    修复因GBK内容被误认为UTF-8解析而导致的乱码问题
    当中文内容以GBK编码，但被当作UTF-8解析时会出现乱码
    """
    try:
        # 读取文件的二进制内容
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        # 先尝试直接用UTF-8解码
        try:
            content = raw_content.decode('utf-8')
        except UnicodeDecodeError:
            # 如果UTF-8失败，尝试用GBK
            content = raw_content.decode('gbk')
        
        # 检查是否包含典型的乱码字符
        # 乱码通常表现为连续的不可读字符，如 
        # 这种情况通常是GB2312/GBK编码内容被错误地当UTF-8解码
        
        # 如果内容中有很多符号，说明可能是乱码
        replacement_char_count = content.count('')
        if replacement_char_count > len(content) * 0.01:  # 如果符号超过1%
            # 尝试修复乱码：将乱码内容重新编码为GBK再解码
            try:
                # 将内容编码为字节，然后用GBK解码
                # 有时需要将错误的UTF-8内容先转回字节形式
                temp_bytes = content.encode('latin1', errors='ignore')  # 使用latin1保留字节值
                # 然后尝试用GBK解码
                try:
                    content = temp_bytes.decode('gbk', errors='ignore')
                except:
                    # 如果还是不行，尝试cp936（简体中文）
                    content = temp_bytes.decode('cp936', errors='ignore')
            except:
                pass  # 如果失败，使用原来的内容
        
        # 确保HTML头部有正确的编码声明
        if '<meta charset="UTF-8">' not in content:
            if '<head>' in content:
                content = content.replace('<head>', '<head>\n    <meta charset="UTF-8">', 1)
            elif '<HEAD>' in content:
                content = content.replace('<HEAD>', '<HEAD>\n    <meta charset="UTF-8">', 1)
            elif '<html>' in content:
                content = content.replace('<html>', '<html>\n<head>\n    <meta charset="UTF-8">\n</head>', 1)
            elif '<HTML>' in content:
                content = content.replace('<HTML>', '<HTML>\n<head>\n    <meta charset="UTF-8">\n</head>', 1)
            else:
                content = '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n</head>\n<body>\n' + content + '\n</body>\n</html>'
        
        # 以UTF-8保存文件
        with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
            f.write(content)
        
        print(f"✓ 已修复文件: {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ 修复文件失败 {file_path}: {str(e)}")
        return False

def fix_all_files_in_directory(directory):
    """
    修复目录下所有HTML文件
    """
    html_files = [f for f in os.listdir(directory) if f.lower().endswith('.html')]
    success_count = 0
    
    for filename in html_files:
        file_path = os.path.join(directory, filename)
        if fix_gbk_utf8_mismatch(file_path):
            success_count += 1
    
    return success_count, len(html_files)

# 修复下载目录中的所有文件
directory = 'downloaded_pages'
success, total = fix_all_files_in_directory(directory)

print(f"\n编码修复完成!")
print(f"成功修复: {success} 个文件")
print(f"总文件数: {total} 个文件")

# 现在尝试重新下载一次特定的页面，确保使用正确的编码
import requests
from bs4 import BeautifulSoup

print(f"\n尝试重新下载页面以确保正确的编码...")
url = 'http://www.xn--3mq943byne27j.com/vip_doc/17283878.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    # 尝试检测响应的编码
    if response.encoding.lower() in ['gbk', 'gb2312', 'cp936']:
        # 如果原始编码是GBK系列，先用原始编码解码，再用UTF-8保存
        content = response.content.decode(response.apparent_encoding or response.encoding)
    else:
        # 否则使用默认方法
        response.encoding = 'utf-8'
        content = response.text
    
    # 解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # 提取正文
    for script in soup(['script', 'style']):
        script.decompose()
    
    text_content = soup.get_text()
    lines = (line.strip() for line in text_content.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
    clean_text = ' '.join(chunk for chunk in chunks if chunk)
    
    # 统计字符
    char_count = len(clean_text)
    chinese_char_count = len([c for c in clean_text if '\u4e00' <= c <= '\u9fff'])
    
    # 保存到文件
    filename = os.path.join(directory, '17283878_fixed.html')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n')
        f.write(f'    <title>{soup.title.string if soup.title else "Page_17283878"}</title>\n')
        f.write(f'</head>\n<body>\n')
        f.write(f'<h1>{soup.title.string if soup.title else "Page_17283878"}</h1>\n')
        f.write(f'<p>URL: {url}</p>\n')
        f.write(f'<p>字符数: {char_count}</p>\n')
        f.write(f'<p>汉字数: {chinese_char_count}</p>\n')
        f.write('<hr>\n')
        f.write(clean_text)
        f.write('\n</body>\n</html>')
    
    print(f"✓ 已重新下载并修复页面: {filename}")
    
    # 显示修复后的部分内容
    print(f"\n修复后的页面内容预览:")
    print(clean_text[:500])  # 显示前500个字符
    
except Exception as e:
    print(f"✗ 重新下载失败: {str(e)}")
    print(f"原始文件中可能存在乱码，但浏览器应能正确显示，因为已添加了<meta charset=\"UTF-8\">标签")
