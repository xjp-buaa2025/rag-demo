// ============================================================
// KgViewer — 知识图谱 D3 力导向图可视化
//
// 功能：
//   - 从 GET /bom/kg/graph 加载节点和关系
//   - D3 force simulation 渲染交互式图谱
//   - 支持：拖拽节点、缩放平移、关键词搜索、点击高亮邻居
//   - 不同实体类型用不同颜色区分
// ============================================================

import { useEffect, useRef, useState, useCallback } from 'react'
import * as d3 from 'd3'
import { getKgGraph } from '../../api/client'
import type { KgNode } from '../../types'

// 实体类型 → 颜色映射
const TYPE_COLORS: Record<string, string> = {
  Part:          '#3b82f6', // blue
  Assembly:      '#22c55e', // green
  Procedure:     '#f97316', // orange
  Tool:          '#a855f7', // purple
  Specification: '#ef4444', // red
  Interface:     '#6b7280', // gray
  GeoConstraint: '#0f766e',
}
const DEFAULT_COLOR = '#94a3b8'

// 关系类型 → 颜色
const REL_COLORS: Record<string, string> = {
  CHILD_OF:       '#94a3b8',
  precedes:       '#f97316',
  participatesIn: '#3b82f6',
  requires:       '#a855f7',
  specifiedBy:    '#ef4444',
  matesWith:      '#22c55e',
  isPartOf:       '#6b7280',
  adjacentTo:     '#06b6d4',
  hasInterface:   '#8b5cf6',
  constrainedBy:  '#0f766e',
}
const DEFAULT_REL_COLOR = '#cbd5e1'

interface SimNode extends KgNode {
  x?: number
  y?: number
  fx?: number | null
  fy?: number | null
}

interface SimLink {
  source: string | SimNode
  target: string | SimNode
  type: string
}

export default function KgViewer() {
  const svgRef = useRef<SVGSVGElement>(null)
  const [keyword, setKeyword] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [nodeCount, setNodeCount] = useState(0)
  const [linkCount, setLinkCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const simulationRef = useRef<d3.Simulation<SimNode, SimLink> | null>(null)

  const loadAndRender = useCallback(async (kw: string) => {
    if (!svgRef.current) return
    setLoading(true)
    setError('')

    try {
      const data = await getKgGraph(kw || undefined, 200)
      if (data.error) {
        setError(data.error)
        setLoading(false)
        return
      }

      setNodeCount(data.nodes.length)
      setLinkCount(data.links.length)

      renderGraph(data.nodes as SimNode[], data.links as SimLink[])
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  const renderGraph = useCallback((nodes: SimNode[], links: SimLink[]) => {
    const svg = d3.select(svgRef.current!)
    svg.selectAll('*').remove()

    const width = svgRef.current!.clientWidth
    const height = svgRef.current!.clientHeight || 500

    // 缩放容器
    const g = svg.append('g')
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => g.attr('transform', event.transform))
    svg.call(zoom)

    // 箭头 marker
    const defs = svg.append('defs')
    Object.entries(REL_COLORS).forEach(([type, color]) => {
      defs.append('marker')
        .attr('id', `arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', color)
    })
    defs.append('marker')
      .attr('id', 'arrow-default')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', DEFAULT_REL_COLOR)

    // Force simulation
    const simulation = d3.forceSimulation<SimNode>(nodes)
      .force('link', d3.forceLink<SimNode, SimLink>(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30))

    simulationRef.current = simulation

    // 边
    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', d => REL_COLORS[d.type] || DEFAULT_REL_COLOR)
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', d => `url(#arrow-${REL_COLORS[d.type] ? d.type : 'default'})`)

    // 边标签
    const linkLabel = g.append('g')
      .selectAll('text')
      .data(links)
      .join('text')
      .attr('text-anchor', 'middle')
      .attr('font-size', '9px')
      .attr('fill', '#94a3b8')
      .attr('pointer-events', 'none')
      .text(d => d.type)

    // 节点组
    const node = g.append('g')
      .selectAll<SVGGElement, SimNode>('g')
      .data(nodes)
      .join('g')
      .style('cursor', 'pointer')
      .call(
        d3.drag<SVGGElement, SimNode>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on('drag', (event, d) => {
            d.fx = event.x
            d.fy = event.y
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
          })
      )

    // 节点圆圈
    node.append('circle')
      .attr('r', 10)
      .attr('fill', d => TYPE_COLORS[d.type] || DEFAULT_COLOR)
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)

    // 节点标签
    node.append('text')
      .attr('dx', 14)
      .attr('dy', 4)
      .attr('font-size', '11px')
      .attr('fill', '#334155')
      .text(d => {
        const label = d.label || ''
        return label.length > 12 ? label.slice(0, 12) + '…' : label
      })

    // Tooltip
    node.append('title')
      .text(d => {
        const parts = [`${d.type}: ${d.label}`]
        if (d.part_id) parts.push(`ID: ${d.part_id as string}`)
        if (d.material) parts.push(`材料: ${d.material as string}`)
        if (d.spec) parts.push(`规格: ${d.spec as string}`)
        if (d.ata_section) parts.push(`ATA: ${d.ata_section as string}`)
        return parts.join('\n')
      })

    // 点击高亮邻居
    const neighborSet = new Map<string, Set<string>>()
    links.forEach(l => {
      const sId = typeof l.source === 'string' ? l.source : (l.source as SimNode).id
      const tId = typeof l.target === 'string' ? l.target : (l.target as SimNode).id
      if (!neighborSet.has(sId)) neighborSet.set(sId, new Set())
      if (!neighborSet.has(tId)) neighborSet.set(tId, new Set())
      neighborSet.get(sId)!.add(tId)
      neighborSet.get(tId)!.add(sId)
    })

    node.on('click', (_, d) => {
      const neighbors = neighborSet.get(d.id) || new Set()
      const isSelected = selectedNode === d.id

      if (isSelected) {
        // 取消高亮
        node.select('circle').attr('opacity', 1)
        node.select('text').attr('opacity', 1)
        link.attr('stroke-opacity', 0.6)
        linkLabel.attr('opacity', 1)
        setSelectedNode(null)
      } else {
        // 高亮邻居
        node.select('circle').attr('opacity', n => n.id === d.id || neighbors.has(n.id) ? 1 : 0.15)
        node.select('text').attr('opacity', n => n.id === d.id || neighbors.has(n.id) ? 1 : 0.15)
        link.attr('stroke-opacity', l => {
          const sId = typeof l.source === 'string' ? l.source : (l.source as SimNode).id
          const tId = typeof l.target === 'string' ? l.target : (l.target as SimNode).id
          return sId === d.id || tId === d.id ? 0.8 : 0.05
        })
        linkLabel.attr('opacity', l => {
          const sId = typeof l.source === 'string' ? l.source : (l.source as SimNode).id
          const tId = typeof l.target === 'string' ? l.target : (l.target as SimNode).id
          return sId === d.id || tId === d.id ? 1 : 0.05
        })
        setSelectedNode(d.id)
      }
    })

    // 点击空白区域取消高亮
    svg.on('click', (event) => {
      if (event.target === svgRef.current) {
        node.select('circle').attr('opacity', 1)
        node.select('text').attr('opacity', 1)
        link.attr('stroke-opacity', 0.6)
        linkLabel.attr('opacity', 1)
        setSelectedNode(null)
      }
    })

    // Tick 更新位置
    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as SimNode).x!)
        .attr('y1', d => (d.source as SimNode).y!)
        .attr('x2', d => (d.target as SimNode).x!)
        .attr('y2', d => (d.target as SimNode).y!)

      linkLabel
        .attr('x', d => ((d.source as SimNode).x! + (d.target as SimNode).x!) / 2)
        .attr('y', d => ((d.source as SimNode).y! + (d.target as SimNode).y!) / 2)

      node.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    // 初始缩放以适应内容
    simulation.on('end', () => {
      if (nodes.length === 0) return
      const xs = nodes.map(n => n.x ?? 0)
      const ys = nodes.map(n => n.y ?? 0)
      const x0 = Math.min(...xs) - 50
      const y0 = Math.min(...ys) - 50
      const x1 = Math.max(...xs) + 50
      const y1 = Math.max(...ys) + 50
      const bw = x1 - x0
      const bh = y1 - y0
      const scale = Math.min(width / bw, height / bh, 1.5) * 0.9
      const tx = (width - bw * scale) / 2 - x0 * scale
      const ty = (height - bh * scale) / 2 - y0 * scale
      svg.transition().duration(500).call(
        zoom.transform,
        d3.zoomIdentity.translate(tx, ty).scale(scale)
      )
    })
  }, [selectedNode])

  // 初始加载
  useEffect(() => {
    loadAndRender(keyword)
    return () => { simulationRef.current?.stop() }
  }, [keyword, loadAndRender])

  const handleSearch = () => {
    setKeyword(searchInput.trim())
  }

  // 图例数据
  const legend = Object.entries(TYPE_COLORS)

  return (
    <div className="space-y-3">
      {/* 搜索栏 + 统计 */}
      <div className="flex items-center gap-3">
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSearch() }}
          placeholder="输入关键词过滤图谱（留空显示全图）…"
          className="flex-1 text-sm border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {loading ? '加载中…' : '搜索'}
        </button>
        <button
          onClick={() => { setSearchInput(''); setKeyword('') }}
          className="px-3 py-1.5 text-sm border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
        >
          重置
        </button>
        <span className="text-xs text-slate-400">
          节点 {nodeCount} / 边 {linkCount}
        </span>
      </div>

      {/* 图例 */}
      <div className="flex flex-wrap gap-3 text-xs">
        {legend.map(([type, color]) => (
          <span key={type} className="flex items-center gap-1">
            <span className="inline-block w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            {type}
          </span>
        ))}
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="text-sm text-red-500 bg-red-50 border border-red-200 rounded-md p-2">
          {error}
        </div>
      )}

      {/* 空状态 */}
      {!loading && !error && nodeCount === 0 && (
        <div className="text-center text-slate-400 text-sm py-12 bg-white rounded-lg border border-slate-200">
          <p className="text-2xl mb-2">🕸️</p>
          <p>暂无图谱数据，请先在「图谱构建」面板上传文件</p>
        </div>
      )}

      {/* SVG 画布 */}
      <div className={`bg-white rounded-lg border border-slate-200 overflow-hidden ${nodeCount === 0 && !loading ? 'hidden' : ''}`}>
        <svg
          ref={svgRef}
          width="100%"
          height="500"
          className="block"
        />
      </div>
    </div>
  )
}
