"""
pdf_to_md.py — 第一步：批量将 data/ 目录下的 PDF 转换为 Markdown 文件

工作流：
  1. 扫描 data/ 目录，找到所有 .pdf 文件
  2. 对每个 PDF 调用 MinerU CLI（pipeline 后端）进行布局分析 + OCR
  3. 读取 MinerU 生成的 .md 文件，写到 data/{书名}.md
  4. 后续 main_ingest.py 再处理这些 .md 文件入库

为什么要这一步（而不是直接用 PyMuPDF）：
  - PyMuPDF get_text() 对扫描版 PDF 完全无效（没有文字层）
  - MinerU 先检测布局，再对图像区域做 OCR，结构化输出 Markdown
  - 中间产物 .md 文件可以人工检查质量，发现问题可手动修正

详见 PROJECT_GUIDE.md § 6.1
"""

import os
import sys
import glob
import tempfile
import subprocess

# data/ 目录：存放原始文档的地方
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# 定位 MinerU 的 CLI 可执行文件路径
# 它和当前 Python 解释器在同一 conda 环境下，Scripts/ 子目录里
if sys.platform == 'win32':
    MINERU_EXE = os.path.join(os.path.dirname(sys.executable), 'Scripts', 'mineru.exe')
else:
    MINERU_EXE = os.path.join(os.path.dirname(sys.executable), 'mineru')


def convert_pdf(pdf_path: str) -> str:
    """
    用 MinerU pipeline 后端将单个 PDF 转为 Markdown 字符串。

    MinerU CLI 参数说明：
      -b pipeline  使用 pipeline 后端（PaddleOCR + DocLayout-YOLO），CPU 即可运行
      -m auto      自动判断每页用文字提取还是 OCR（混合文档友好）
      -l ch        中文优先，提升中文 OCR 识别率

    MinerU 会把结果写到一个临时目录，目录结构为：
      tmp_dir/{stem}/auto/{stem}.md

    我们读取这个 .md 文件内容后返回，临时目录随 with 块自动删除。

    首次运行会从 HuggingFace 自动下载模型（约 2-4 GB）。
    国内网络慢时，运行前设置环境变量：MINERU_MODEL_SOURCE=modelscope
    """
    stem = os.path.splitext(os.path.basename(pdf_path))[0]

    # 使用临时目录存放 MinerU 输出，避免污染 data/ 目录
    with tempfile.TemporaryDirectory() as tmp_dir:
        cmd = [
            MINERU_EXE,
            '-p', pdf_path,   # 输入 PDF 路径
            '-o', tmp_dir,    # 输出到临时目录
            '-b', 'pipeline', # 后端：pipeline（CPU 通用，支持 OCR）
            '-m', 'auto',     # 方法：自动检测
            '-l', 'ch',       # 语言：中文
        ]

        # 继承父进程环境变量，并确保 UTF-8 输出
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
        )

        # 非 0 返回码表示 MinerU 出错
        if result.returncode != 0:
            raise RuntimeError(
                (result.stderr or result.stdout)[-1500:].strip()
            )

        # 标准输出路径：tmp_dir/{stem}/auto/{stem}.md
        expected = os.path.join(tmp_dir, stem, 'auto', f'{stem}.md')
        if os.path.exists(expected):
            md_path = expected
        else:
            # 回退：递归搜索所有 .md，排除调试辅助文件（文件名以 {stem}_ 开头的）
            found = glob.glob(os.path.join(tmp_dir, '**', '*.md'), recursive=True)
            found = [f for f in found if not os.path.basename(f).startswith(stem + '_')]
            if not found:
                raise RuntimeError("MinerU 未生成 .md 文件，请检查上方错误输出")
            # 多个候选时取内容最多的（最大文件）
            found.sort(key=os.path.getsize, reverse=True)
            md_path = found[0]

        with open(md_path, 'r', encoding='utf-8') as f:
            return f.read()


def main():
    # 找出 data/ 目录下所有 PDF
    pdfs = [f for f in os.listdir(DATA_DIR) if f.lower().endswith('.pdf')]
    if not pdfs:
        print("data/ 目录下没有 PDF 文件。")
        return

    for fname in pdfs:
        pdf_path = os.path.join(DATA_DIR, fname)
        # 目标 Markdown 文件路径，和 PDF 同名，扩展名换成 .md
        md_path = os.path.join(DATA_DIR, os.path.splitext(fname)[0] + '.md')

        # 幂等：已存在则跳过，避免重复转换浪费时间
        if os.path.exists(md_path):
            print(f"跳过（MD 已存在）: {fname}")
            continue

        print(f"转换中: {fname}  （首次运行需下载模型，请耐心等待…）")
        try:
            md_text = convert_pdf(pdf_path)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_text)
            size_kb = os.path.getsize(md_path) // 1024
            print(f"  完成 → {os.path.basename(md_path)} ({size_kb} KB)")
        except Exception as e:
            print(f"  失败: {e}")

    print("\n转换完成。运行 main_ingest.py --clear 开始入库。")


if __name__ == '__main__':
    main()
