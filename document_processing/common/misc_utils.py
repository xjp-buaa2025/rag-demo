"""
document_processing/common/misc_utils.py — deepdoc common.misc_utils shim

deepdoc 通过以下方式使用：
  from common.misc_utils import pip_install_torch, thread_pool_exec
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed


def pip_install_torch():
    """
    torch 已在 rag_demo 环境中安装，空实现即可。
    deepdoc 在某些路径会调用此函数确保 torch 存在。
    """
    pass


def thread_pool_exec(fn, items, max_workers=None):
    """
    并发执行 fn(item) 对每个 item，返回结果列表（顺序与 items 对应）。

    Args:
        fn: 可调用对象，接收单个 item
        items: 可迭代的输入列表
        max_workers: 线程池大小，默认为 CPU 数量
    """
    items = list(items)
    if not items:
        return []

    if max_workers is None:
        max_workers = min(len(items), (os.cpu_count() or 1) * 2)

    results = [None] * len(items)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {executor.submit(fn, item): i for i, item in enumerate(items)}
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                results[idx] = e
    return results
