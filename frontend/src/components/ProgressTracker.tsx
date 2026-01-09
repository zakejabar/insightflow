'use client'

interface Step {
  name: string
  icon: string
  description: string
}

interface ProgressTrackerProps {
  currentStep: string
  progress?: string
}

const steps: Step[] = [
  {
    name: 'Planning',
    icon: '🎯',
    description: 'Breaking down your query into sub-questions'
  },
  {
    name: 'Gathering',
    icon: '🔍',
    description: 'Searching sources and collecting information'
  },
  {
    name: 'Analyzing',
    icon: '🧠',
    description: 'Extracting insights and identifying patterns'
  },
  {
    name: 'Reporting',
    icon: '✍️',
    description: 'Generating structured report with citations'
  }
]

export default function ProgressTracker({ currentStep, progress }: ProgressTrackerProps) {
  // Match EXACT step names from backend
  const getCurrentStepIndex = () => {
    // Normalize the step name
    const step = (currentStep || '').toLowerCase().trim()
    
    // Match exact backend step names
    if (step === 'planning') return 0
    if (step === 'gathering') return 1
    if (step === 'analyzing') return 2
    if (step === 'reporting') return 3
    if (step === 'complete') return 4
    
    // Fallback: try to match keywords (only if exact match fails)
    if (step.includes('plan')) return 0
    if (step.includes('gather') || step.includes('search')) return 1
    if (step.includes('analyze')) return 2
    if (step.includes('report') || step.includes('generat')) return 3
    
    return 0  // Default to first step
  }

  const currentIndex = getCurrentStepIndex()

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-100">
      <h2 className="text-xl font-bold text-gray-800 mb-6">Research Progress</h2>

      <div className="space-y-4">
        {steps.map((step, index) => {
          const isCompleted = index < currentIndex
          const isCurrent = index === currentIndex
          const isPending = index > currentIndex

          return (
            <div key={index} className="flex items-start gap-4">
              {/* Icon */}
              <div className={`shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl transition ${
                isCompleted ? 'bg-green-100' :
                isCurrent ? 'bg-blue-100 animate-pulse' :
                'bg-gray-100 opacity-50'
              }`}>
                {isCompleted ? '✓' : step.icon}
              </div>

              {/* Content */}
              <div className="flex-1 pt-2">
                <div className="flex items-center gap-2">
                  <h3 className={`font-semibold ${
                    isCompleted ? 'text-green-600' :
                    isCurrent ? 'text-blue-600' :
                    'text-gray-400'
                  }`}>
                    {step.name}
                  </h3>
                  {isCurrent && (
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  )}
                </div>
                <p className={`text-sm mt-1 ${
                  isCompleted ? 'text-gray-600' :
                  isCurrent ? 'text-gray-700' :
                  'text-gray-400'
                }`}>
                  {step.description}
                </p>

                {/* Current progress detail */}
                {isCurrent && progress && (
                  <div className="mt-2 text-xs text-blue-600 bg-blue-50 px-3 py-1 rounded-lg inline-block">
                    {progress}
                  </div>
                )}

                {isCompleted && (
                  <div className="mt-2 text-xs text-green-600">
                    ✓ Complete
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Overall Progress Bar */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Overall Progress</span>
          <span>{Math.round((currentIndex / steps.length) * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-linear-to-br from-blue-600 to-indigo-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${(currentIndex / steps.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}