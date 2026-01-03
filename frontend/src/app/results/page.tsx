'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { getStatus, type StatusResponse } from '@/lib/api'
import ProgressTracker from '@/components/ProgressTracker'
import ReportView from '@/components/ReportView'

export default function ResultsPage() {
  const params = useParams()
  const jobId = params.id as string

  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let interval: NodeJS.Timeout

    const checkStatus = async () => {
      try {
        const data = await getStatus(jobId)
        setStatus(data)

        // Stop polling if completed or error
        if (data.status === 'completed' || data.status === 'error') {
          if (interval) clearInterval(interval)
        }
      } catch (err) {
        setError('Failed to fetch status. Is the backend running?')
        console.error(err)
        if (interval) clearInterval(interval)
      }
    }

    // Initial check
    checkStatus()

    // Poll every 2 seconds
    interval = setInterval(checkStatus, 2000)

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [jobId])

  return (
    <main className="min-h-screen bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
            Research in Progress
          </h1>
          <p className="text-gray-600">
            Job ID: <code className="text-xs bg-gray-200 px-2 py-1 rounded">{jobId}</code>
          </p>
        </div>

        {/* Error State */}
        {error && (
          <div className="max-w-2xl mx-auto mb-6">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <h3 className="font-bold text-red-800 mb-2">Error</h3>
              <p className="text-red-600">{error}</p>
              <p className="text-sm text-red-500 mt-2">
                Make sure the backend is running on http://localhost:8000
              </p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {!status && !error && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">Loading...</p>
            </div>
          </div>
        )}

        {/* Processing State */}
        {status && status.status === 'processing' && (
          <div className="max-w-2xl mx-auto">
            <ProgressTracker 
              currentStep={status.progress || 'Starting'} 
              progress={status.progress}
            />
          </div>
        )}

        {/* Completed State */}
        {status && status.status === 'completed' && status.result && (
          <div className="max-w-4xl mx-auto">
            <ReportView
              report={status.result.report}
              sources={status.result.sources}
              insights={status.result.insights}
              query={status.result.query}
            />
          </div>
        )}

        {/* Error State from Backend */}
        {status && status.status === 'error' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <h3 className="font-bold text-red-800 mb-2">Research Failed</h3>
              <p className="text-red-600">{status.error || 'Unknown error occurred'}</p>
              
                href="/"
                className="inline-block mt-4 bg-red-600 text-white py-2 px-6 rounded-lg hover:bg-red-700 transition"
              <a>
                Try Again
              </a>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}