type Props = { level: number; xp: number }
export default function XPBar({ level, xp }: Props) {
  const pct = Math.max(0, Math.min(100, xp))
  return (
    <div className="panel" style={{ padding: 12 }}>
      <div className="row" style={{ marginBottom: 8 }}>
        <div className="title">等级 {level}</div>
        <div className="muted">经验 {xp}/100</div>
      </div>
      <div className="xpBar"><div className="xpFill" style={{ width: `${pct}%` }} /></div>
    </div>
  )
}



