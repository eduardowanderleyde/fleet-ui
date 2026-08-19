import { useCallback, useEffect, useState } from 'react'
import { listRoutes } from '../api/fleetApi'

export function useRoutes(robotId) {
  const [routes, setRoutes] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const refreshRoutes = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listRoutes(robotId)
      setRoutes(data.route_names || [])
    } catch (err) {
      setRoutes([])
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [robotId])

  useEffect(() => {
    refreshRoutes()
  }, [refreshRoutes])

  return { routes, loading, error, refreshRoutes }
}
