"""
PPT 风格提取脚本
从 PPTX 文件解压并提取所有风格信息，保存为 JSON
"""

import json
import os
import zipfile
import shutil
from pathlib import Path
from lxml import etree
from typing import Dict, Any, List
import re

class PPTStyleExtractor:
    """从 PPTX 文件提取风格信息"""
    
    def __init__(self, pptx_path: str):
        """
        初始化提取器
        
        Args:
            pptx_path: PPTX 文件路径
        """
        self.pptx_path = pptx_path
        self.temp_dir = "temp_extracted_pptx"
        self.ppt_dir = os.path.join(self.temp_dir, "ppt")
        
        # 命名空间
        self.ns = {
            'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
            'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main',
        }
        
        # 存储提取的数据
        self.styles_data = {
            'metadata': {},
            'global': {
                'slideSize': {},
                'themeColors': {},
                'themeFonts': {}
            },
            'slides': []
        }
        
        # 解压 PPTX
        self._extract_pptx()
        
        print("✅ PPTX 已解压到临时目录")
    
    # ==================== 解压和初始化 ====================
    
    def _extract_pptx(self):
        """解压 PPTX 文件"""
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        with zipfile.ZipFile(self.pptx_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
    
    # ==================== 提取全局风格 ====================
    
    def extract_global_styles(self):
        """提取全局风格信息"""
        
        print("📊 开始提取全局风格...")
        
        # 1. 提取幻灯片尺寸
        self._extract_slide_size()
        
        # 2. 提取主题颜色
        self._extract_theme_colors()
        
        # 3. 提取主题字体
        self._extract_theme_fonts()
        
        # 4. 提取元数据
        self._extract_metadata()
        
        print("✅ 全局风格提取完成")
    
    def _extract_slide_size(self):
        """提取幻灯片尺寸"""
        
        prs_path = os.path.join(self.ppt_dir, 'presentation.xml')
        
        try:
            tree = etree.parse(prs_path)
            root = tree.getroot()
            
            # 查找幻灯片尺寸
            sld_sz = root.find('.//p:sldSz', self.ns)
            
            if sld_sz is not None:
                width = int(sld_sz.get('cx', 9144000))
                height = int(sld_sz.get('cy', 6858000))
                
                self.styles_data['global']['slideSize'] = {
                    'width': width,
                    'height': height
                }
                
                print(f"  📐 幻灯片尺寸: {width} x {height}")
        
        except Exception as e:
            print(f"  ⚠️ 提取幻灯片尺寸失败: {e}")
            # 设置默认值
            self.styles_data['global']['slideSize'] = {
                'width': 9144000,
                'height': 6858000
            }
    
    def _extract_theme_colors(self):
        """提取主题颜色"""
        
        theme_path = os.path.join(self.ppt_dir, 'theme', 'theme1.xml')
        
        try:
            tree = etree.parse(theme_path)
            root = tree.getroot()
            
            # 查找颜色方案
            clr_scheme = root.find('.//a:clrScheme', self.ns)
            
            if clr_scheme is not None:
                # 标准的 12 种颜色
                color_names = [
                    'dk1', 'lt1', 'dk2', 'lt2',
                    'accent1', 'accent2', 'accent3', 'accent4', 'accent5', 'accent6',
                    'hlink', 'folHlink'
                ]
                
                for color_name in color_names:
                    # 查找颜色定义
                    color_elem = clr_scheme.find(f'.//a:{color_name}', self.ns)
                    
                    if color_elem is not None:
                        # 查找 sRGB 颜色值
                        srgb = color_elem.find('.//a:srgbClr', self.ns)
                        
                        if srgb is not None:
                            color_val = srgb.get('val')
                            self.styles_data['global']['themeColors'][color_name] = f"#{color_val}"
                            print(f"  🎨 {color_name}: #{color_val}")
        
        except Exception as e:
            print(f"  ⚠️ 提取主题颜色失败: {e}")
    
    def _extract_theme_fonts(self):
        """提取主题字体"""
        
        theme_path = os.path.join(self.ppt_dir, 'theme', 'theme1.xml')
        
        try:
            tree = etree.parse(theme_path)
            root = tree.getroot()
            
            # 查找字体方案
            font_scheme = root.find('.//a:fontScheme', self.ns)
            
            if font_scheme is not None:
                # 标题字体 (majorFont)
                major_font = font_scheme.find('.//a:majorFont', self.ns)
                if major_font is not None:
                    major_fonts = self._extract_font_typefaces(major_font)
                    self.styles_data['global']['themeFonts']['majorFont'] = major_fonts
                    print(f"  🔤 majorFont: {major_fonts}")
                
                # 正文字体 (minorFont)
                minor_font = font_scheme.find('.//a:minorFont', self.ns)
                if minor_font is not None:
                    minor_fonts = self._extract_font_typefaces(minor_font)
                    self.styles_data['global']['themeFonts']['minorFont'] = minor_fonts
                    print(f"  🔤 minorFont: {minor_fonts}")
        
        except Exception as e:
            print(f"  ⚠️ 提取主题字体失败: {e}")
    
    def _extract_font_typefaces(self, font_elem) -> Dict[str, str]:
        """从字体元素提取字体族"""
        
        typefaces = {}
        
        font_types = [
            ('latin', 'Latin'),
            ('ea', 'East Asian'),
            ('cs', 'Complex Script')
        ]
        
        for tag, label in font_types:
            font = font_elem.find(f'.//a:{tag}', self.ns)
            if font is not None:
                typeface = font.get('typeface', '')
                if typeface:
                    typefaces[tag] = typeface
        
        return typefaces
    
    def _extract_metadata(self):
        """提取文档元数据"""
        
        prs_path = os.path.join(self.ppt_dir, 'presentation.xml')
        
        try:
            tree = etree.parse(prs_path)
            root = tree.getroot()
            
            # 统计幻灯片数量
            sld_id_lst = root.find('.//p:sldIdLst', self.ns)
            slide_count = 0
            if sld_id_lst is not None:
                slide_count = len(sld_id_lst.findall('.//p:sldId', self.ns))
            
            self.styles_data['metadata'] = {
                'pptxFile': Path(self.pptx_path).name,
                'slideCount': slide_count,
                'extractionTool': 'PPT Style Extractor v1.0'
            }
            
            print(f"  📄 总幻灯片数: {slide_count}")
        
        except Exception as e:
            print(f"  ⚠️ 提取元数据失败: {e}")
    
    # ==================== 提取幻灯片级别风格 ====================
    
    def extract_slides_styles(self):
        """提取所有幻灯片的风格"""
        
        print("🎬 开始提取幻灯片风格...")
        
        slides_dir = os.path.join(self.ppt_dir, 'slides')
        
        # 获取所有幻灯片文件
        slide_files = sorted(
            [f for f in os.listdir(slides_dir) 
             if f.startswith('slide') and f.endswith('.xml') and '_rels' not in f],
            key=lambda x: int(re.search(r'\d+', x).group())
        )
        
        for slide_file in slide_files:
            slide_num = int(re.search(r'\d+', slide_file).group())
            slide_path = os.path.join(slides_dir, slide_file)
            
            print(f"\n  📄 处理 {slide_file}...")
            
            slide_data = self._extract_slide_style(slide_path, slide_num)
            self.styles_data['slides'].append(slide_data)
        
        print(f"\n✅ 幻灯片风格提取完成 (共 {len(self.styles_data['slides'])} 页)")
    
    def _extract_slide_style(self, slide_path: str, slide_num: int) -> Dict[str, Any]:
        """提取单个幻灯片的风格"""
        
        slide_data = {
            'slideNumber': slide_num,
            'background': {},
            'shapes': []
        }
        
        try:
            tree = etree.parse(slide_path)
            root = tree.getroot()
            
            # 1. 提取背景
            bg = root.find('.//p:bg', self.ns)
            if bg is not None:
                slide_data['background'] = self._extract_background(bg)
            
            # 2. 提取形状
            sp_tree = root.find('.//p:spTree', self.ns)
            if sp_tree is not None:
                shapes = sp_tree.findall('.//p:sp', self.ns)
                
                for idx, shape in enumerate(shapes):
                    shape_info = self._extract_shape(shape, idx)
                    if shape_info:
                        slide_data['shapes'].append(shape_info)
        
        except Exception as e:
            print(f"    ⚠️ 提取幻灯片失败: {e}")
        
        return slide_data
    
    def _extract_background(self, bg_elem) -> Dict[str, Any]:
        """提取背景风格"""
        
        bg_style = {}
        
        bg_pr = bg_elem.find('.//p:bgPr', self.ns)
        if bg_pr is None:
            return bg_style
        
        # 1. 纯色背景
        solid_fill = bg_pr.find('.//a:solidFill', self.ns)
        if solid_fill is not None:
            srgb = solid_fill.find('.//a:srgbClr', self.ns)
            if srgb is not None:
                color = srgb.get('val')
                alpha = srgb.find('.//a:alpha', self.ns)
                
                bg_style['type'] = 'solid'
                bg_style['color'] = f"#{color}"
                
                if alpha is not None:
                    bg_style['alpha'] = int(alpha.get('val', 100000))
                
                return bg_style
        
        # 2. 渐变背景
        grad_fill = bg_pr.find('.//a:gradFill', self.ns)
        if grad_fill is not None:
            bg_style['type'] = 'gradient'
            
            # 渐变停止点
            gs_lst = grad_fill.find('.//a:gsLst', self.ns)
            if gs_lst is not None:
                stops = []
                for gs in gs_lst.findall('.//a:gs', self.ns):
                    pos = int(gs.get('pos', 0))
                    srgb = gs.find('.//a:srgbClr', self.ns)
                    
                    if srgb is not None:
                        color = srgb.get('val')
                        stops.append({
                            'position': pos / 1000,
                            'color': f"#{color}"
                        })
                
                bg_style['stops'] = stops
            
            # 渐变方向
            lin = grad_fill.find('.//a:lin', self.ns)
            if lin is not None:
                angle = int(lin.get('ang', 0))
                bg_style['angle'] = angle / 60000
            
            return bg_style
        
        return bg_style
    
    def _extract_shape(self, shape_elem, shape_idx: int) -> Dict[str, Any]:
        """提取形状风格"""
        
        shape_info = {
            'id': shape_idx,
            'geometry': {},
            'fill': {},
            'line': {},
            'shadow': {},
            'text': {}
        }
        
        try:
            # 非视觉属性
            nv_sp_pr = shape_elem.find('.//p:nvSpPr', self.ns)
            if nv_sp_pr is not None:
                c_nv_pr = nv_sp_pr.find('.//p:cNvPr', self.ns)
                if c_nv_pr is not None:
                    shape_info['name'] = c_nv_pr.get('name', f'Shape {shape_idx}')
            
            # 形状属性
            sp_pr = shape_elem.find('.//p:spPr', self.ns)
            if sp_pr is not None:
                # 几何信息
                geometry = self._extract_geometry(sp_pr)
                shape_info['geometry'].update(geometry)
                
                # 填充
                fill = self._extract_fill(sp_pr)
                shape_info['fill'].update(fill)
                
                # 边框
                line = self._extract_line(sp_pr)
                shape_info['line'].update(line)
                
                # 阴影
                shadow = self._extract_shadow(sp_pr)
                shape_info['shadow'].update(shadow)
            
            # 文本内容
            tx_body = shape_elem.find('.//p:txBody', self.ns)
            if tx_body is not None:
                text = self._extract_text(tx_body)
                shape_info['text'].update(text)
        
        except Exception as e:
            print(f"    ⚠️ 提取形状失败: {e}")
        
        return shape_info
    
    def _extract_geometry(self, sp_pr_elem) -> Dict[str, Any]:
        """提取形状几何"""
        
        geometry = {}
        
        # 位置和大小
        xfrm = sp_pr_elem.find('.//a:xfrm', self.ns)
        if xfrm is not None:
            off = xfrm.find('.//a:off', self.ns)
            ext = xfrm.find('.//a:ext', self.ns)
            
            if off is not None:
                geometry['position'] = {
                    'x': int(off.get('x', 0)),
                    'y': int(off.get('y', 0))
                }
            
            if ext is not None:
                geometry['size'] = {
                    'width': int(ext.get('cx', 0)),
                    'height': int(ext.get('cy', 0))
                }
            
            # 旋转
            rot = xfrm.get('rot')
            if rot:
                geometry['rotation'] = int(rot) / 60000
        
        # 形状类型
        prst_geom = sp_pr_elem.find('.//a:prstGeom', self.ns)
        if prst_geom is not None:
            geometry['type'] = prst_geom.get('prst', 'unknown')
        
        return geometry
    
    def _extract_fill(self, sp_pr_elem) -> Dict[str, Any]:
        """提取填充"""
        
        fill = {}
        
        # 1. 纯色填充
        solid_fill = sp_pr_elem.find('.//a:solidFill', self.ns)
        if solid_fill is not None:
            fill['type'] = 'solid'
            
            # sRGB 颜色
            srgb = solid_fill.find('.//a:srgbClr', self.ns)
            if srgb is not None:
                fill['color'] = f"#{srgb.get('val', '000000')}"
                
                # 透明度
                alpha = srgb.find('.//a:alpha', self.ns)
                if alpha is not None:
                    fill['alpha'] = int(alpha.get('val', 100000))
            
            # 主题颜色
            scheme_clr = solid_fill.find('.//a:schemeClr', self.ns)
            if scheme_clr is not None:
                fill['schemeColor'] = scheme_clr.get('val', '')
            
            return fill
        
        # 2. 渐变填充
        grad_fill = sp_pr_elem.find('.//a:gradFill', self.ns)
        if grad_fill is not None:
            fill['type'] = 'gradient'
            
            # 渐变类型
            fill['gradientType'] = grad_fill.get('flip', 'none')
            
            # 渐变停止点
            gs_lst = grad_fill.find('.//a:gsLst', self.ns)
            if gs_lst is not None:
                stops = []
                for gs in gs_lst.findall('.//a:gs', self.ns):
                    pos = int(gs.get('pos', 0))
                    srgb = gs.find('.//a:srgbClr', self.ns)
                    
                    if srgb is not None:
                        color = srgb.get('val')
                        alpha_elem = srgb.find('.//a:alpha', self.ns)
                        
                        stop = {
                            'position': pos / 1000,
                            'color': f"#{color}"
                        }
                        
                        if alpha_elem is not None:
                            stop['alpha'] = int(alpha_elem.get('val', 100000))
                        
                        stops.append(stop)
                
                fill['stops'] = stops
            
            # 线性渐变
            lin = grad_fill.find('.//a:lin', self.ns)
            if lin is not None:
                angle = int(lin.get('ang', 0))
                fill['angle'] = angle / 60000
            
            return fill
        
        # 3. 无填充
        no_fill = sp_pr_elem.find('.//a:noFill', self.ns)
        if no_fill is not None:
            fill['type'] = 'none'
            return fill
        
        return fill
    
    def _extract_line(self, sp_pr_elem) -> Dict[str, Any]:
        """提取边框"""
        
        line = {}
        
        ln = sp_pr_elem.find('.//a:ln', self.ns)
        if ln is None:
            return line
        
        # 线宽
        width = ln.get('w')
        if width:
            line['width'] = int(width)
        
        # 线颜色
        solid_fill = ln.find('.//a:solidFill', self.ns)
        if solid_fill is not None:
            srgb = solid_fill.find('.//a:srgbClr', self.ns)
            if srgb is not None:
                line['color'] = f"#{srgb.get('val', '000000')}"
                
                alpha = srgb.find('.//a:alpha', self.ns)
                if alpha is not None:
                    line['alpha'] = int(alpha.get('val', 100000))
        
        # 线型
        prst_dash = ln.find('.//a:prstDash', self.ns)
        if prst_dash is not None:
            line['dashType'] = prst_dash.get('val', 'solid')
        else:
            line['dashType'] = 'solid'
        
        # 线端点
        prstln_end = ln.find('.//a:prstLnEnd', self.ns)
        if prstln_end is not None:
            line['lineEnd'] = prstln_end.get('val', 'flat')
        
        # 线连接点
        ln_join = ln.find('.//a:miter', self.ns)
        if ln_join is not None:
            line['lineJoin'] = 'miter'
        else:
            ln_join = ln.find('.//a:round', self.ns)
            if ln_join is not None:
                line['lineJoin'] = 'round'
        
        return line
    
    def _extract_shadow(self, sp_pr_elem) -> Dict[str, Any]:
        """提取阴影"""
        
        shadow = {}
        
        # 外阴影
        outer_shdw = sp_pr_elem.find('.//a:outerShdw', self.ns)
        if outer_shdw is not None:
            shadow['type'] = 'outer'
            shadow['blurRad'] = int(outer_shdw.get('blurRad', 0))
            shadow['distance'] = int(outer_shdw.get('dist', 0))
            shadow['direction'] = int(outer_shdw.get('dir', 0))
            shadow['alignment'] = outer_shdw.get('algn', 'tl')
            
            srgb = outer_shdw.find('.//a:srgbClr', self.ns)
            if srgb is not None:
                shadow['color'] = f"#{srgb.get('val', '000000')}"
                
                alpha = srgb.find('.//a:alpha', self.ns)
                if alpha is not None:
                    shadow['alpha'] = int(alpha.get('val', 100000))
            
            return shadow
        
        # 内阴影
        inner_shdw = sp_pr_elem.find('.//a:innerShdw', self.ns)
        if inner_shdw is not None:
            shadow['type'] = 'inner'
            shadow['blurRad'] = int(inner_shdw.get('blurRad', 0))
            shadow['distance'] = int(inner_shdw.get('dist', 0))
            shadow['direction'] = int(inner_shdw.get('dir', 0))
            
            srgb = inner_shdw.find('.//a:srgbClr', self.ns)
            if srgb is not None:
                shadow['color'] = f"#{srgb.get('val', '000000')}"
            
            return shadow
        
        return shadow
    
    def _extract_text(self, tx_body_elem) -> Dict[str, Any]:
        """提取文本风格"""
        
        text_data = {
            'paragraphs': []
        }
        
        # 文本框属性
        body_pr = tx_body_elem.find('.//a:bodyPr', self.ns)
        if body_pr is not None:
            text_data['textBox'] = {
                'anchor': body_pr.get('anchor', 'ctr'),
                'vertical': body_pr.get('vert', 'horz'),
                'insetLeft': int(body_pr.get('lIns', 91440)),
                'insetRight': int(body_pr.get('rIns', 91440)),
                'insetTop': int(body_pr.get('tIns', 45720)),
                'insetBottom': int(body_pr.get('bIns', 45720))
            }
        
        # 段落
        paragraphs = tx_body_elem.findall('.//a:p', self.ns)
        
        for para in paragraphs:
            para_data = self._extract_paragraph(para)
            text_data['paragraphs'].append(para_data)
        
        return text_data
    
    def _extract_paragraph(self, para_elem) -> Dict[str, Any]:
        """提取段落风格"""
        
        para_data = {
            'alignment': 'l',
            'runs': []
        }
        
        # 段落属性
        p_pr = para_elem.find('.//a:pPr', self.ns)
        if p_pr is not None:
            # 对齐
            alignment = p_pr.get('algn')
            align_map = {'ctr': 'center', 'l': 'left', 'r': 'right', 'just': 'justify'}
            para_data['alignment'] = align_map.get(alignment, 'left')
            
            # 边距
            para_data['marginLeft'] = int(p_pr.get('marL', 0))
            para_data['marginRight'] = int(p_pr.get('marR', 0))
            para_data['indent'] = int(p_pr.get('indent', 0))
            
            # 行距
            ln_spc = p_pr.find('.//a:lnSpc', self.ns)
            if ln_spc is not None:
                spc_pct = ln_spc.find('.//a:spcPct', self.ns)
                if spc_pct is not None:
                    para_data['lineSpacing'] = {
                        'type': 'percentage',
                        'value': int(spc_pct.get('val', 120000)) / 1000
                    }
                
                spc_pts = ln_spc.find('.//a:spcPts', self.ns)
                if spc_pts is not None:
                    para_data['lineSpacing'] = {
                        'type': 'points',
                        'value': int(spc_pts.get('val', 0))
                    }
        
        # 文本内容
        runs = para_elem.findall('.//a:r', self.ns)
        
        for run in runs:
            run_data = self._extract_run(run)
            para_data['runs'].append(run_data)
        
        return para_data
    
    def _extract_run(self, run_elem) -> Dict[str, Any]:
        """提取文本段"""
        
        run_data = {
            'text': '',
            'font': {}
        }
        
        # 文本内容
        t = run_elem.find('.//a:t', self.ns)
        if t is not None and t.text:
            run_data['text'] = t.text
        
        # 文本属性
        r_pr = run_elem.find('.//a:rPr', self.ns)
        if r_pr is not None:
            font_info = {}
            
            # 字体大小
            sz = r_pr.get('sz')
            if sz:
                font_info['size'] = int(sz) / 100
            
            # 加粗和斜体
            font_info['bold'] = r_pr.get('b') == '1'
            font_info['italic'] = r_pr.get('i') == '1'
            
            # 下划线
            underline = r_pr.get('u')
            font_info['underline'] = underline if underline else 'none'
            
            # 删除线
            strike = r_pr.get('strike')
            font_info['strike'] = strike if strike else 'none'
            
            # 字体族
            latin = r_pr.find('.//a:latin', self.ns)
            if latin is not None:
                font_info['latin'] = latin.get('typeface', 'Calibri')
            
            ea = r_pr.find('.//a:ea', self.ns)
            if ea is not None:
                font_info['ea'] = ea.get('typeface', '微软雅黑')
            
            cs = r_pr.find('.//a:cs', self.ns)
            if cs is not None:
                font_info['cs'] = cs.get('typeface', 'Arial')
            
            # 颜色
            solid_fill = r_pr.find('.//a:solidFill', self.ns)
            if solid_fill is not None:
                srgb = solid_fill.find('.//a:srgbClr', self.ns)
                if srgb is not None:
                    font_info['color'] = f"#{srgb.get('val', '000000')}"
            
            # 语言
            lang = r_pr.get('lang')
            if lang:
                font_info['lang'] = lang
            
            run_data['font'] = font_info
        
        return run_data
    
    # ==================== 保存为 JSON ====================
    
    def save_json(self, output_path: str = 'styles.json'):
        """保存提取的风格为 JSON 文件"""
        
        # 确保有全局风格
        if not self.styles_data['global']['slideSize']:
            self._extract_slide_size()
        
        if not self.styles_data['global']['themeColors']:
            self._extract_theme_colors()
        
        if not self.styles_data['global']['themeFonts']:
            self._extract_theme_fonts()
        
        # 保存为 JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.styles_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 风格已保存到: {output_path}")
        
        return output_path
    
    # ==================== 清理临时文件 ====================
    
    def cleanup(self):
        """清理临时目录"""
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print("✅ 临时文件已清理")


# ==================== 主程序 ====================

def main():
    """主函数"""
    
    import sys
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python extract_ppt_style.py <input.pptx> [output.json]")
        print("\n示例:")
        print("  python extract_ppt_style.py template.pptx styles.json")
        sys.exit(1)
    
    input_pptx = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else 'styles.json'
    
    # 检查输入文件
    if not os.path.exists(input_pptx):
        print(f"❌ 文件不存在: {input_pptx}")
        sys.exit(1)
    
    print(f"📂 输入文件: {input_pptx}")
    print(f"💾 输出文件: {output_json}")
    print("=" * 60)
    
    # 创建提取器
    extractor = PPTStyleExtractor(input_pptx)
    
    try:
        # 提取全局风格
        extractor.extract_global_styles()
        
        # 提取幻灯片风格
        extractor.extract_slides_styles()
        
        # 保存为 JSON
        extractor.save_json(output_json)
        
        print("\n" + "=" * 60)
        print("✅ 风格提取完成！")
    
    except Exception as e:
        print(f"\n❌ 提取失败: {e}")
        sys.exit(1)
    
    finally:
        # 清理临时文件
        extractor.cleanup()


if __name__ == '__main__':
    main()
