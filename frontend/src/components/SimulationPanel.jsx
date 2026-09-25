import React, { useEffect, useRef, useState } from 'react'
import { useSimulation } from '../hooks/useSimulation'
import { goToPoint } from '../api/fleetApi'

// Formação em L: 3 pontos, um por robô — o clássico "pixel voador" de show de
// drone, só que com 3 pontos em vez de milhares.
const PRESET_L = [[0, 0, 0], [0, 1.5, 0], [1.5, 1.5, 0]]
const sleep = (ms) => new Promise(r => setTimeout(r, ms))

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
  // Formação: 1 ponto (x,y,yaw) por robô, na mesma ordem de `robots` —
  // cada robô é "um pixel" da formação, ideia de show de drone com 2-3
  // robôs em vez de milhares.
  const [formation, setFormation] = useState(PRESET_L.slice(0, 2))
  const [dispatch, setDispatch] = useState({})  // robotId -> 'pending' | 'ok' | 'error: ...'
  const dispatchedRef = useRef(false)

  const toggleRobot = (id) => {
    setRobots(r => {
      const next = r.includes(id) ? r.filter(x => x !== id) : [...r, id]
      setFormation(f => next.map((_, i) => f[i] || PRESET_L[i] || [0, 0, 0]))
      return next
    })
  }

  const applyPresetL = () => setFormation(robots.map((_, i) => PRESET_L[i] || [0, 0, 0]))

  const setPoint = (i, axis, val) => {
    setFormation(f => f.map((p, pi) => pi === i ? [
      axis === 'x' ? parseFloat(val) || 0 : p[0],
      axis === 'y' ? parseFloat(val) || 0 : p[1],
      axis === 'yaw' ? parseFloat(val) || 0 : p[2],
    ] : p))
  }

  // Assim que a simulação fica pronta, manda cada robô pro seu ponto da
  // formação, em sequência (um de cada vez, com uma pequena pausa entre —
  // "mesmo que sequencial" é aceitável, não precisa ser simultâneo) — só
  // uma vez por sessão de simulação (dispatchedRef reseta quando ela para).
  useEffect(() => {
    if (!status.running) {
      dispatchedRef.current = false
      setDispatch({})
      return
    }
    if (mode !== 'multi' || !status.ready || dispatchedRef.current) return
    dispatchedRef.current = true

    ;(async () => {
      for (let i = 0; i < robots.length; i++) {
        const robotId = robots[i]
        const [x, y, yaw] = formation[i] || [0, 0, 0]
        setDispatch(d => ({ ...d, [robotId]: 'pending' }))
        try {
          await goToPoint({ robotId, x, y, yaw })
          setDispatch(d => ({ ...d, [robotId]: 'ok' }))
        } catch (e) {
          setDispatch(d => ({ ...d, [robotId]: `error: ${e.message}` }))
        }
        await sleep(1500)  // dá tempo do robô sair antes do próximo — mais fácil de ver na tela
      }
    })()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status.running, status.ready, mode])

  const badge = statusBadge(status)

  return (
    <div style={S.panel}>
      <div style={S.title}>Missão Coordenada — Planejar → Validar → Executar</div>

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

          {mode === 'multi' && status.ready && (
            <div>
              <span style={S.label}>Formação — dispatch</span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                {robots.map(id => {
                  const st = dispatch[id]
                  const color = st === 'ok' ? '#6ee7b7' : st === 'pending' ? '#fbbf24' : st?.startsWith('error') ? '#f87171' : '#4b5563'
                  const label = st === 'ok' ? '✓ chegou no ponto' : st === 'pending' ? '⏳ indo…' : st?.startsWith('error') ? `✗ ${st}` : '— aguardando'
                  return (
                    <div key={id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', fontFamily: 'monospace' }}>
                      <span style={{ color: '#a0aec0' }}>{id}</span>
                      <span style={{ color }}>{label}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

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

          {mode === 'multi' && robots.length >= 2 && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={S.label}>Formação — 1 ponto por robô</span>
                <button onClick={applyPresetL} style={{ background: 'none', border: 'none', color: '#6366f1', cursor: 'pointer', fontSize: '0.72rem', padding: 0 }}>
                  ⬛ Formação em L
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {robots.map((id, i) => {
                  const [x, y, yaw] = formation[i] || [0, 0, 0]
                  return (
                    <div key={id} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <span style={{ fontSize: '0.75rem', color: '#6366f1', width: '32px', fontFamily: 'monospace', fontWeight: 700 }}>{id}</span>
                      {[['x', x], ['y', y], ['yaw', yaw]].map(([axis, val]) => (
                        <div key={axis} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.1rem' }}>
                          <span style={{ fontSize: '0.6rem', color: '#4b5563' }}>{axis}</span>
                          <input type="number" step="0.1" value={val} onChange={e => setPoint(i, axis, e.target.value)}
                            style={{ ...S.select, width: '64px', padding: '0.25rem 0.3rem', textAlign: 'center' }} />
                        </div>
                      ))}
                    </div>
                  )
                })}
              </div>
              <div style={{ fontSize: '0.68rem', color: '#4b5563', marginTop: '0.3rem' }}>
                Assim que a simulação ficar pronta, cada robô vai pro seu ponto em sequência.
              </div>
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
