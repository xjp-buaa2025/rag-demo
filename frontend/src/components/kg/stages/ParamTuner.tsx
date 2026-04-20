import React, { useState } from 'react'

interface Props {
  stageN: 1 | 2
  onRerun: (params: RerunParams) => void
  running: boolean
}

export interface RerunParams {
  confidence_threshold: number
  gleaning_rounds: number
}

export default function ParamTuner({ stageN, onRerun, running }: Props) {
  const [threshold, setThreshold] = useState(0.3)
  const [gleaning, setGleaning] = useState(1)

  return (
    <div className="text-xs">
      <p className="text-gray-400 mb-2">调整参数后点击重跑，结果将替换本阶段当前数据：</p>

      <div className="flex flex-col gap-2">
        <label className="flex items-center gap-3">
          <span className="text-gray-300 w-28 shrink-0">置信度阈值</span>
          <input
            type="range" min={0} max={0.9} step={0.05}
            value={threshold}
            onChange={e => setThreshold(parseFloat(e.target.value))}
            className="flex-1"
          />
          <span className="text-blue-400 w-10 text-right">{threshold.toFixed(2)}</span>
        </label>
        <p className="text-gray-600 pl-31 -mt-1">低于此置信度的三元组将被过滤</p>

        {stageN === 2 && (
          <label className="flex items-center gap-3">
            <span className="text-gray-300 w-28 shrink-0">Gleaning 轮次</span>
            <input
              type="range" min={0} max={3} step={1}
              value={gleaning}
              onChange={e => setGleaning(parseInt(e.target.value))}
              className="flex-1"
            />
            <span className="text-blue-400 w-10 text-right">{gleaning}</span>
          </label>
        )}
      </div>

      <button
        onClick={() => onRerun({ confidence_threshold: threshold, gleaning_rounds: gleaning })}
        disabled={running}
        className="mt-3 px-3 py-1 bg-amber-800 text-white rounded hover:bg-amber-700 disabled:opacity-40"
      >
        {running ? '重跑中...' : `重新运行 Stage ${stageN}`}
      </button>
      <p className="text-gray-600 mt-1">注：重跑后需重新审阅</p>
    </div>
  )
}
