import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchMe } from '@api/auth'

export default function TopbarUser() {
  const [token] = useState<string | null>(sessionStorage.getItem('token'))
  const { data } = useQuery({
    queryKey: ['me', token],
    queryFn: fetchMe,
    enabled: !!token,
    staleTime: 60_000,
  })
  const name = data?.display_name ?? sessionStorage.getItem('display_name') ?? '角色名'
  const avatarUrl = data?.avatar_url ?? sessionStorage.getItem('avatar_url')

  useEffect(() => {}, [data])

  return (
    <div className="topbarUser">
      <img className="avatar" src={avatarUrl ?? 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=='} alt="avatar" />
      <span>{name}</span>
    </div>
  )
}


