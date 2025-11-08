import api from './client'

export async function loginApi(params: { username: string; password: string }) {
  const { data } = await api.post('/auth/login', params)
  return data as { token: string; user: { username: string; display_name: string; avatar_url?: string | null } }
}

export async function fetchMe() {
  const { data } = await api.get('/auth/me')
  return data as {
    user: { id: number; username: string }
    display_name: string
    avatar_url?: string | null
    level: number
    xp: number
    attributes: { learning: number; stamina: number; charisma: number; craft: number; inspiration: number }
  }
}



