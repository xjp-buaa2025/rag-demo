"""
document_processing/common/file_utils.py — deepdoc common.file_utils shim

deepdoc 视觉模块通过以下方式使用：
  from common.file_utils import get_project_base_directory, traversal_files

get_project_base_directory() 返回项目根目录，deepdoc 据此找到 ONNX 模型：
  {root}/rag/res/deepdoc/layout.onnx
  {root}/rag/res/deepdoc/tsr.onnx
  {root}/rag/res/deepdoc/det.onnx
  {root}/rag/res/deepdoc/rec.onnx
"""

import os


def get_project_base_directory(*args) -> str:
    """
    返回项目根目录（document_processing/ 的父目录）。
    deepdoc 模型文件存放于 {root}/rag/res/deepdoc/。

    支持可选的路径拼接参数（与 RAGFlow 原版签名兼容）。
    """
    # 本文件位于 document_processing/common/file_utils.py
    # 项目根 = document_processing/../ = rag-demo/
    this_file = os.path.abspath(__file__)
    doc_processing_dir = os.path.dirname(os.path.dirname(this_file))
    project_root = os.path.dirname(doc_processing_dir)
    if args:
        return os.path.join(project_root, *args)
    return project_root


def traversal_files(directory: str) -> list:
    """递归列举目录下所有文件的绝对路径。"""
    result = []
    for dirpath, _, filenames in os.walk(directory):
        for fname in filenames:
            result.append(os.path.join(dirpath, fname))
    return result
