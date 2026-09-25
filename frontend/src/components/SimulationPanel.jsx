import React, { useEffect, useRef, useState } from 'react'
import { useSimulation } from '../hooks/useSimulation'
import { goToPoint } from '../api/fleetApi'

// Formações: 1 ponto por robô, até 3 — o clássico "pixel voador" de show de
// drone, só que com 2-3 pontos em vez de milhares.
const SHAPES = {
  L:         { label: 'L',         points: [[0, 0, 0], [0, 1.5, 0], [1.5, 1.5, 0]] },
  linha:     { label: 'Linha',     points: [[0, 0, 0], [1.5, 0, 0], [3.0, 0, 0]] },
  triangulo: { label: 'Triângulo', points: [[0, 0, 0], [1.5, 0, 0], [0.75, 1.3, 0]] },
}
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

const MODE = 'multi'
const WORLD = 'warehouse'
const ALL_ROBOTS = ['tb1', 'tb2', 'tb3']

export default function SimulationPanel() {
  const { status, actionError, starting, start, stop } = useSimulation()
  const [shape, setShape] = useState('L')
  const [robotCount, setRobotCount] = useState(2)
  const [dispatch, setDispatch] = useState({})  // robotId -> 'pending' | 'ok' | 'error: ...'
  const dispatchedRef = useRef(false)

  const robots = ALL_ROBOTS.slice(0, robotCount)
  const points = SHAPES[shape].points

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
    if (!status.ready || dispatchedRef.current) return
    dispatchedRef.current = true
    const activeRobots = status.robots?.length ? status.robots : robots

    ;(async () => {
      for (let i = 0; i < activeRobots.length; i++) {
        const robotId = activeRobots[i]
        const [x, y, yaw] = points[i] || [0, 0, 0]
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
  }, [status.running, status.ready])

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

          {status.ready && (
            <div>
              <span style={S.label}>Formação — dispatch</span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                {(status.robots?.length ? status.robots : robots).map(id => {
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
                3 robôs simultâneos tende a falhar ao subir a simulação nesta máquina (teto de CPU/DDS, já documentado) — o disparo da formação em si funciona igual, o risco é a simulação nem ficar pronta.
              </div>
            )}
          </div>

          <div style={{ fontSize: '0.75rem', color: '#a0aec0' }}>
            {robots.join(' + ')} · {WORLD} · formação {SHAPES[shape].label.toLowerCase()}
          </div>

          {actionError && <div style={{ fontSize: '0.78rem', color: '#f87171' }}>{actionError}</div>}

          <button
            onClick={() => start({ mode: MODE, world: WORLD, robots })}
            disabled={starting}
            style={{ ...btn('#065f46', '#6ee7b7', starting), alignSelf: 'flex-start' }}>
            {starting ? '⏳ Iniciando…' : `▶ Rodar simulação — ${SHAPES[shape].label}`}
          </button>
        </>
      )}
    </div>
  )
}
