import requests
from bs4 import BeautifulSoup
import os
import chardet
import re

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 创建输出目录
output_dir = 'downloaded_pages_corrected'
os.makedirs(output_dir, exist_ok=True)

# 要下载的URL列表
urls = [
    'https://m.thepaper.cn/baijiahao_4396501',
    'https://xy.zjnu.edu.cn/jjh/zjnu_jjh/cnt/?id=660cc72e-f662-4228-b6f5-b13a8e49ba2b',
    'https://m.21jingji.com/article/20140924/3823338d90ae2688710bbbd76dd193e2.html',
    'http://e.mzyfz.org.cn/mag/paper_25016_13454.html'
]

successful_downloads = []
failed_downloads = []

print(f'开始下载 {len(urls)} 个新网页...')
print()

for idx, url in enumerate(urls, 1):
    print(f'[{idx}/{len(urls)}] 正在下载: {url}')
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # 检测响应的实际编码
            try:
                # 使用chardet检测编码
                detected = chardet.detect(response.content)
                encoding = detected['encoding']
                
                if encoding and encoding.lower() in ['gbk', 'gb2312', 'cp936']:
                    content = response.content.decode(encoding, errors='replace')
                else:
                    # 尝试从响应头获取编码
                    response.encoding = response.apparent_encoding or response.encoding or 'utf-8'
                    content = response.text
            except:
                # 如果检测失败，尝试常见的编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'cp936']
                content = None
                for enc in encodings:
                    try:
                        content = response.content.decode(enc, errors='replace')
                        break
                    except:
                        continue
                
                if content is None:
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
            
            # 根据URL生成文件名
            # 简化URL以创建合适的文件名
            safe_filename = re.sub(r'[^\w\s-]', '_', url.split('//')[1].replace('/', '_'))[:100] + '.html'
            filename = os.path.join(output_dir, safe_filename)
            
            # 保存页面内容，使用正确的编码
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n')
                f.write(f'    <title>{soup.title.string if soup.title else "Downloaded Page"}</title>\n')
                f.write(f'</head>\n<body>\n')
                f.write(f'<h1>{soup.title.string if soup.title else "Downloaded Page"}</h1>\n')
                f.write(f'<p>URL: {url}</p>\n')
                f.write(f'<p>字符数: {char_count}</p>\n')
                f.write(f'<p>汉字数: {chinese_char_count}</p>\n')
                f.write('<hr>\n')
                f.write(clean_text)
                f.write('\n</body>\n</html>')
            
            successful_downloads.append((url, char_count, chinese_char_count, filename))
            print(f'  ✓ 成功下载并保存到 {filename} (字符数: {char_count}, 汉字数: {chinese_char_count})')
        else:
            failed_downloads.append((url, response.status_code))
            print(f'  ✗ 下载失败，状态码: {response.status_code}')
            
    except requests.exceptions.Timeout:
        failed_downloads.append((url, "Timeout"))
        print(f'  ✗ 下载超时')
    except Exception as e:
        failed_downloads.append((url, str(e)))
        print(f'  ✗ 下载失败，错误: {e}')

# 生成下载报告
report_filename = os.path.join(output_dir, 'additional_download_report.txt')
with open(report_filename, 'w', encoding='utf-8') as f:
    f.write('新增网页下载报告\n')
    f.write('='*50 + '\n\n')
    
    f.write(f'目标网页数: {len(urls)}\n')
    f.write(f'成功下载数: {len(successful_downloads)}\n')
    f.write(f'失败下载数: {len(failed_downloads)}\n\n')
    
    if successful_downloads:
        f.write('成功下载的网页:\n')
        f.write('-' * 30 + '\n')
        for url, char_count, chinese_count, filename in successful_downloads:
            f.write(f'{filename} - {url} (字符数: {char_count}, 汉字数: {chinese_count})\n')
        f.write('\n')
    
    if failed_downloads:
        f.write('下载失败的网页:\n')
        f.write('-' * 30 + '\n')
        for item in failed_downloads:
            if len(item) == 2:
                url, error = item
                f.write(f'{url} (错误: {error})\n')
        f.write('\n')

print(f'\n新增网页下载完成!')
print(f'成功: {len(successful_downloads)} 个网页')
print(f'失败: {len(failed_downloads)} 个网页')
print(f'报告已保存到: {report_filename}')

# 验证下载的文件内容
print(f'\n验证下载的文件内容...')
for url, _, _, filename in successful_downloads:
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read(300)  # 读取前300个字符
        print(f'\n{filename} 前300个字符预览:')
        print(content[:content.find('<hr>') if '<hr>' in content else 300])
