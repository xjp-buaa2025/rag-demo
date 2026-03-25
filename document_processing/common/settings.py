"""
document_processing/common/settings.py — deepdoc common.settings shim

deepdoc 通过以下方式使用：
  from common import settings
  settings.PARALLEL_DEVICES

PARALLEL_DEVICES 控制并行设备数量，0 表示单设备（CPU）模式。
"""

PARALLEL_DEVICES = 0
