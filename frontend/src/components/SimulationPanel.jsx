import React from 'react'
import { SHAPES } from '../hooks/useSimulation'

const S = {
  panel: {
    // Fixo no canto superior direito da tela — longe do mapa (coluna
    // central), em vez de flutuar logo abaixo do botão "Simulação" e
    // cobrir parte dele.
    position: 'fixed', top: '3.2rem', right: '1rem', zIndex: 100,
    background: '#161a22', border: '1px solid #2a3142', borderRadius: '10px',
    padding: '1rem', width: '320px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.5)', display: 'flex', flexDirection: 'column', gap: '0.75rem',
  },
  title: { fontSize: '0.78rem', color: '#8b92a8', textTransform: 'uppercase', letterSpacing: '0.05em' },
  label: { fontSize: '0.72rem', color: '#8b92a8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem', display: 'block' },
}

function btn(bg, color, disabled = false) {
  return { background: bg, color, border: `1px solid ${color}`, borderRadius: '8px', padding: '0.45rem 0.9rem', fontSize: '0.85rem', fontWeight: 600, cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.55 : 1, fontFamily: 'inherit' }
}

function statusBadge(status) {
  if (status.error) return { label: '✗ erro no bringup', color: '#f87171' }
  if (status.running && status.ready) return { label: '✓ pronta', color: '#6ee7b7' }
  if (status.running) return { label: '⏳ subindo…', color: '#fbbf24' }
  return { label: 'parada', color: '#4b5563' }
}

const WORLD = 'warehouse'

// Painel puramente de configuração/controle — status detalhado e log ao
// vivo aparecem no painel "Output" existente (App.jsx), não aqui, pra não
// flutuar por cima do mapa.
export default function SimulationPanel({ sim }) {
  const { status, actionError, starting, start, stop, shape, setShape, robotCount, setRobotCount, robots } = sim
  const badge = statusBadge(status)

  return (
    <div style={S.panel}>
      <div style={S.title}>Missão Coordenada</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem' }}>
        <span style={{ color: badge.color, fontWeight: 600 }}>{badge.label}</span>
        {status.running && <span style={{ color: '#a0aec0' }}>· {(status.robots?.length ? status.robots : robots).join(', ')} · {status.world}</span>}
      </div>

      {status.running ? (
        <button onClick={stop} style={{ ...btn('#3a1a1a', '#f87171'), alignSelf: 'flex-start' }}>
          ■ Parar simulação
        </button>
      ) : (
        <>
          <div>
            <span style={S.label}>Formação</span>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              {Object.entries(SHAPES).map(([key, { label }]) => (
                <button key={key} onClick={() => setShape(key)}
                  style={{ ...btn(shape === key ? '#1e3a2f' : '#0d0f14', shape === key ? '#6ee7b7' : '#8b92a8'), flex: 1, fontSize: '0.78rem', padding: '0.35rem' }}>
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <span style={S.label}>Robôs</span>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              {[2, 3].map(n => (
                <button key={n} onClick={() => setRobotCount(n)}
                  style={{ ...btn(robotCount === n ? '#1e3a2f' : '#0d0f14', robotCount === n ? '#6ee7b7' : '#8b92a8'), flex: 1, fontSize: '0.78rem', padding: '0.35rem' }}>
                  {n}
                </button>
              ))}
            </div>
            {robotCount === 3 && (
              <div style={{ fontSize: '0.7rem', color: '#fbbf24', marginTop: '0.3rem' }}>
                3 robôs simultâneos tende a falhar ao subir a simulação nesta máquina (teto de CPU/DDS) — o disparo da formação funciona igual, o risco é a simulação não ficar pronta.
              </div>
            )}
          </div>

          <div style={{ fontSize: '0.75rem', color: '#a0aec0' }}>
            {robots.join(' + ')} · {WORLD} · formação {SHAPES[shape].label.toLowerCase()}
          </div>

          {actionError && <div style={{ fontSize: '0.78rem', color: '#f87171' }}>{actionError}</div>}

          <button
            onClick={() => start({ mode: 'multi', world: WORLD, robots })}
            disabled={starting}
            style={{ ...btn('#065f46', '#6ee7b7', starting), alignSelf: 'flex-start' }}>
            {starting ? '⏳ Iniciando…' : `▶ Rodar simulação — ${SHAPES[shape].label}`}
          </button>
        </>
      )}
    </div>
  )
}
