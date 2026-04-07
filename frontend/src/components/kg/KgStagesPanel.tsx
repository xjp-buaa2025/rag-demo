import { useState, useEffect } from 'react'
import Stage1Bom from './stages/Stage1Bom'
import Stage2Manual from './stages/Stage2Manual'
import Stage3Cad from './stages/Stage3Cad'
import Stage4Validate from './stages/Stage4Validate'
import { getKgStagesStatus } from '../../api/client'

type TabId = 'stage1' | 'stage2' | 'stage3' | 'stage4'

const TABS = [
  { id: 'stage1', label: '阶段一：BOM入库',  stageKey: 'bom' },
  { id: 'stage2', label: '阶段二：参考手册', stageKey: 'manual' },
  { id: 'stage3', label: '阶段三：CAD模型',  stageKey: 'cad' },
  { id: 'stage4', label: '阶段四：验证测试', stageKey: null },
] as const

export default function KgStagesPanel() {
  const [activeTab, setActiveTab] = useState<TabId>('stage1')
  const [stagesStatus, setStagesStatus] = useState<Record<string, boolean>>({})

  const refreshStatus = () => {
    getKgStagesStatus().then(s => setStagesStatus({
      bom: s.bom.exists, manual: s.manual.exists, cad: s.cad.exists
    })).catch(() => {})
  }

  useEffect(() => { refreshStatus() }, [])

  return (
    <div className="space-y-4">
      {/* Tab 标签栏 */}
      <div className="flex gap-1 border-b border-slate-200">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as TabId)}
            className={`px-4 py-2 text-sm font-medium rounded-t transition-colors ${
              activeTab === tab.id
                ? 'bg-white border border-b-white border-slate-200 text-blue-600'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            {tab.label}
            {tab.stageKey && stagesStatus[tab.stageKey] && (
              <span className="ml-1 text-green-500">✓</span>
            )}
          </button>
        ))}
      </div>

      {/* 面板内容：始终挂载，用 hidden 隐藏非活动 Tab，保留各阶段状态 */}
      <div className="min-h-64">
        <div className={activeTab === 'stage1' ? '' : 'hidden'}><Stage1Bom onComplete={refreshStatus} /></div>
        <div className={activeTab === 'stage2' ? '' : 'hidden'}><Stage2Manual onComplete={refreshStatus} /></div>
        <div className={activeTab === 'stage3' ? '' : 'hidden'}><Stage3Cad onComplete={refreshStatus} /></div>
        <div className={activeTab === 'stage4' ? '' : 'hidden'}><Stage4Validate /></div>
      </div>
    </div>
  )
}
