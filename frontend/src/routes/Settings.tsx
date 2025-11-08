import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { listMappings, updateMapping, getDropConfig, AttributeMapping } from '@api/settings'

type Weights = AttributeMapping['weights']
export default function Settings() {
  const qc = useQueryClient()
  const { data: mappings } = useQuery({ queryKey: ['mappings'], queryFn: listMappings })
  const { data: drop } = useQuery({ queryKey: ['drop'], queryFn: getDropConfig })
  const [drafts, setDrafts] = useState<Record<number, Weights>>({})
  useEffect(() => {
    if (mappings) {
      const next: Record<number, Weights> = {}
      for (const m of mappings) next[m.id] = { ...m.weights }
      setDrafts(next)
    }
  }, [mappings])
  const mut = useMutation({
    mutationFn: (payload: { id: number; weights: AttributeMapping['weights'] }) =>
      updateMapping(payload.id, payload.weights),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['mappings'] })
    },
  })
  return (
    <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="title">设置</div>
      <section>
        <div className="title" style={{ fontSize: 14, marginBottom: 8 }}>分类/全局 → 属性系数（方案B：各维独立，建议0–1，修改仅影响未来任务）</div>
        <div style={{ display: 'grid', gap: 8 }}>
          {mappings?.map(m => {
            const d = drafts[m.id] ?? m.weights
            const setVal = (key: keyof Weights, value: number) => {
              setDrafts(prev => ({ ...prev, [m.id]: { ...d, [key]: value } }))
            }
            const numInput = (label: string, key: keyof Weights) => (
              <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span className="muted" style={{ width: 36 }}>{label}</span>
                <input
                  className="input"
                  type="number"
                  min={0}
                  max={1}
                  step={0.1}
                  value={d[key]}
                  onChange={(e) => setVal(key, Number(e.target.value))}
                  style={{ width: 80, padding: '6px 8px' }}
                />
              </label>
            )
            return (
              <div key={m.id} style={{ display: 'grid', gridTemplateColumns: '180px 1fr max-content', gap: 12, alignItems: 'center' }}>
                <div className="muted">{m.label}</div>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                  {numInput('学习', 'learning')}
                  {numInput('体力', 'stamina')}
                  {numInput('魅力', 'charisma')}
                  {numInput('技艺', 'craft')}
                  {numInput('灵感', 'inspiration')}
                </div>
                <button className="btn" disabled={mut.isPending} onClick={() => mut.mutate({ id: m.id, weights: d })}>
                  {mut.isPending ? '保存中…' : '保存'}
                </button>
              </div>
            )
          })}
        </div>
      </section>
      <section>
        <div className="title" style={{ fontSize: 14, marginBottom: 8 }}>掉落节奏（只读）</div>
        <div className="muted">
          {drop?.bands?.map((b, i) => (
            <span key={i} style={{ marginRight: 12 }}>
              [{b.min}–{b.max}] → {Math.round(b.prob * 100)}%
            </span>
          ))}
        </div>
      </section>
    </div>
  )
}


