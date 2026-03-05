import os
import sys
import glob
import tempfile
import subprocess

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# MinerU CLI 路径（与当前 Python 同一 conda 环境）
if sys.platform == 'win32':
    MINERU_EXE = os.path.join(os.path.dirname(sys.executable), 'Scripts', 'mineru.exe')
else:
    MINERU_EXE = os.path.join(os.path.dirname(sys.executable), 'mineru')


def convert_pdf(pdf_path: str) -> str:
    """
    用 MinerU pipeline 后端将 PDF 转为 Markdown（支持 OCR）。
    首次运行会自动下载布局/OCR 模型（约 2-4 GB），请保持网络畅通。
    国内网络慢时可设环境变量 MINERU_MODEL_SOURCE=modelscope 后再运行。
    """
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    with tempfile.TemporaryDirectory() as tmp_dir:
        cmd = [
            MINERU_EXE,
            '-p', pdf_path,
            '-o', tmp_dir,
            '-b', 'pipeline',  # CPU 通用后端，支持 OCR
            '-m', 'auto',      # 自动判断：文字层/扫描图自动选 txt or ocr
            '-l', 'ch',        # 中文优先（提升识别率）
        ]
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding='utf-8', errors='replace', env=env
        )
        if result.returncode != 0:
            raise RuntimeError(
                (result.stderr or result.stdout)[-1500:].strip()
            )

        # 标准输出路径: tmp_dir/{stem}/auto/{stem}.md
        expected = os.path.join(tmp_dir, stem, 'auto', f'{stem}.md')
        if os.path.exists(expected):
            md_path = expected
        else:
            # 回退：递归找最大的 .md（排除辅助调试文件）
            found = glob.glob(os.path.join(tmp_dir, '**', '*.md'), recursive=True)
            found = [f for f in found if not os.path.basename(f).startswith(stem + '_')]
            if not found:
                raise RuntimeError("MinerU 未生成 .md 文件，请检查上方错误输出")
            found.sort(key=os.path.getsize, reverse=True)
            md_path = found[0]

        with open(md_path, 'r', encoding='utf-8') as f:
            return f.read()


def main():
    pdfs = [f for f in os.listdir(DATA_DIR) if f.lower().endswith('.pdf')]
    if not pdfs:
        print("data/ 目录下没有 PDF 文件。")
        return

    for fname in pdfs:
        pdf_path = os.path.join(DATA_DIR, fname)
        md_path = os.path.join(DATA_DIR, os.path.splitext(fname)[0] + '.md')
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
