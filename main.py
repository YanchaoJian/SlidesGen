from datetime import datetime
import json
import os
import sys
import argparse
import logging
import asyncio


class _Tee:
    """同时写入原始流和日志文件的简易 tee。

    控制台原样输出；文件按行缓冲，对 tqdm 这类用 ``\\r`` 刷新的进度条，
    仅在行结束（``\\n``）时写入最终一帧，丢弃中间所有刷新内容。
    """

    def __init__(self, stream, file):
        self.stream = stream
        self.file = file
        self._buf = ""

    def write(self, data):
        try:
            self.stream.write(data)
        except Exception:
            pass
        try:
            self._buf += data
            while "\n" in self._buf:
                line, self._buf = self._buf.split("\n", 1)
                # 若该行内含 \r（进度条刷新），只保留最后一段
                if "\r" in line:
                    line = line.rsplit("\r", 1)[-1]
                if line:
                    self.file.write(line + "\n")
            # 防止无 \n 的纯 \r 流持续膨胀缓冲
            if "\r" in self._buf:
                self._buf = self._buf.rsplit("\r", 1)[-1]
            self.file.flush()
        except Exception:
            pass

    def flush(self):
        for s in (self.stream, self.file):
            try:
                s.flush()
            except Exception:
                pass

    def isatty(self):
        return getattr(self.stream, "isatty", lambda: False)()

    def __getattr__(self, name):
        return getattr(self.stream, name)

from dotenv import load_dotenv
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command

load_dotenv()
from workflow.state import initialize_overall_state
from workflow.graph import build_graph

def setup_logging(verbose=False, session_dir=None):
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter('%(asctime)s - %(levelname)-7s: %(message)s', datefmt='%m-%d %H:%M')

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    handlers = []
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # 按会话写入 log.txt
    if session_dir:
        os.makedirs(session_dir, exist_ok=True)
        log_path = os.path.join(session_dir, "log.txt")
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

        # 将 stdout/stderr 也镜像到日志文件，捕获 print() 和未处理异常的 traceback
        log_file = open(log_path, "a", encoding="utf-8", buffering=1)
        sys.stdout = _Tee(sys.__stdout__, log_file)
        sys.stderr = _Tee(sys.__stderr__, log_file)

        # 兜底：未捕获异常也写入日志
        def _excepthook(exc_type, exc, tb):
            logging.getLogger().critical("Uncaught exception", exc_info=(exc_type, exc, tb))
            sys.__excepthook__(exc_type, exc, tb)
        sys.excepthook = _excepthook

    logging.basicConfig(level=level, handlers=handlers, force=True)

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

    parser.add_argument('--llm_max_retries', type=int, default=3,
                        help='Unified retry limit for ALL LLM-related loops: style protocol check, '
                             'SVG generation/validation, design critique, and the underlying ChatOpenAI '
                             'SDK transient-error retries (default: 3).')

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
                with open(snapshot_file, "w", encoding="utf-8") as sf:
                    json.dump(snapshot.values, sf, indent=2, ensure_ascii=False, default=str)
                logging.info(f"📄 Snapshot saved to: {snapshot_file}")
                break

            # 检查是否有 interrupt 需要处理
            if snapshot.tasks:
                interrupt_handled = False
                for task in snapshot.tasks:
                    if task.interrupts:
                        interrupt_value = task.interrupts[0].value
                        hitl_type = interrupt_value.get("type")
                        prompt_text = interrupt_value.get("prompt")

                        # HITL 2 额外提示 PPTX 路径
                        if hitl_type == "pptx_review":
                            pptx_path = interrupt_value.get("pptx_path")
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

    # 1. 配置会话
    is_resuming = bool(args.thread_id)
    safe_model_name = args.model_name.replace('/', '_').replace('\\', '_')
    thread_id = args.thread_id if is_resuming else f"{datetime.now().strftime('%m%d_%H%M')}_{safe_model_name}"
    session_dir = os.path.join(args.output_dir, thread_id)

    setup_logging(args.verbose, session_dir=session_dir)
    
    default_model = args.model_name
    config = {
        "max_concurrency": 4,  # LangGraph 顶层字段：限制 Send 扇出的并发子任务数
        "configurable": {
            "thread_id": thread_id,
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
            "llm_max_retries": args.llm_max_retries,
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
        logging.info("\n\n👋 Program interrupted by user. Rerun with the same --thread_id to resume.")
    except Exception as e:
        logging.error(f"❌ A fatal error occurred: {e}", exc_info=True)
