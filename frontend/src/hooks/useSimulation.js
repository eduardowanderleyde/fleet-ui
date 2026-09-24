import { useCallback, useEffect, useState } from 'react'
import { getSimulationOptions, getSimulationStatus, startSimulation, stopSimulation } from '../api/fleetApi'

const EMPTY_STATUS = { running: false, ready: false, mode: null, world: null, robots: [], lines: [], error: null }

export function useSimulation(intervalMs = 2000) {
  const [options, setOptions] = useState({ worlds: [], robots: [] })
  const [status, setStatus] = useState(EMPTY_STATUS)
  const [actionError, setActionError] = useState(null)
  const [starting, setStarting] = useState(false)

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

  return { options, status, actionError, starting, start, stop }
}
