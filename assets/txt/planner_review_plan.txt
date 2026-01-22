import logging

logger = logging.getLogger(__name__)


def print_plan_summary(slides_plan):
    """
    辅助函数：美化并完整地打印演示大纲，以便用户审查。
    """
    # 打印顶部边框和标题
    print("\n" + "="*80)
    print("📋 Generated Presentation Plan (Awaiting Your Approval)".center(80))
    print("="*80)

    # 处理大纲为空的情况
    if not slides_plan:
        print("  (The generated plan is empty.)")
        print("="*80 + "\n")
        return

    # 遍历并打印每一页的详细信息
    for slide in slides_plan:
        # --- 基本信息 ---
        slide_num = slide.get('slide_page') 
        title = slide.get('title')
        print(f"\n[Slide {slide_num}] {title}")
        print("-" * (len(title) + 12)) # 打印与标题长度匹配的下划线

        # --- 正文要点 ---
        content = slide.get('content')
        print("  Content:")
        for point in content:
            # 使用 • 符号和缩进，使其更像列表
            print(f"    • {point}")

        # --- 媒体资源 ---
        assets = []
        if slide.get('include_figures'):
            for figure in slide.get('figures_reference'):
                assets.append(f"🖼️ Figure (Caption: {figure.get('caption')}; Path: {figure.get('path')})")
        
        if slide.get('include_tables'):
            for table in slide.get('tables_reference'):
                assets.append(f"📊 Table (Caption: {table.get('caption')})")
            
        if slide.get('include_equations'):
            for equation in slide.get('equations_reference'):
                latex_preview = (equation.get('latex')[:30] + '...') if len(equation.get('latex')) > 30 else equation.get('latex')
                assets.append(f"🧮 Equation (LaTeX: {latex_preview})")
        
        if assets:
            print(f"  Assets:")
            for asset in assets:
                print(f"    {asset}")
            
        # --- 演讲者备注 ---
        print(f"  Notes: {slide.get('notes')}")

    # 打印底部边框
    print("\n" + "="*80)
    print("👆 Please review the plan above. You can approve, or provide feedback for revision.".center(80))
    print("="*80 + "\n")

