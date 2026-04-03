// ============================================================
// shared/SourceCard.tsx — 溯源来源卡片（三路渲染）
//
// chunk_type = "bom_entity"   → BomEntityCard（属性表格）
// chunk_type = "bom_relation" → BomRelationCard（关系可视化）
// 其他                         → 文本/图片摘录（通用）
//
// 通过 theme prop 控制颜色主题：
//   "blue"   → RAG 知识库问答（UnifiedChat RAG 模式）
//   "orange" → 装配方案问答（UnifiedChat 装配模式）
// ============================================================

import { useState } from 'react'
import type { Citation, BomEntityData, BomRelationData } from '../../types'

// ─── 关系标签映射（支持未来扩展的 9 类关系）───────────────────
const REL_LABEL: Record<string, string> = {
  CHILD_OF:       '子组件属于',
  precedes:       '工序先于',
  participatesIn: '参与工序',
  requires:       '需要工具',
  specifiedBy:    '遵循规范',
  matesWith:      '配合关系',
  adjacentTo:     '相邻关系',
  hasInterface:   '具有接口',
  constrainedBy:  '受约束于',
  isPartOf:       '属于组件',
}

// ─── 属性行辅助组件（空值自动隐藏）──────────────────────────
function PropRow({ label, value }: { label: string; value?: string | number | null }) {
  if (value === null || value === undefined || value === '') return null
  return (
    <tr>
      <td className="text-[10px] text-slate-400 pr-2 py-0.5 whitespace-nowrap align-top">{label}</td>
      <td className="text-[11px] text-slate-700 py-0.5 break-all">{String(value)}</td>
    </tr>
  )
}

// ─── BOM 实体卡片内容（属性表格）────────────────────────────
function BomEntityCard({ entity }: { entity: BomEntityData }) {
  const TYPE_STYLES: Record<string, string> = {
    Assembly: 'bg-amber-50  text-amber-800  border-amber-300',
    Part:     'bg-sky-50    text-sky-800    border-sky-300',
    Standard: 'bg-emerald-50 text-emerald-800 border-emerald-300',
  }
  const TYPE_LABELS: Record<string, string> = {
    Assembly: '组件', Part: '零件', Standard: '标准件',
  }
  const style = TYPE_STYLES[entity.entity_type] ?? 'bg-slate-50 text-slate-700 border-slate-300'
  const label = TYPE_LABELS[entity.entity_type] ?? entity.entity_type

  return (
    <div className="mt-1.5">
      <span className={`inline-block text-[10px] font-semibold px-1.5 py-0.5 rounded border mb-1.5 ${style}`}>
        {label}&nbsp;·&nbsp;{entity.part_id}
      </span>
      <table className="w-full border-collapse">
        <tbody>
          <PropRow label="英文名"  value={entity.part_name_en} />
          <PropRow label="层级码"  value={entity.level_code} />
          <PropRow label="数量"    value={entity.qty != null ? `${entity.qty} ${entity.unit ?? ''}`.trim() : undefined} />
          <PropRow label="材料"    value={entity.material} />
          <PropRow label="重量"    value={entity.weight_kg != null ? `${entity.weight_kg} kg` : undefined} />
          <PropRow label="规格"    value={entity.spec} />
          <PropRow label="备注"    value={entity.note} />
          {entity.parent_name && (
            <PropRow label="父组件" value={`${entity.parent_name}（${entity.parent_id ?? ''}）`} />
          )}
        </tbody>
      </table>
    </div>
  )
}

// ─── BOM 关系卡片内容（关系可视化）──────────────────────────
function BomRelationCard({ rel }: { rel: BomRelationData }) {
  const relLabel = REL_LABEL[rel.rel_type] ?? rel.rel_type

  return (
    <div className="mt-1.5">
      <span className="inline-block text-[10px] font-semibold px-1.5 py-0.5 rounded border mb-2 bg-purple-50 text-purple-800 border-purple-300">
        {relLabel}
      </span>
      {/* 实体 A → 箭头 → 实体 B */}
      <div className="flex items-center gap-1.5 flex-wrap">
        <div className="flex flex-col items-center gap-0.5">
          <span className="text-[9px] text-slate-400">{rel.from_type}</span>
          <div
            className="px-2 py-1 bg-sky-50 border border-sky-200 rounded text-[11px] text-sky-800 font-medium max-w-[88px] truncate"
            title={rel.from_name}
          >
            {rel.from_name}
          </div>
          <span className="text-[9px] text-slate-400">{rel.from_id}</span>
        </div>

        <div className="flex flex-col items-center gap-0.5 shrink-0">
          <span className="text-[9px] text-purple-500 font-medium">{relLabel}</span>
          <span className="text-slate-400">→</span>
        </div>

        <div className="flex flex-col items-center gap-0.5">
          <span className="text-[9px] text-slate-400">{rel.to_type}</span>
          <div
            className="px-2 py-1 bg-amber-50 border border-amber-200 rounded text-[11px] text-amber-800 font-medium max-w-[88px] truncate"
            title={rel.to_name}
          >
            {rel.to_name}
          </div>
          <span className="text-[9px] text-slate-400">{rel.to_id}</span>
        </div>
      </div>
    </div>
  )
}

// ─── 主 SourceCard 组件 ──────────────────────────────────────

type Theme = 'blue' | 'orange'

const THEME = {
  blue: {
    badge:       'text-blue-700 bg-blue-100 border-blue-200',
    activeCard:  'border-blue-400 bg-blue-50 shadow-sm ring-1 ring-blue-200',
    idleCard:    'border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50',
    expandBtn:   'text-blue-500 hover:text-blue-700',
    activeLabel: 'text-blue-500',
  },
  orange: {
    badge:       'text-orange-700 bg-orange-100 border-orange-200',
    activeCard:  'border-orange-400 bg-orange-50 shadow-sm ring-1 ring-orange-200',
    idleCard:    'border-slate-200 bg-white hover:border-orange-300 hover:bg-slate-50',
    expandBtn:   'text-orange-500 hover:text-orange-700',
    activeLabel: 'text-orange-500',
  },
}

export function SourceCard({
  src,
  active,
  onClick,
  theme = 'blue',
}: {
  src: Citation
  active: boolean
  onClick: () => void
  theme?: Theme
}) {
  const [expanded, setExpanded] = useState(false)
  const t = THEME[theme]

  const isBomEntity   = src.chunk_type === 'bom_entity'   && !!src.bom_entity
  const isBomRelation = src.chunk_type === 'bom_relation' && !!src.bom_relation

  const chunkIcon =
    isBomEntity                          ? '🔩'
    : isBomRelation                      ? '🔗'
    : src.chunk_type === 'bom'           ? '🔩'
    : src.chunk_type === 'image'         ? '🖼️'
    : src.chunk_type?.startsWith('flowchart') ? '📊'
    : '📄'

  // 卡片标题：实体/关系用自己的名称，文本块用文件名
  const cardTitle = isBomEntity
    ? src.bom_entity!.part_name
    : isBomRelation
    ? `${src.bom_relation!.from_name} → ${src.bom_relation!.to_name}`
    : src.source

  return (
    <div
      id={`source-card-${src.id}`}
      className={`rounded-lg border p-3 cursor-pointer transition-all text-left ${active ? t.activeCard : t.idleCard}`}
      onClick={onClick}
    >
      {/* 卡片头部：编号角标 + 标题 + 页码 + 图标 */}
      <div className="flex items-start gap-2 mb-1.5">
        <span className={`shrink-0 inline-flex items-center justify-center w-5 h-5 text-[11px] font-bold rounded-full border ${t.badge}`}>
          {src.id}
        </span>
        <div className="min-w-0 flex-1">
          <div className="text-xs font-medium text-slate-700 truncate" title={cardTitle}>
            {cardTitle}
          </div>
          {src.page > 0 && (
            <div className="text-[11px] text-slate-400">第 {src.page} 页</div>
          )}
        </div>
        <span className="shrink-0 text-sm">{chunkIcon}</span>
      </div>

      {/* 分支渲染 */}
      {isBomEntity && (
        <BomEntityCard entity={src.bom_entity!} />
      )}

      {isBomRelation && (
        <BomRelationCard rel={src.bom_relation!} />
      )}

      {!isBomEntity && !isBomRelation && (
        <>
          <p className={`text-[11px] text-slate-600 leading-relaxed whitespace-pre-wrap break-words ${expanded ? '' : 'line-clamp-4'}`}>
            {src.text}
          </p>
          {src.text.length > 160 && (
            <button
              onClick={(e) => { e.stopPropagation(); setExpanded((v) => !v) }}
              className={`mt-1 text-[11px] transition-colors ${t.expandBtn}`}
            >
              {expanded ? '收起 ▲' : '展开全文 ▼'}
            </button>
          )}
          {src.image_url && (
            <img
              src={src.image_url}
              alt="来源图片"
              className="mt-2 h-20 w-full object-cover rounded border border-slate-200 cursor-zoom-in"
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
              onClick={(e) => { e.stopPropagation(); window.open(src.image_url!, '_blank') }}
            />
          )}
        </>
      )}
    </div>
  )
}
