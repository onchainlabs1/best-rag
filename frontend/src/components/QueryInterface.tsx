'use client'

import { useState } from 'react'

interface QueryResponse {
  answer: string
  sources: Array<{
    chunk_id: string
    content: string
    source: string
    score: number
    metadata?: Record<string, unknown>
  }>
  score: number
  metadata: Record<string, unknown>
}

export default function QueryInterface() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState<QueryResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/api/v1/queries`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query,
            top_k: 5,
            score_threshold: 0.3,
            stream: false,
          }),
        }
      )

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Failed to process query' }))
        throw new Error(errorData.detail || 'Failed to process query')
      }

      const data: QueryResponse = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Query Input */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8">
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Query Knowledge Base</h2>
          <p className="text-gray-600">
            Ask questions about indexed documents and receive RAG-based answers
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Question
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Example: What is RAG? How does the embedding system work?"
              className="w-full px-4 py-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-none"
              rows={4}
              disabled={loading}
            />
            <div className="absolute bottom-3 right-3 text-xs text-gray-400">
              {query.length} characters
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Query
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-red-900">Error</h3>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Response */}
      {response && (
        <div className="space-y-6 animate-fade-in">
          {/* Answer Card */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Answer
              </h3>
              <div className="flex items-center gap-2 px-3 py-1 bg-blue-100 rounded-full">
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                <span className="text-sm font-medium text-blue-700">
                  {((response.score || 0) * 100).toFixed(0)}% confidence
                </span>
              </div>
            </div>
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {response.answer}
              </p>
            </div>
          </div>

          {/* Sources Card */}
          {response.sources && response.sources.length > 0 && (
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Sources ({response.sources.length})
              </h3>
              <div className="space-y-4">
                {response.sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="border-2 border-gray-200 rounded-xl p-5 hover:border-blue-300 transition-colors bg-gray-50/50"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold shadow-md">
                          {idx + 1}
                        </div>
                        <div>
                          <div className="font-semibold text-gray-900">
                            {source.source || 'Document'}
                          </div>
                          <div className="text-sm text-gray-500">
                            ID: {source.chunk_id}
                          </div>
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-green-100 rounded-full">
                        <span className="text-sm font-medium text-green-700">
                          {(source.score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="text-gray-700 text-sm leading-relaxed line-clamp-3">
                      {source.content}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Metadata (if available) */}
          {response.metadata && Object.keys(response.metadata).length > 0 && (
            <div className="bg-gray-50/50 rounded-xl p-4 border border-gray-200">
              <details className="cursor-pointer">
                <summary className="text-sm font-medium text-gray-600 hover:text-gray-900">
                  Additional Information
                </summary>
                <div className="mt-3 text-sm text-gray-600">
                  <pre className="whitespace-pre-wrap font-mono">
                    {JSON.stringify(response.metadata, null, 2)}
                  </pre>
                </div>
              </details>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
