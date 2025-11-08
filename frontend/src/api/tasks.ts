import api from './client'

export type TaskRow = { id: string; title: string; final_score: number; status: 'todo' | 'doing' | 'done' }
export async function listTasks() {
  const { data } = await api.get('/tasks/')
  return data as TaskRow[]
}

export type TaskDetail = {
  id: string
  title: string
  status: 'todo' | 'doing' | 'done'
  suggested_score: number
  score_override: number | null
  final_score: number
  narrative?: string | null
  subtasks: { id: string; title: string; estimate_seconds: number | null; position: number; status: 'todo' | 'done' }[]
}
export async function getTask(id: string) {
  const { data } = await api.get(`/tasks/${id}/`)
  return data as TaskDetail
}

export async function createTask(payload: { title: string; suggested_score?: number; attribute_weights?: any }) {
  const { data } = await api.post('/tasks/', payload)
  return data as TaskDetail
}

export async function updateTask(id: string, payload: Partial<{ title: string; score_override: number | null; attribute_weights: any }>) {
  const { data } = await api.patch(`/tasks/${id}/`, payload)
  return data as TaskDetail
}

export async function startTask(id: string) {
  const { data } = await api.post(`/tasks/${id}/start/`)
  return data as TaskDetail
}

export async function completeTask(id: string) {
  const { data } = await api.post(`/tasks/${id}/complete/`)
  return data as {
    final_score: number
    dropped_item?: { id: string; name: string; description: string } | null
    level_ups: { id: string; level: number; title: string; content: string }[]
    new_profile: { level: number; xp: number; attributes: { learning: number; stamina: number; charisma: number; craft: number } }
  }
}

export async function addSubtask(taskId: string, payload: { title: string; estimate_seconds?: number }) {
  const { data } = await api.post(`/tasks/${taskId}/subtasks/`, payload)
  return data as { id: string }
}

export async function toggleSubtask(taskId: string, subtaskId: string) {
  const { data } = await api.post(`/tasks/${taskId}/subtasks/${subtaskId}/toggle/`)
  return data
}


