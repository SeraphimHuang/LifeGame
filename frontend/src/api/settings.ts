import api from './client'

export type AttributeMapping = { id: number; label: string; weights: { learning: number; stamina: number; charisma: number; craft: number } }
export async function listMappings() {
  const { data } = await api.get('/config/mapping/')
  return data as AttributeMapping[]
}

export async function updateMapping(id: number, weights: AttributeMapping['weights']) {
  const { data } = await api.put(`/config/mapping/${id}/`, { weights })
  return data as AttributeMapping
}

export type DropBand = { min: number; max: number; prob: number }
export async function getDropConfig() {
  const { data } = await api.get('/config/drop-config/')
  // use first one
  return (Array.isArray(data) && data.length > 0 ? data[0] : { bands: [] }) as { bands: DropBand[] }
}



