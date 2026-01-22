"""工作流图可视化脚本"""
import os
from workflow.graph import build_graph
from langgraph.checkpoint.memory import MemorySaver

def visualize_workflow():
    """生成并保存工作流图"""
    checkpointer = MemorySaver()
    graph = build_graph(checkpointer)
    
    # 方法1: 生成 PNG 图片（需要安装 pygraphviz 或 graphviz）
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        output_path = "output/workflow_graph.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(png_data)
        print(f"✅ Workflow graph saved to {output_path}")
    except Exception as e:
        print(f"❌ PNG generation failed: {e}")
        print("Tip: Install graphviz - pip install pygraphviz or brew install graphviz")
    
    # 方法2: 生成 Mermaid 语法（可在线渲染）
    try:
        mermaid_code = graph.get_graph().draw_mermaid()
        mermaid_path = "output/workflow_graph.mmd"
        
        with open(mermaid_path, "w", encoding="utf-8") as f:
            f.write(mermaid_code)
        print(f"✅ Mermaid diagram saved to {mermaid_path}")
        print("   View online: https://mermaid.live/")
    except Exception as e:
        print(f"❌ Mermaid generation failed: {e}")
    
    # 方法3: 生成 ASCII 文本表示
    try:
        ascii_repr = graph.get_graph().print_ascii()
        print("\n📊 Workflow Graph (ASCII):")
        print(ascii_repr)
    except Exception as e:
        print(f"❌ ASCII generation failed: {e}")

if __name__ == "__main__":
    visualize_workflow()