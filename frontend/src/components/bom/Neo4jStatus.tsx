// ============================================================
// Neo4jStatus — Neo4j 图数据库状态检测
//
// 对应 Gradio Tab 2 的"⚙️ Neo4j 图数据库状态" Accordion。
// 功能：
//   - 点击按钮调 GET /bom/status 检测连接
//   - 连接成功：显示节点数、关系数、URI
//   - 连接失败：显示红色错误提示 + 启动命令
// ============================================================

import { useState } from 'react'
import { getBomStatus } from '../../api/client'
import type { BomStatus } from '../../types'

export default function Neo4jStatus() {
  const [status, setStatus] = useState<BomStatus | null>(null)
  const [checking, setChecking] = useState(false)

  const handleCheck = async () => {
    setChecking(true)
    try {
      const s = await getBomStatus()
      setStatus(s)
    } catch (e) {
      setStatus({ connected: false, uri: '', error: String(e) })
    } finally {
      setChecking(false)
    }
  }

  return (
    <div className="border border-slate-200 rounded-lg p-4 bg-white space-y-3">
      <div className="flex items-center gap-3">
        <button
          onClick={handleCheck}
          disabled={checking}
          className="px-4 py-2 text-sm bg-emerald-600 text-white rounded-md hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          {checking ? '⏳ 检测中…' : '🔍 检测 Neo4j 连接'}
        </button>
        <span className="text-xs text-slate-400">默认地址：bolt://localhost:7687</span>
      </div>

      {status && (
        <div className={`rounded-md p-3 text-sm ${status.connected ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200'}`}>
          {status.connected ? (
            <div className="space-y-1 text-emerald-800">
              <p>✅ <strong>已连接</strong> — {status.uri}</p>
              <p>节点总数：<strong>{status.nodes}</strong>（Assembly + Part + Standard）</p>
              <p>CHILD_OF 关系：<strong>{status.edges}</strong> 条</p>
            </div>
          ) : (
            <div className="space-y-1 text-red-700">
              <p>❌ <strong>连接失败</strong></p>
              <p className="text-xs">{status.error}</p>
              <p className="text-xs mt-1">
                启动命令：<code className="bg-red-100 px-1 rounded">docker start neo4j</code>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
