import requests
from bs4 import BeautifulSoup
import os

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 失败的页面列表
failed_pages = [17283846, 17283845, 17283843, 17283841]

output_dir = 'downloaded_pages_corrected'

success_count = 0
for page_num in failed_pages:
    url = f'http://www.xn--3mq943byne27j.com/vip_doc/{page_num}.html'
    print(f'正在重新尝试下载: {url}')
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 使用更宽容的编码处理方式
            try:
                # 首先尝试检测编码
                import chardet
                detected = chardet.detect(response.content)
                encoding = detected['encoding']
                
                if encoding and ('gbk' in encoding.lower() or 'gb2312' in encoding.lower()):
                    # 对于可能有问题的字节序列，使用'ignore'或'replace'参数
                    content = response.content.decode(encoding, errors='replace')
                else:
                    # 使用默认方法
                    response.encoding = response.apparent_encoding or 'utf-8'
                    content = response.text
            except:
                # 如果检测失败，尝试多种编码方式
                encodings = ['gbk', 'gb2312', 'cp936', 'utf-8']
                content = None
                for enc in encodings:
                    try:
                        content = response.content.decode(enc, errors='replace')
                        print(f"  使用 {enc} 编码成功")
                        break
                    except:
                        continue
                
                if content is None:
                    print(f"  所有编码方式都失败，使用latin1编码")
                    content = response.content.decode('latin1', errors='replace')
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 提取页面正文（去除脚本和样式）
            for script in soup(['script', 'style']):
                script.decompose()
            
            text_content = soup.get_text()
            # 清理文本
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # 统计字符数
            char_count = len(clean_text)
            chinese_char_count = len([c for c in clean_text if '\u4e00' <= c <= '\u9fff'])
            
            # 保存页面内容，使用正确的编码
            filename = os.path.join(output_dir, f'{page_num}_corrected.html')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n')
                f.write(f'    <title>{soup.title.string if soup.title else f"Page_{page_num}"}</title>\n')
                f.write(f'</head>\n<body>\n')
                f.write(f'<h1>{soup.title.string if soup.title else f"Page_{page_num}"}</h1>\n')
                f.write(f'<p>URL: {url}</p>\n')
                f.write(f'<p>字符数: {char_count}</p>\n')
                f.write(f'<p>汉字数: {chinese_char_count}</p>\n')
                f.write('<hr>\n')
                f.write(clean_text)
                f.write('\n</body>\n</html>')
            
            print(f'  ✓ 成功下载并保存到 {filename} (字符数: {char_count}, 汉字数: {chinese_char_count})')
            success_count += 1
        else:
            print(f'  ✗ 下载失败，状态码: {response.status_code}')
            
    except Exception as e:
        print(f'  ✗ 下载失败，错误: {e}')

print(f'\n重试完成! 成功下载了 {success_count} 个之前失败的页面')
