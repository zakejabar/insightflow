'use client'

import { useEffect, useRef } from 'react'

interface ProgressTrackerProps {
  currentStep: string
  progress?: string
  logs?: string[]
}

const steps = [
  { id: 'planning', name: 'Planner', icon: '🎯' },
  { id: 'gathering', name: 'Gatherer', icon: '🔍' },
  { id: 'analyzing', name: 'Analyst', icon: '🧠' },
  { id: 'reporting', name: 'Writer', icon: '✍️' }
]

export default function ProgressTracker({ currentStep, progress, logs = [] }: ProgressTrackerProps) {
  const terminalRef = useRef<HTMLDivElement>(null)

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [logs])

  const getCurrentStepId = () => {
    const s = (currentStep || '').toLowerCase()
    if (s.includes('plan')) return 'planning'
    if (s.includes('gather') || s.includes('search')) return 'gathering'
    if (s.includes('analyze')) return 'analyzing'
    if (s.includes('report') || s.includes('generat')) return 'reporting'
    return 'complete'
  }

  const activeStepId = getCurrentStepId()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-5xl mx-auto animate-in fade-in zoom-in-95 duration-500">

      {/* LEFT: Agent Mesh (Core) */}
      <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 flex flex-col justify-between h-[400px]">
        <div>
          <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            Active Agents
          </h2>

          <div className="grid grid-cols-2 gap-4">
            {steps.map((step) => {
              const isActive = activeStepId === step.id
              const isPast = steps.findIndex(s => s.id === step.id) < steps.findIndex(s => s.id === activeStepId)

              return (
                <div
                  key={step.id}
                  className={`relative p-4 rounded-xl border-2 transition-all duration-300 ${isActive
                    ? 'border-blue-500 bg-blue-50 shadow-lg scale-105'
                    : isPast
                      ? 'border-green-200 bg-white opacity-50'
                      : 'border-gray-100 bg-gray-50 opacity-40'
                    }`}
                >
                  <div className="text-3xl mb-2">{step.icon}</div>
                  <div className="font-semibold text-gray-800">{step.name}</div>
                  {isActive && (
                    <div className="absolute top-2 right-2">
                      <span className="flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
                      </span>
                    </div>
                  )}
                  {isActive && (
                    <div className="mt-2 text-xs text-blue-600 font-mono">
                      {progress || 'Processing...'}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        <div className="text-xs text-gray-400 text-center font-mono mt-4">
          INSIGHTFLOW CORTEX v2.0
        </div>
      </div>

      {/* RIGHT: Neural Stream (Thought Logs) */}
      <div className="bg-gray-900 rounded-2xl shadow-2xl p-6 border border-gray-800 h-[400px] flex flex-col">
        <h2 className="text-sm font-mono text-gray-400 mb-4 flex justify-between items-center border-b border-gray-800 pb-2">
          <span>&gt;_ NEURAL_STREAM</span>
          <span className="flex gap-1">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <div className="w-2 h-2 rounded-full bg-yellow-500" />
            <div className="w-2 h-2 rounded-full bg-green-500" />
          </span>
        </h2>

        <div
          ref={terminalRef}
          className="flex-1 overflow-y-auto font-mono text-xs space-y-2 pr-2 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent"
        >
          {logs.length === 0 && (
            <div className="text-gray-600 italic">Waiting for input...</div>
          )}

          {logs.map((log, i) => (
            <div key={i} className="animate-in slide-in-from-left-2 duration-300">
              <span className="text-gray-500 mr-2">[{new Date().toLocaleTimeString()}]</span>
              <span className={`${log.includes('❌') ? 'text-red-400' :
                log.includes('✅') ? 'text-green-400' :
                  log.includes('🎓') ? 'text-purple-400' :
                    log.includes('🤖') ? 'text-blue-400' :
                      'text-gray-300'
                }`}>
                {log}
              </span>
            </div>
          ))}

          <div className="h-4 w-2 bg-gray-500 animate-pulse mt-2" />
        </div>
      </div>
    </div>
  )
}