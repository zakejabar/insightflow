'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { startResearch } from '@/lib/api'

export default function QueryInput() {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Phase 3: Academic Filters
  const [searchMode, setSearchMode] = useState<'web' | 'academic'>('web')
  const [minCitations, setMinCitations] = useState(0)
  const [openAccess, setOpenAccess] = useState(false)

  const exampleQueries = [
    "Analyze Indonesian e-wallet market: GoPay vs OVO vs Dana",
    "Top YC AI companies: business models and funding rounds",
    "Latest research on digital transformation in Indonesian SMEs",
    "Compare React vs Vue for enterprise applications",
  ]

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please enter a query')
      return
    }

    setLoading(true)
    setError('')

    try {
      const result = await startResearch(query, searchMode, minCitations, openAccess)
      // Navigate to results page with job_id
      router.push(`/results/${result.job_id}`)
    } catch (err) {
      setError('Failed to start research. Is the backend running?')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.metaKey) {
      handleSubmit()
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Main Input Card */}
      <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-100">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What do you want to research?
        </label>

        {/* Mode Toggle */}
        <div className="flex bg-gray-100 p-1 rounded-lg w-fit mb-4">
          <button
            onClick={() => setSearchMode('web')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${searchMode === 'web'
                ? 'bg-white text-blue-600 shadow-xs'
                : 'text-gray-500 hover:text-gray-700'
              }`}
          >
            🌍 Web Search
          </button>
          <button
            onClick={() => setSearchMode('academic')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${searchMode === 'academic'
                ? 'bg-white text-purple-600 shadow-xs'
                : 'text-gray-500 hover:text-gray-700'
              }`}
          >
            🎓 Academic
          </button>
        </div>

        {/* Academic Filters */}
        {searchMode === 'academic' && (
          <div className="mb-4 p-4 bg-purple-50 rounded-xl border border-purple-100 flex flex-wrap gap-4 items-center animate-in fade-in slide-in-from-top-2">
            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-purple-700 uppercase tracking-wide">Min Citations</label>
              <select
                value={minCitations}
                onChange={(e) => setMinCitations(Number(e.target.value))}
                className="bg-white border border-purple-200 text-gray-700 text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block p-2"
              >
                <option value="0">Any Impact</option>
                <option value="10">⭐ &gt; 10 Citations</option>
                <option value="50">⭐⭐ &gt; 50 Citations</option>
                <option value="100">⭐⭐⭐ &gt; 100 Citations</option>
                <option value="500">⭐⭐⭐⭐⭐ &gt; 500 Citations</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-purple-700 uppercase tracking-wide">License</label>
              <label className="inline-flex items-center bg-white border border-purple-200 rounded-lg p-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={openAccess}
                  onChange={(e) => setOpenAccess(e.target.checked)}
                  className="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500 focus:ring-2"
                />
                <span className="ml-2 text-sm text-gray-700 font-medium">🔓 Open Access Only</span>
              </label>
            </div>
          </div>
        )}

        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter your research query..."
          className="w-full h-32 p-4 border-2 border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-gray-800 placeholder-gray-400"
          disabled={loading}
        />

        {/* Character Count */}
        <div className="text-xs text-gray-400 mt-1 text-right">
          {query.length} characters
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={loading || !query.trim()}
          className="mt-4 w-full bg-linear-to-br from-blue-600 to-indigo-600 text-white py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed transition shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 active:translate-y-0"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Starting Research...
            </span>
          ) : (
            <span>Start Research →</span>
          )}
        </button>

        <div className="text-xs text-gray-500 text-center mt-2">
          Press <kbd className="px-2 py-1 bg-gray-100 border border-gray-300 rounded text-xs">⌘ + Enter</kbd> to submit
        </div>
      </div>

      {/* Example Queries */}
      <div className="mt-6">
        <p className="text-sm text-gray-600 mb-3">Try these examples:</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {exampleQueries.map((example, i) => (
            <button
              key={i}
              onClick={() => setQuery(example)}
              className="text-left p-3 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg text-sm text-gray-700 transition"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}