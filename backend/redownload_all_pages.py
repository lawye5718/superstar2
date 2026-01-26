import requests
from bs4 import BeautifulSoup
import os
import re

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 创建输出目录
output_dir = 'downloaded_pages_corrected'
os.makedirs(output_dir, exist_ok=True)

# 生成URL列表（从17283878递减到17283833）
start_num = 17283878
end_num = 17283833

urls = []
for num in range(start_num, end_num - 1, -1):
    url = f'http://www.xn--3mq943byne27j.com/vip_doc/{num}.html'
    urls.append((num, url))

successful_downloads = []
failed_downloads = []

print(f'开始重新下载 {len(urls)} 个网页...')
print(f'范围: {start_num} 到 {end_num} (递减)')
print()

for idx, (num, url) in enumerate(urls, 1):
    print(f'[{idx}/{len(urls)}] 正在重新下载: {url}')
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 检测响应的实际编码
            if response.encoding and response.encoding.lower() in ['gbk', 'gb2312', 'cp936']:
                content = response.content.decode(response.encoding)
            elif response.apparent_encoding and response.apparent_encoding.lower() in ['gbk', 'gb2312', 'cp936']:
                content = response.content.decode(response.apparent_encoding)
            else:
                # 如果不是中文编码，使用默认方式
                response.encoding = 'utf-8'
                content = response.text
            
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
            filename = os.path.join(output_dir, f'{num}_corrected.html')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n')
                f.write(f'    <title>{soup.title.string if soup.title else f"Page_{num}"}</title>\n')
                f.write(f'</head>\n<body>\n')
                f.write(f'<h1>{soup.title.string if soup.title else f"Page_{num}"}</h1>\n')
                f.write(f'<p>URL: {url}</p>\n')
                f.write(f'<p>字符数: {char_count}</p>\n')
                f.write(f'<p>汉字数: {chinese_char_count}</p>\n')
                f.write('<hr>\n')
                f.write(clean_text)
                f.write('\n</body>\n</html>')
            
            successful_downloads.append((num, url, char_count, chinese_char_count))
            print(f'  ✓ 成功下载并保存到 {filename} (字符数: {char_count}, 汉字数: {chinese_char_count})')
        else:
            failed_downloads.append((num, url, response.status_code))
            print(f'  ✗ 下载失败，状态码: {response.status_code}')
            
    except Exception as e:
        failed_downloads.append((num, url, str(e)))
        print(f'  ✗ 下载失败，错误: {e}')

# 生成下载报告
report_filename = os.path.join(output_dir, 'download_report_corrected.txt')
with open(report_filename, 'w', encoding='utf-8') as f:
    f.write('网页重新下载报告\n')
    f.write('='*50 + '\n\n')
    
    f.write(f'下载范围: {start_num} 到 {end_num} (递减)\n')
    f.write(f'目标网页数: {len(urls)}\n')
    f.write(f'成功下载数: {len(successful_downloads)}\n')
    f.write(f'失败下载数: {len(failed_downloads)}\n\n')
    
    if successful_downloads:
        f.write('成功下载的网页:\n')
        f.write('-' * 30 + '\n')
        for num, url, char_count, chinese_count in successful_downloads:
            f.write(f'{num}_corrected.html - {url} (字符数: {char_count}, 汉字数: {chinese_count})\n')
        f.write('\n')
    
    if failed_downloads:
        f.write('下载失败的网页:\n')
        f.write('-' * 30 + '\n')
        for item in failed_downloads:
            if len(item) == 3:
                num, url, error = item
                f.write(f'{num}_corrected.html - {url} (错误: {error})\n')
        f.write('\n')

print(f'\n重新下载完成!')
print(f'成功: {len(successful_downloads)} 个网页')
print(f'失败: {len(failed_downloads)} 个网页')
print(f'报告已保存到: {report_filename}')

# 验证几个文件的内容
print(f'\n验证下载的文件内容...')
sample_files = [f for f in os.listdir(output_dir) if f.endswith('_corrected.html')][:3]
for sample_file in sample_files:
    filepath = os.path.join(output_dir, sample_file)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read(300)  # 读取前300个字符
        print(f'\n{sample_file} 前300个字符预览:')
        print(content[:content.find('<hr>') if '<hr>' in content else 300])
