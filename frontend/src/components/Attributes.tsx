type Props = { learning: number; stamina: number; charisma: number; craft: number; inspiration: number }
export default function Attributes({ learning, stamina, charisma, craft, inspiration }: Props) {
  const items = [
    { label: '学习', value: learning },
    { label: '体力', value: stamina },
    { label: '魅力', value: charisma },
    { label: '技艺', value: craft },
    { label: '灵感', value: inspiration },
  ]
  return (
    <div className="attrs">
      {items.map((it) => (
        <div key={it.label} className="attrCard">
          <div className="attrLabel">{it.label}</div>
          <div className="title">{Number(it.value).toFixed(1)}</div>
        </div>
      ))}
    </div>
  )
}



