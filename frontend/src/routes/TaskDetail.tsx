import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTask, toggleSubtask, completeTask, updateTask } from '@api/tasks'

export default function TaskDetail() {
  const { id } = useParams()
  const queryClient = useQueryClient()
  const { data } = useQuery({ queryKey: ['task', id], queryFn: () => getTask(id!), enabled: !!id })
  const mutToggle = useMutation({
    mutationFn: (subtaskId: string) => toggleSubtask(id!, subtaskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', id] })
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    }
  })
  const mutComplete = useMutation({
    mutationFn: () => completeTask(id!),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['task', id] })
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      const lines = [
        `结算分数：${res.final_score}`,
        res.dropped_item ? `掉落：${res.dropped_item.name} - ${res.dropped_item.description}` : '无掉落',
        res.level_ups.length ? `升级到${res.level_ups[res.level_ups.length - 1].level}级` : '',
      ].filter(Boolean)
      alert(lines.join('\n'))
    }
  })
  const mutSaveScore = useMutation({
    mutationFn: (score_override: number | null) => updateTask(id!, { score_override }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', id] })
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    }
  })
  const mutSaveWeights = useMutation({
    mutationFn: (attribute_weights: any) => updateTask(id!, { attribute_weights }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', id] })
    }
  })
  return (
    <div className="panel">
      <div className="title" style={{ marginBottom: 12 }}>{data?.title ?? '任务详情'}</div>
      {data?.narrative ? (
        <div className="panel" style={{ marginBottom: 12, background: '#101522' }}>
          <div className="muted">鼓励文案</div>
          <div style={{ marginTop: 6 }}>{data.narrative}</div>
        </div>
      ) : null}
      <div className="panel" style={{ marginBottom: 12 }}>
        <div className="row" style={{ gap: 12, alignItems: 'center' }}>
          <span className="muted">建议分</span>
          <span className="title">{data?.suggested_score ?? 5}</span>
          <span className="muted">最终分</span>
          <span className="title">{data?.score_override ?? data?.suggested_score ?? 5}</span>
          <div style={{ display: 'flex', gap: 8, marginLeft: 'auto' }}>
            <button className="btn" onClick={() => {
              const base = data?.suggested_score ?? 5
              const cur = data?.score_override ?? base
              const next = Math.max(0, Math.min(50, cur - 1))
              mutSaveScore.mutate(next)
            }}>-</button>
            <button className="btn" onClick={() => {
              const base = data?.suggested_score ?? 5
              const cur = data?.score_override ?? base
              const next = Math.max(0, Math.min(50, cur + 1))
              mutSaveScore.mutate(next)
            }}>+</button>
            <button className="btn" onClick={() => mutSaveScore.mutate(null)}>重置</button>
          </div>
        </div>
      </div>
      <div className="panel" style={{ marginBottom: 12 }}>
        <div className="title" style={{ fontSize: 14, marginBottom: 8 }}>本次属性权重（0–1，留空则使用AI推断）</div>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          {['learning','stamina','charisma','craft','inspiration'].map((k) => {
            const cur = (data?.attribute_weights as any)?.[k]
            return (
              <label key={k} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span className="muted" style={{ width: 54 }}>
                  {k==='learning'?'学习':k==='stamina'?'体力':k==='charisma'?'魅力':k==='craft'?'技艺':'灵感'}
                </span>
                <input
                  className="input"
                  type="number"
                  min={0}
                  max={1}
                  step={0.1}
                  value={cur ?? ''}
                  placeholder="AI"
                  onChange={(e) => {
                    const val = e.target.value
                    const next = { ...(data?.attribute_weights || {}) }
                    if (val === '') {
                      delete (next as any)[k]
                    } else {
                      (next as any)[k] = Math.max(0, Math.min(1, Number(val)))
                    }
                    mutSaveWeights.mutate(next)
                  }}
                  style={{ width: 90, padding: '6px 8px' }}
                />
              </label>
            )
          })}
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {data?.subtasks?.map(st => (
          <label key={st.id} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <input type="checkbox" checked={st.status === 'done'} onChange={() => mutToggle.mutate(st.id)} />
            <span>{st.title} {st.estimate_seconds ? <span className="muted">（≈{st.estimate_seconds >= 60 ? `${Math.round(st.estimate_seconds/60)}分钟` : `${st.estimate_seconds}秒`}）</span> : null}</span>
          </label>
        ))}
      </div>
      <div style={{ marginTop: 16 }}>
        <button className="btn" onClick={() => mutComplete.mutate()}>完成大任务</button>
      </div>
    </div>
  )
}


