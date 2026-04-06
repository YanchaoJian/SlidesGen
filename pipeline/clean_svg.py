import re

with open('pptx_slide_mockup.svg', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove <marker> definition (banned in PPT)
content = re.sub(r'<marker[^>]*>.*?</marker>\s*', '', content, flags=re.DOTALL)

# 2. Remove <mask> definition (banned in PPT)
content = re.sub(r'<mask[^>]*>.*?</mask>', '', content, flags=re.DOTALL)

# 3. Clean up empty <defs>
content = re.sub(r'<defs>\s*</defs>', '<defs/>', content)

# 4. Remove mask attributes from elements
content = re.sub(r'\s*mask="url\([^)]*\)"', '', content)

# 5. Remove all inline style attributes (they duplicate explicit SVG attributes)
content = re.sub(r'\s*style="[^"]*"', '', content)

# 6. Fix rgba fill on shadow rect
content = content.replace('fill="#00000018"', 'fill="black" fill-opacity="0.094"')

with open('svg_output/01_slide.svg', 'w', encoding='utf-8') as f:
    f.write(content)

print('SVG cleaned and saved to svg_output/01_slide.svg')
