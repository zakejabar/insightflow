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
          <h3 className="text-xl font-bold text-gray-800 mb-4">Sources ({sources.length})</h3>
          <div className="space-y-3">
            {sources.map((source, i) => (
              <div key={i} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="font-semibold text-gray-800">{source.title}</div>
                
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                <a>
                  {source.url}
                </a>
              </div>
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