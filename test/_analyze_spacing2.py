import re, os, glob
from pathlib import Path
from collections import defaultdict

num_re = re.compile(r'y\s*=\s*["\']([\d.]+)["\']')
x_re = re.compile(r'x\s*=\s*["\']([\d.]+)["\']')
fs_re = re.compile(r'font-size\s*=\s*["\']([\d.]+)["\']')

for svg_path in sorted(glob.glob('output/0415_2127_GGG/result/slide_*/slide_*.svg')):
    with open(svg_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    texts = []
    for m in re.finditer(r'<text\b([^>]*)>', code, re.IGNORECASE):
        attrs = m.group(1)
        y_m = num_re.search(attrs)
        x_m = x_re.search(attrs)
        fs_m = fs_re.search(attrs)
        if y_m and x_m:
            y = float(y_m.group(1))
            x = float(x_m.group(1))
            fs = float(fs_m.group(1)) if fs_m else 16.0
            texts.append((x, y, fs))
    
    # 按 x 分组（允许 5px 误差）
    groups = defaultdict(list)
    for x, y, fs in texts:
        key = round(x / 10) * 10
        groups[key].append((y, fs))
    
    violations = 0
    for key, items in groups.items():
        items.sort()
        for i in range(len(items)-1):
            dy = items[i+1][0] - items[i][0]
            if 0 < dy < items[i][1] * 0.9:
                violations += 1
    
    name = Path(svg_path).parent.name + '/' + Path(svg_path).name
    status = 'OK' if violations == 0 else f'BAD({violations})'
    print(f'{name}: {status}')
