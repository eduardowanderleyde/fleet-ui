import { useCallback, useEffect, useRef, useState } from 'react'
import { getSimulationOptions, getSimulationStatus, goToPoint, startSimulation, stopSimulation } from '../api/fleetApi'

const EMPTY_STATUS = { running: false, ready: false, mode: null, world: null, robots: [], lines: [], error: null }

// Formações: 1 ponto por robô, 3 robôs fixos — o clássico "pixel voador"
// de show de drone, só que com 3 pontos em vez de milhares.
export const SHAPES = {
  L:  { label: 'L',  points: [[0, 0, 0], [0, 1.5, 0], [1.5, 1.5, 0]] },
  I:  { label: 'I',  points: [[0, 0, 0], [0, 1.5, 0], [0, 3.0, 0]] },
  V:  { label: 'V',  points: [[0, 1.5, 0], [0.75, 0, 0], [1.5, 1.5, 0]] },
  '\\': { label: '\\', points: [[0, 0, 0], [0.75, -0.75, 0], [1.5, -1.5, 0]] },
}
export const ROBOTS = ['tb1', 'tb2', 'tb3']
const sleep = (ms) => new Promise(r => setTimeout(r, ms))

export function useSimulation(intervalMs = 2000) {
  const [options, setOptions] = useState({ worlds: [], robots: [] })
  const [status, setStatus] = useState(EMPTY_STATUS)
  const [actionError, setActionError] = useState(null)
  const [starting, setStarting] = useState(false)
  const [shape, setShape] = useState('L')
  const [dispatch, setDispatch] = useState({})  // robotId -> 'pending' | 'ok' | 'error: ...'
  const dispatchedRef = useRef(false)

  const points = SHAPES[shape].points

  // Assim que a simulação fica pronta, manda cada robô pro seu ponto da
  // formação, em sequência (um de cada vez, com uma pequena pausa entre —
  // não precisa ser simultâneo) — só uma vez por sessão de simulação
  // (dispatchedRef reseta quando ela para).
  useEffect(() => {
    if (!status.running) {
      dispatchedRef.current = false
      setDispatch({})
      return
    }
    if (!status.ready || dispatchedRef.current) return
    dispatchedRef.current = true
    const activeRobots = status.robots?.length ? status.robots : ROBOTS

    ;(async () => {
      for (let i = 0; i < activeRobots.length; i++) {
        const robotId = activeRobots[i]
        const [x, y, yaw] = points[i] || [0, 0, 0]
        setDispatch(d => ({ ...d, [robotId]: 'pending' }))
        try {
          const result = await goToPoint({ robotId, x, y, yaw })
          if (!result.success) throw new Error(result.message || 'falhou sem detalhe')
          setDispatch(d => ({ ...d, [robotId]: 'ok' }))
        } catch (e) {
          setDispatch(d => ({ ...d, [robotId]: `error: ${e.message}` }))
        }
        await sleep(1500)  // dá tempo do robô sair antes do próximo — mais fácil de ver na tela
      }
    })()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status.running, status.ready])

  useEffect(() => {
    getSimulationOptions().then(setOptions).catch(() => {})
  }, [])

  useEffect(() => {
    let alive = true
    const refresh = async () => {
      try {
        const data = await getSimulationStatus()
        if (alive && data) setStatus(data)
      } catch {
        // Backend pode estar offline; painel só mostra o último status conhecido.
      }
    }
    refresh()
    const timer = setInterval(refresh, intervalMs)
    return () => { alive = false; clearInterval(timer) }
  }, [intervalMs])

  const start = useCallback(async ({ mode, world, robots }) => {
    setActionError(null)
    setStarting(true)
    try {
      await startSimulation({ mode, world, robots })
      const data = await getSimulationStatus()
      setStatus(data)
    } catch (e) {
      setActionError(e.message)
    } finally {
      setStarting(false)
    }
  }, [])

  const stop = useCallback(async () => {
    setActionError(null)
    try {
      await stopSimulation()
      setStatus(EMPTY_STATUS)
    } catch (e) {
      setActionError(e.message)
    }
  }, [])

  return {
    options, status, actionError, starting, start, stop,
    shape, setShape, dispatch,
  }
}
