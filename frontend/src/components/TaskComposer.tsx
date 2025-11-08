import { useState } from 'react'
import { requestDecomposition, requestScore, requestNarrative } from '@api/ai'
import { createTask, addSubtask } from '@api/tasks'
import { useNavigate } from 'react-router-dom'

export default function TaskComposer() {
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [shouldDecompose, setShouldDecompose] = useState(true)
  const navigate = useNavigate()
  return (
    <div className="panel" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      <input className="input" placeholder="输入一个大任务标题" value={title} onChange={(e) => setTitle(e.target.value)} />
      <label className="muted" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <input type="checkbox" checked={shouldDecompose} onChange={(e) => setShouldDecompose(e.target.checked)} />
        拆解任务
      </label>
      <button className="btn" disabled={loading || !title.trim()} onClick={async () => {
        const t = title.trim()
        if (!t) return
        setLoading(true)
        try {
          if (shouldDecompose) {
            const dec = await requestDecomposition({ title: t })
            const score = await requestScore({ title: t, subtasks: dec.subtasks.map(s => ({ title: s.title })) })
            const task = await createTask({ title: t, suggested_score: score.score, attribute_weights: dec.attribute_weights })
            for (const st of dec.subtasks) {
              await addSubtask(task.id, { title: st.title, estimate_seconds: st.estimate_seconds })
            }
            navigate(`/tasks/${task.id}`)
          } else {
            const nar = await requestNarrative({ title: t })
            const score = await requestScore({ title: t, subtasks: [] })
            const task = await createTask({ title: t, suggested_score: score.score, attribute_weights: nar.attribute_weights, narrative: nar.narrative } as any)
            navigate(`/tasks/${task.id}`)
          }
        } catch (e) {
          try {
            const task = await createTask({ title: t })
            navigate(`/tasks/${task.id}`)
          } catch {}
        } finally {
          setLoading(false)
          setTitle('')
        }
      }}>{loading ? '生成中…' : '创建'}</button>
    </div>
  )
}



