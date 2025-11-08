import React, { useEffect } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import TopbarUser from './components/TopbarUser'
import './styles/global.css'

export default function App() {
  const location = useLocation()
  const navigate = useNavigate()
  useEffect(() => {
    const token = sessionStorage.getItem('token')
    if (!token && location.pathname !== '/login') {
      navigate('/login', { replace: true })
    }
  }, [location.pathname, navigate])
  return (
    <div className="appRoot">
      <header className="topbar">
        <nav className="nav">
          <Link className={`navLink ${location.pathname === '/' ? 'active' : ''}`} to="/">仪表盘</Link>
          <Link className={`navLink ${location.pathname.startsWith('/tasks') ? 'active' : ''}`} to="/tasks">任务</Link>
          <Link className={`navLink ${location.pathname === '/backpack' ? 'active' : ''}`} to="/backpack">背包</Link>
          <Link className={`navLink ${location.pathname === '/settings' ? 'active' : ''}`} to="/settings">设置</Link>
        </nav>
        <TopbarUser />
      </header>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}


