from datetime import datetime
import json
import os
import argparse
import logging
import asyncio

from dotenv import load_dotenv
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command

load_dotenv()
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
    
    parser.add_argument('--model_name', default='gpt-4o', help='Default LLM model (fallback for all stages).')
    parser.add_argument('--vision_model', default=None, help='Model for vision tasks (style extraction, image orientation). Defaults to --model_name.')
    parser.add_argument('--svg_model', default=None, help='Model for SVG code generation. Defaults to --model_name.')
    parser.add_argument('--text_model', default=None, help='Model for text generation (planning, expansion, critique). Defaults to --model_name.')
    parser.add_argument('--marker_path', default='models/marker', help='Path to the local Marker model directory.')

    parser.add_argument('--skip_plan_review', action='store_true', help='Auto-approve the plan without HITL review.')
    parser.add_argument('--skip_pptx_review', action='store_true', help='Auto-approve the final PPTX without HITL review.')

    parser.add_argument('--thread_id', default=None, help='A specific session ID to resume a previously interrupted workflow.')
    parser.add_argument('--verbose', action='store_true', help='Enable detailed debug logging.')
    
    return parser.parse_args()

async def run_workflow(graph, initial_state, config):
    """运行完整工作流，通过 interrupt/Command 机制处理人工交互"""
    graph_input = initial_state

    while True:
        try:
            # 执行图直到完成或遇到 interrupt
            async for event in graph.astream(graph_input, config=config, stream_mode="updates"):
                for node_name, _ in event.items():
                    logging.info(f"✅ Node '{node_name}' completed.")

            # 获取当前状态快照
            snapshot = await graph.aget_state(config)

            # 检查是否完成（无后续节点且无中断）
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

            # 检查是否有 interrupt 需要处理
            if snapshot.tasks:
                interrupt_handled = False
                for task in snapshot.tasks:
                    if task.interrupts:
                        interrupt_value = task.interrupts[0].value
                        hitl_type = interrupt_value.get("type", "unknown")
                        prompt_text = interrupt_value.get("prompt", ">> ")

                        # HITL 2 额外提示 PPTX 路径
                        if hitl_type == "pptx_review":
                            pptx_path = interrupt_value.get("pptx_path", "")
                            logging.info(f"\n✨ Preview Ready: Your presentation has been generated at '{pptx_path}'")

                        logging.info(f"🛑 HITL: {hitl_type} - Waiting for user input.")
                        user_input = input(f">> {prompt_text} ").strip()

                        # 用 Command(resume=...) 恢复图执行
                        graph_input = Command(resume=user_input)
                        interrupt_handled = True
                        break

                if interrupt_handled:
                    continue

            # 无 interrupt 但有后续节点，继续执行（从 checkpoint 恢复）
            graph_input = None

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
    
    default_model = args.model_name
    config = {
        "configurable": {
            "thread_id": thread_id,
            "max_concurrency": 4,
            "pdf_path": args.pdf_path,
            "style_image_path": args.style_image_path,
            "output_dir": session_dir,
            "marker_path": args.marker_path,
            "verbose": args.verbose,
            # 各阶段模型：未指定时回退到 model_name
            "model_name": default_model,
            "vision_model": args.vision_model or default_model,
            "svg_model": args.svg_model or default_model,
            "text_model": args.text_model or default_model,
            # HITL 跳过标志
            "skip_plan_review": args.skip_plan_review,
            "skip_pptx_review": args.skip_pptx_review,
            "base_url": os.getenv("OPENAI_BASE_URL"),
            "api_key": os.getenv("OPENAI_API_KEY"),
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
