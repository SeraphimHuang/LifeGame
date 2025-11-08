import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loginApi } from '@api/auth'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const onSubmit = async () => {
    setError(null)
    try {
      const res = await loginApi({ username, password })
      sessionStorage.setItem('token', res.token)
      sessionStorage.setItem('display_name', res.user.display_name)
      if (res.user.avatar_url) sessionStorage.setItem('avatar_url', res.user.avatar_url)
      navigate('/')
    } catch (e) {
      setError('登录失败')
    }
  }
  return (
    <div style={{ display: 'grid', placeItems: 'center', minHeight: '80vh' }}>
      <div className="panel" style={{ width: 360, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div className="title">登录</div>
        <input className="input" placeholder="用户名" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input className="input" placeholder="密码" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <div className="muted">{error}</div>}
        <button className="btn" onClick={onSubmit}>进入</button>
      </div>
    </div>
  )
}


