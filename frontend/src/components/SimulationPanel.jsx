import React, { useState } from 'react'
import { useSimulation } from '../hooks/useSimulation'

const S = {
  panel: {
    position: 'absolute', top: '2.5rem', left: 0, zIndex: 100,
    background: '#161a22', border: '1px solid #2a3142', borderRadius: '10px',
    padding: '1rem', width: '420px', maxHeight: '70vh', overflowY: 'auto',
    boxShadow: '0 8px 32px rgba(0,0,0,0.5)', display: 'flex', flexDirection: 'column', gap: '0.75rem',
  },
  title:  { fontSize: '0.78rem', color: '#8b92a8', textTransform: 'uppercase', letterSpacing: '0.05em' },
  label:  { fontSize: '0.72rem', color: '#8b92a8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem', display: 'block' },
  select: { background: '#0d0f14', border: '1px solid #2a3142', borderRadius: '6px', color: '#e6e9ef', padding: '0.4rem 0.6rem', fontSize: '0.85rem', outline: 'none', width: '100%', boxSizing: 'border-box' },
  row:    { display: 'flex', gap: '0.6rem' },
  field:  { display: 'flex', flexDirection: 'column', flex: 1 },
  log:    { background: '#0d0f14', border: '1px solid #2a3142', borderRadius: '6px', padding: '0.5rem 0.6rem', fontSize: '0.7rem', fontFamily: 'monospace', color: '#8b92a8', maxHeight: '160px', overflowY: 'auto', whiteSpace: 'pre-wrap' },
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

export default function SimulationPanel() {
  const { options, status, actionError, starting, start, stop } = useSimulation()
  const [mode, setMode] = useState('single')
  const [world, setWorld] = useState('warehouse')
  const [robots, setRobots] = useState(['tb1', 'tb2'])

  const toggleRobot = (id) => {
    setRobots(r => r.includes(id) ? r.filter(x => x !== id) : [...r, id])
  }

  const badge = statusBadge(status)

  return (
    <div style={S.panel}>
      <div style={S.title}>Simulação (Gazebo + Nav2 + frota)</div>

      {status.running ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', fontSize: '0.82rem' }}>
            <span style={{ color: badge.color, fontWeight: 600 }}>{badge.label}</span>
            <span style={{ color: '#4b5563' }}>·</span>
            <span style={{ color: '#a0aec0' }}>{status.mode === 'multi' ? status.robots.join(', ') : 'single-robot'}</span>
            <span style={{ color: '#4b5563' }}>·</span>
            <span style={{ color: '#a0aec0' }}>{status.world}</span>
          </div>
          {status.error && <div style={{ fontSize: '0.75rem', color: '#f87171' }}>{status.error}</div>}
          <div style={S.log}>
            {status.lines.slice(-15).map((l, i) => <div key={i}>{l}</div>)}
          </div>
          <button onClick={stop} style={{ ...btn('#3a1a1a', '#f87171'), alignSelf: 'flex-start' }}>
            ■ Parar simulação
          </button>
        </div>
      ) : (
        <>
          <div style={S.row}>
            <div style={S.field}>
              <span style={S.label}>Mapa</span>
              <select value={world} onChange={e => setWorld(e.target.value)} style={S.select}>
                {(options.worlds.length ? options.worlds : ['warehouse', 'depot']).map(w => (
                  <option key={w} value={w}>{w}</option>
                ))}
              </select>
            </div>
            <div style={S.field}>
              <span style={S.label}>Modo</span>
              <select value={mode} onChange={e => setMode(e.target.value)} style={S.select}>
                <option value="single">1 robô (sem namespace)</option>
                <option value="multi">Múltiplos robôs</option>
              </select>
            </div>
          </div>

          {mode === 'multi' && (
            <div>
              <span style={S.label}>Robôs</span>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {(options.robots.length ? options.robots : ['tb1', 'tb2', 'tb3']).map(id => (
                  <label key={id} style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', cursor: 'pointer',
                    background: robots.includes(id) ? 'rgba(99,102,241,0.12)' : 'transparent',
                    border: `1px solid ${robots.includes(id) ? '#6366f1' : '#2a3142'}`,
                    borderRadius: '6px', padding: '0.3rem 0.65rem' }}>
                    <input type="checkbox" checked={robots.includes(id)} onChange={() => toggleRobot(id)} style={{ accentColor: '#6366f1', margin: 0 }} />
                    <span style={{ fontSize: '0.82rem', color: robots.includes(id) ? '#e6e9ef' : '#8b92a8', fontFamily: 'monospace' }}>{id}</span>
                  </label>
                ))}
              </div>
              {robots.length < 2 && (
                <div style={{ fontSize: '0.72rem', color: '#fbbf24', marginTop: '0.3rem' }}>
                  3 robôs simultâneos é instável nesta máquina (teto de CPU) — 2 é o validado.
                </div>
              )}
            </div>
          )}

          {actionError && <div style={{ fontSize: '0.78rem', color: '#f87171' }}>{actionError}</div>}

          <button
            onClick={() => start({ mode, world, robots })}
            disabled={starting || (mode === 'multi' && robots.length === 0)}
            style={{ ...btn('#065f46', '#6ee7b7', starting || (mode === 'multi' && robots.length === 0)), alignSelf: 'flex-start' }}>
            {starting ? '⏳ Iniciando…' : '▶ Iniciar simulação'}
          </button>
        </>
      )}
    </div>
  )
}
