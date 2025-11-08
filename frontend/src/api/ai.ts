import api from './client'

export async function requestDecomposition(payload: { title: string }) {
  const { data } = await api.post('/ai/decompose', payload)
  return data as { subtasks: { title: string; estimate_seconds?: number }[], attribute_weights?: { learning: number; stamina: number; charisma: number; craft: number } }
}

export async function requestScore(payload: { title: string; subtasks: { title: string }[] }) {
  const { data } = await api.post('/ai/score', payload)
  return data as { score: number }
}

export async function requestNarrative(payload: { title: string }) {
  const { data } = await api.post('/ai/narrative', payload)
  return data as { narrative: string; attribute_weights?: { learning: number; stamina: number; charisma: number; craft: number; inspiration: number } }
}


