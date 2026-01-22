from datetime import datetime
import json
import os
import argparse
import logging
import asyncio

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from workflow.state import initialize_overall_state
from workflow.graph import build_graph

def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)-7s: %(message)s', datefmt='%m-%d %H:%M'))

    # 只保留控制台输出，不保存到文件
    logging.basicConfig(
        level=level,
        handlers=[console_handler]
    )

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AI PPT Generator.")
    parser.add_argument('--pdf_path', required=True, help='Path to the input PDF file.')
    parser.add_argument('--style_image_path', required=True, help='Path to the reference style image.')
    parser.add_argument('--output_dir', default='output', help='Root directory for all outputs.')
    
    parser.add_argument('--model_name', default='gpt-4o', help='Name of the LLM to use.')
    parser.add_argument('--marker_path', default='models/marker', help='Path to the local Marker model directory.')
    
    parser.add_argument('--thread_id', default=None, help='A specific session ID to resume a previously interrupted workflow.')
    parser.add_argument('--enhance_marker', action='store_true', help='Enable content enhancement using Marker model.')
    parser.add_argument('--verbose', action='store_true', help='Enable detailed debug logging.')
    
    return parser.parse_args()

async def run_workflow(graph, initial_state, config):
    """运行完整工作流"""
    current_state = initial_state
    
    while True:
        try:
            # 执行图直到下一个断点或完成
            async for event in graph.astream(current_state, config=config, stream_mode="updates"):
                for node_name, _ in event.items():
                    logging.info(f"✅ Node '{node_name}' completed.")
            
            # 获取当前状态快照
            snapshot = await graph.aget_state(config)
            
            # 检查是否完成
            if not snapshot.next:
                logging.info("✅ Workflow Completed Successfully!")
                final_pptx_path = snapshot.values.get("final_pptx_path")
                if final_pptx_path:
                    logging.info(f"🎉 PPT file is ready at: {final_pptx_path}")
                
                # 保存最终状态快照
                snapshot_file = os.path.join(config["configurable"]["output_dir"], "final_snapshot.json")
                with open(snapshot_file, "w", encoding="utf-8") as f:
                    json.dump(snapshot.values, f, indent=2, ensure_ascii=False, default=str)
                logging.info(f"📄 Snapshot saved to: {snapshot_file}")
                break
            
            # 继续下一轮
            current_state = None
            
        except Exception as e:
            logging.error(f"❌ Workflow execution failed: {e}", exc_info=True)
            break

async def main():
    args = parse_args()
    setup_logging(args.verbose)
    
    # 1. 配置会话
    is_resuming = bool(args.thread_id)
    thread_id = args.thread_id if is_resuming else datetime.now().strftime("%m%d_%H%M")
    session_dir = os.path.join(args.output_dir, thread_id)
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "max_concurrency": 4,
            "pdf_path": args.pdf_path,
            "style_image_path": args.style_image_path,
            "output_dir": session_dir,
            "marker_path": args.marker_path,
            "enhance_marker": args.enhance_marker,
            "verbose": args.verbose,
            "model_name": args.model_name,
            "base_url": os.getenv("OPENAI_BASE_URL"),
            "api_key": os.getenv("OPENAI_API_KEY")
        },
    }

    # 2. 准备输出目录和初始状态
    initial_state = None
    if not is_resuming:
        os.makedirs(session_dir, exist_ok=True)
        logging.info(f"🚀 Starting new session: {thread_id}")
        initial_state = initialize_overall_state()
    else:
        logging.info(f"🔄 Resuming session: {thread_id}")

    # 3. 设置持久化后端
    checkpoint_dir = os.path.join(session_dir, "checkpoints")
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_db = os.path.join(checkpoint_dir, "checkpoints.sqlite")
    
    async with AsyncSqliteSaver.from_conn_string(checkpoint_db) as checkpointer:
        # 4. 编译图
        graph = build_graph(checkpointer=checkpointer)
        
        # 5. 启动工作流
        await run_workflow(graph, initial_state, config)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        logging.info("\n\n👋 Program interrupted by user. Rerun with the same --thread-id to resume.")
    except Exception as e:
        logging.error(f"❌ A fatal error occurred: {e}", exc_info=True)