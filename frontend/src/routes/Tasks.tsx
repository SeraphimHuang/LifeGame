import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listTasks } from '@api/tasks'

export default function Tasks() {
  const { data } = useQuery({ queryKey: ['tasks'], queryFn: listTasks })
  const rows = data ?? []
  return (
    <div className="stack" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {rows.map((r) => (
        <Link key={r.id} to={`/tasks/${r.id}`} className="listRow" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div>{r.title}</div>
          <div className="muted">{r.final_score}</div>
        </Link>
      ))}
    </div>
  )
}


