import random

def generate_large_html(target_length):
    html_start = '<!DOCTYPE html><html lang=en><head><meta charset=UTF-8><meta name=viewport content=width=device-width, initial-scale=1.0><title>Large HTML Document</title></head><body>'
    html_end = '</body></html>'
    lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

    content = html_start
    current_length = len(content)

    while current_length < target_length:
        paragraph = f'<p>{lorem_ipsum}</p>'
        content += paragraph
        current_length = len(content)

        if random.random() < 0.1:
            content += '<hr>'
        if random.random() < 0.05:
            content += '<h2>Section Header</h2>'

    content += html_end
    return content

# 生成HTML
target_length = 20000000
large_html = generate_large_html(target_length)

# 将HTML保存到文件，不包含换行符
with open('large_document.html', 'w', encoding='utf-8') as f:
    f.write(large_html.replace('\n', ''))

print(f'Generated HTML with {len(large_html)} characters.')
