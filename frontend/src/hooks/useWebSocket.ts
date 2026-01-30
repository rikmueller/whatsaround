import { useEffect, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'
import { JobStatus } from '../api'

export function useWebSocket(jobId: string | null, onJobUpdate: (job: JobStatus) => void) {
  const socketRef = useRef<Socket | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const socket = io('/', {
      path: '/socket.io',
      transports: ['polling'],  // Use polling only, more reliable with dev server
    })
    socketRef.current = socket

    socket.on('connect', () => setConnected(true))
    socket.on('disconnect', () => setConnected(false))

    socket.on('job_progress', (payload) => {
      if (payload && (!jobId || payload.id === jobId)) {
        onJobUpdate(payload as JobStatus)
      }
    })

    return () => {
      socket.disconnect()
    }
  }, [jobId, onJobUpdate])

  useEffect(() => {
    if (socketRef.current && jobId) {
      socketRef.current.emit('subscribe_job', { job_id: jobId })
    }
  }, [jobId])

  return { connected }
}
