import XPBar from '@components/XPBar'
import Attributes from '@components/Attributes'
import TaskComposer from '@components/TaskComposer'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchMe } from '@api/auth'
import { createTask } from '@api/tasks'

export default function Dashboard() {
  const navigate = useNavigate()
  const { data: me } = useQuery({ queryKey: ['me'], queryFn: fetchMe })
  const mockLevel = me?.level ?? 1
  const mockXp = me?.xp ?? 0
  const mockAttrs = me?.attributes ?? { learning: 0, stamina: 0, charisma: 0, craft: 0, inspiration: 0 }

  return (
    <div className="stack" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <XPBar level={mockLevel} xp={mockXp} />
      <Attributes {...mockAttrs} />
      <TaskComposer />
    </div>
  )
}


