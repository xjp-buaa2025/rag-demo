# PT6A 论文 PDF 编译脚本
# 用法：在 paper 目录下右键 → "用 PowerShell 运行" 或 cd paper; .\build.ps1
#
# 依赖：MikTeX 或 TeXLive（含 xelatex）
#       中文字体 SimHei（Windows 自带）
#       ctex 宏包（首次编译时 MikTeX 会自动下载）

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== PT6A MHRAG 论文编译 ===" -ForegroundColor Cyan

# 检查 xelatex
$xe = Get-Command xelatex -ErrorAction SilentlyContinue
if (-not $xe) {
    Write-Host "ERROR: 找不到 xelatex。请先安装 MikTeX 或 TeXLive。" -ForegroundColor Red
    Write-Host "MikTeX 下载: https://miktex.org/download"
    exit 1
}
Write-Host "xelatex: $($xe.Path)" -ForegroundColor Green

# 清理旧产物（保留 .pdf 备用对比）
$cleanExts = @("aux", "log", "toc", "out", "lof", "lot", "blg", "synctex.gz", "fls", "fdb_latexmk")
foreach ($ext in $cleanExts) {
    Get-ChildItem -Filter "*.$ext" -ErrorAction SilentlyContinue | Remove-Item -Force
}

# 第一遍
Write-Host "`n--- Pass 1/2 ---" -ForegroundColor Yellow
& xelatex -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: 第一遍编译失败。查看 main.log 定位错误。" -ForegroundColor Red
    exit 1
}

# 第二遍（生成 ToC + 引用）
Write-Host "`n--- Pass 2/2 ---" -ForegroundColor Yellow
& xelatex -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: 第二遍编译失败。" -ForegroundColor Red
    exit 1
}

if (Test-Path "main.pdf") {
    $size = (Get-Item main.pdf).Length / 1024
    Write-Host "`n[OK] main.pdf 生成成功（$([math]::Round($size, 1)) KB）" -ForegroundColor Green
    Write-Host "打开方式: start main.pdf"
} else {
    Write-Host "ERROR: main.pdf 未生成。" -ForegroundColor Red
    exit 1
}
