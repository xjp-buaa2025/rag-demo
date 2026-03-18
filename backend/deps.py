"""
backend/deps.py — FastAPI 依赖注入函数

通过 Depends(get_state) 在路由中获取全局状态，
避免直接引用模块级全局变量，方便单元测试时替换 mock。
"""

from fastapi import Request
from backend.state import AppState


def get_state(request: Request) -> AppState:
    """获取应用全局状态（由 lifespan 初始化后存入 app.state）。"""
    return request.app.state.app_state


def get_llm_model(request: Request) -> str:
    """获取当前 LLM 模型名称。"""
    return request.app.state.llm_model


def get_data_dir(request: Request) -> str:
    """获取文档数据目录路径。"""
    return request.app.state.data_dir


def get_bom_default(request: Request) -> str:
    """获取默认 BOM 文件路径。"""
    return request.app.state.bom_default


def get_neo4j_cfg(request: Request) -> dict:
    """获取 Neo4j 连接配置字典 {uri, user, pass}。"""
    return request.app.state.neo4j_cfg
