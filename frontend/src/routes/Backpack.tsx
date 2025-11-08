import { useQuery } from '@tanstack/react-query'
import { listItems } from '@api/inventory'

export default function Backpack() {
  const { data } = useQuery({ queryKey: ['inventory'], queryFn: listItems })
  const items = data ?? []
  return (
    <div className="grid" style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))' }}>
      {items.length === 0 ? (
        <div className="muted">当前没有物品。完成大任务有机会获得一件奇妙物品。</div>
      ) : (
        items.map((it) => (
          <div key={it.id} className="panel">
            <div className="title" style={{ marginBottom: 6 }}>{it.name}</div>
            <div className="muted">{it.description}</div>
          </div>
        ))
      )}
    </div>
  )
}



