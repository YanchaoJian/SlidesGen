"""日志基础设施：Tee 双写流 + 会话级日志配置。"""

import logging
import os
import sys


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
