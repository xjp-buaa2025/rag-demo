#!/bin/bash
cd "$(dirname "$0")"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" run_backend.py &
echo "✓ Backend started (PID: $!)"
cd frontend && npm run dev
