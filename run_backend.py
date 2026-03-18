"""
run_backend.py — FastAPI 后端快捷启动脚本

运行方式（在项目根目录下）：
  PYTHONUTF8=1 python run_backend.py

服务启动后访问：
  API 文档：http://localhost:8000/docs
  健康检查：http://localhost:8000/health
  Gradio UI（另开终端）：python app.py → http://localhost:7860
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,       # 开发模式：文件变更时自动重载
        reload_dirs=["backend"],
    )
