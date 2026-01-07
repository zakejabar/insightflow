'use client'

import { useState } from 'react'

interface ReportViewProps {
  report: string
  sources?: Array<{
    title: string
    url: string
    content: string
  }>
  insights?: string[]
  query: string
}

export default function ReportView({ report, sources, insights, query }: ReportViewProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(report)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `research-report-${Date.now()}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-linear-to-r from-green-50 to-emerald-50 border border-green-200 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-white text-xl">
            ✓
          </div>
          <h2 className="text-2xl font-bold text-gray-800">Research Complete!</h2>
        </div>
        <p className="text-gray-600 ml-13">
          Your research on: <span className="font-semibold">"{query}"</span>
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleCopy}
          className="flex-1 bg-white border-2 border-gray-200 text-gray-700 py-3 px-4 rounded-xl font-semibold hover:bg-gray-50 transition flex items-center justify-center gap-2"
        >
          {copied ? (
            <>
              <span>✓</span>
              <span>Copied!</span>
            </>
          ) : (
            <>
              <span>📋</span>
              <span>Copy to Clipboard</span>
            </>
          )}
        </button>
        <button
          onClick={handleDownload}
          className="flex-1 bg-white border-2 border-gray-200 text-gray-700 py-3 px-4 rounded-xl font-semibold hover:bg-gray-50 transition flex items-center justify-center gap-2"
        >
          <span>📥</span>
          <span>Download Markdown</span>
        </button>
      </div>

      {/* Main Report */}
      <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-100">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Research Report</h3>
        <div className="prose prose-sm md:prose-base max-w-none">
          <pre className="whitespace-pre-wrap font-sans text-gray-700 leading-relaxed">
            {report}
          </pre>
        </div>
      </div>

      {/* Sources (if available) */}
      {sources && sources.length > 0 && (
        <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-100">
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            Sources ({sources.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {sources.map((source, i) => (
              <a
                key={i}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-400 hover:bg-blue-50 transition"
              >
                <div className="flex items-start gap-3">
                  {/* Number */}
                  <div className="shrink-0 w-6 h-6 bg-gray-300 group-hover:bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold transition">
                    {i + 1}
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-800 group-hover:text-blue-600 transition line-clamp-2 text-sm">
                      {source.title}
                    </div>
                    <div className="text-xs text-gray-500 mt-1 truncate">
                      {new URL(source.url).hostname}
                    </div>
                  </div>
                  
                  {/* Arrow Icon */}
                  <svg 
                    className="w-4 h-4 text-gray-400 group-hover:text-blue-600 transition shrink-0" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M9 5l7 7-7 7" 
                    />
                  </svg>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* New Research Button */}
      <div className="text-center">
        
          href="/"
          className="inline-block bg-linear-to-r from-blue-600 to-indigo-600 text-white py-3 px-8 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition shadow-lg"
        <a>
          Start New Research →
        </a>
      </div>
    </div>
  )
}