import QueryInput from '@/components/QueryInput'

export default function Home() {
  return (
    <main className="min-h-screen bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto px-4 py-12 md:py-20">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-semibold mb-6 shadow-lg">
            <span className="animate-pulse">⚡</span>
            <span>Powered by LangGraph + OpenRouter</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-linear-to-br from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
            InsightFlow
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto mb-4">
            AI Research Agent that delivers comprehensive reports in{' '}
            <span className="font-bold text-blue-600">10 minutes</span> instead of{' '}
            <span className="line-through text-gray-400">6 hours</span>
          </p>

          <div className="flex items-center justify-center gap-6 text-sm text-gray-600 mt-6">
            <div className="flex items-center gap-2">
              <span className="text-green-600">✓</span>
              <span>Multi-agent system</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-600">✓</span>
              <span>Real-time progress</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-600">✓</span>
              <span>Citations included</span>
            </div>
          </div>
        </div>

        {/* Query Input */}
        <QueryInput />

        {/* Stats */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="bg-white/50 backdrop-blur rounded-xl p-6 text-center border border-gray-200">
            <div className="text-3xl font-bold text-blue-600 mb-2">~10 min</div>
            <div className="text-sm text-gray-600">Average research time</div>
          </div>
          <div className="bg-white/50 backdrop-blur rounded-xl p-6 text-center border border-gray-200">
            <div className="text-3xl font-bold text-indigo-600 mb-2">$0.50-1</div>
            <div className="text-sm text-gray-600">Cost per report</div>
          </div>
          <div className="bg-white/50 backdrop-blur rounded-xl p-6 text-center border border-gray-200">
            <div className="text-3xl font-bold text-purple-600 mb-2">4 Agents</div>
            <div className="text-sm text-gray-600">Working in sequence</div>
          </div>
        </div>
      </div>
    </main>
  )
}