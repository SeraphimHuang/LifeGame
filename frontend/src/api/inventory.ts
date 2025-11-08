import api from './client'

export type Item = { id: string; name: string; description: string; obtained_at: string; source_task: string }

export async function listItems() {
  const { data } = await api.get('/inventory/')
  return data as Item[]
}


