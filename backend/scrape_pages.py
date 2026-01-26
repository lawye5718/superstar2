import requests
from bs4 import BeautifulSoup
import os
import re

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 定义6个URL
urls = [
    'http://www.xn--3mq943byne27j.com/vip_doc/23078845_0_0_1.html',
    'http://www.xn--3mq943byne27j.com/vip_doc/23078845_0_0_2.html',
    'http://www.xn--3mq943byne27j.com/vip_doc/23078845_0_0_3.html',
    'http://www.xn--3mq943byne27j.com/vip_doc/23078845_0_0_4.html',
    'http://www.xn--3mq943byne27j.com/vip_doc/23078845_0_0_5.html',
    'http://www.xn--3mq943byne27j.com/vip_doc/23078845_0_0_6.html'
]

# 创建输出目录
output_dir = 'filtered_pages'
os.makedirs(output_dir, exist_ok=True)

valid_pages = []
page_info = []

for i, url in enumerate(urls, 1):
    print(f'正在检查第 {i} 个网页: {url}')
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
        chinese_char_count = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
        
        print(f'  字符数: {char_count}, 汉字数: {chinese_char_count}')
        
        page_info.append({
            'num': i,
            'url': url,
            'char_count': char_count,
            'chinese_char_count': chinese_char_count,
            'content': clean_text,
            'title': soup.title.string if soup.title else f'Page_{i}'
        })
        
        # 如果字符数大于等于2000，则加入有效页面列表
        if char_count >= 2000:
            valid_pages.append({
                'num': i,
                'url': url,
                'char_count': char_count,
                'chinese_char_count': chinese_char_count,
                'content': clean_text,
                'title': soup.title.string if soup.title else f'Page_{i}'
            })
        else:
            print(f'  字符数少于2000，跳过')
        
    except Exception as e:
        print(f'  处理第 {i} 个网页时出错: {e}')

# 保存有效页面
print(f'\n发现 {len(valid_pages)} 个有效页面（字符数>=2000）')
for idx, page in enumerate(valid_pages, 1):
    # 创建子目录用于存放每个有效页面
    page_dir = os.path.join(output_dir, str(idx))
    os.makedirs(page_dir, exist_ok=True)
    
    # 保存完整页面内容
    filename = os.path.join(page_dir, f'{idx}.html')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'<!-- 网页标题: {page["title"]} -->\n')
        f.write(f'<!-- 网页URL: {page["url"]} -->\n')
        f.write(f'<!-- 字符数: {page["char_count"]} -->\n')
        f.write(f'<!-- 汉字数: {page["chinese_char_count"]} -->\n')
        f.write(f'<html><head><title>{page["title"]}</title></head><body>\n')
        f.write(f'<h1>{page["title"]}</h1>\n')
        f.write(f'<p>URL: {page["url"]}</p>\n')
        f.write(f'<p>字符数: {page["char_count"]}</p>\n')
        f.write(f'<p>汉字数: {page["chinese_char_count"]}</p>\n')
        f.write(f'<hr>\n')
        f.write(page['content'])
        f.write(f'\n</body></html>')
    
    print(f'第 {idx} 个有效页面已保存到 {filename}')

# 保存过滤结果摘要
summary_filename = os.path.join(output_dir, 'filter_summary.txt')
with open(summary_filename, 'w', encoding='utf-8') as f:
    f.write('网页过滤摘要\n')
    f.write('='*50 + '\n\n')
    
    f.write('所有页面统计:\n')
    for info in page_info:
        status = '保留' if info['char_count'] >= 2000 else '过滤'
        f.write(f'{info["num"]}. {info["url"]}\n')
        f.write(f'   字符数: {info["char_count"]}, 汉字数: {info["chinese_char_count"]}, 状态: {status}\n\n')
    
    f.write(f'\n有效页面 ({len(valid_pages)} 个):\n')
    for idx, page in enumerate(valid_pages, 1):
        f.write(f'{idx}. {page["url"]} (字符数: {page["char_count"]})\n')

print(f'\n过滤摘要已保存到 {summary_filename}')
print('\n处理完成!')
