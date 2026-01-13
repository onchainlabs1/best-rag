'use client'

import { useState } from 'react'

interface UploadProgress {
  filename: string
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
  docId?: string
}

export default function DocumentUpload() {
  const [files, setFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([])
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files)
      setFiles(prev => [...prev, ...newFiles])
      setMessage(null)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newFiles = Array.from(e.dataTransfer.files)
      setFiles(prev => [...prev, ...newFiles])
      setMessage(null)
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
    setUploadProgress(prev => prev.filter((_, i) => i !== index))
  }

  const uploadFile = async (file: File, index: number): Promise<void> => {
    // Update progress to uploading
    setUploadProgress(prev => {
      const newProgress = [...prev]
      newProgress[index] = { filename: file.name, status: 'uploading' }
      return newProgress
    })

    try {
      // For PDFs and binary files, convert to base64
      // For text files, read as text
      const isBinary = file.type === 'application/pdf' || 
                       file.name.toLowerCase().endsWith('.pdf') ||
                       file.type.startsWith('image/')
      
      let content: string
      if (isBinary) {
        // Convert to base64 for binary files
        const arrayBuffer = await file.arrayBuffer()
        const bytes = new Uint8Array(arrayBuffer)
        const binary = Array.from(bytes, byte => String.fromCharCode(byte)).join('')
        content = btoa(binary)
      } else {
        // Read as text for text files
        content = await file.text()
      }
      
      // Add timeout (5 minutes per file)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5 * 60 * 1000) // 5 minutes
      
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/api/v1/documents`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            filename: file.name,
            content,
            content_type: file.type || 'text/plain',
            metadata: {},
          }),
          signal: controller.signal,
        })
        
        clearTimeout(timeoutId)

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to upload document' }))
        throw new Error(error.detail || 'Failed to upload document')
      }

        const data = await response.json()
        
        // Update progress to success
        setUploadProgress(prev => {
          const newProgress = [...prev]
          newProgress[index] = { 
            filename: file.name, 
            status: 'success',
            docId: data.id
          }
          return newProgress
        })
      } finally {
        clearTimeout(timeoutId)
      }
    } catch (error) {
      clearTimeout(timeoutId)
      // Update progress to error
      const errorMessage = error instanceof Error 
        ? (error.name === 'AbortError' ? 'Upload timeout (5 minutes exceeded)' : error.message)
        : 'Unknown error'
      
      setUploadProgress(prev => {
        const newProgress = [...prev]
        newProgress[index] = { 
          filename: file.name, 
          status: 'error',
          error: errorMessage
        }
        return newProgress
      })
      throw error
    }
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      setMessage({ type: 'error', text: 'Please select at least one file' })
      return
    }

    setLoading(true)
    setMessage(null)
    
    // Initialize progress for all files
    setUploadProgress(files.map(file => ({ filename: file.name, status: 'pending' as const })))

    let successCount = 0
    let errorCount = 0

    // Upload files sequentially to avoid overwhelming the server
    for (let i = 0; i < files.length; i++) {
      try {
        await uploadFile(files[i], i)
        successCount++
      } catch (error) {
        errorCount++
      }
    }

    // Show summary message
    if (successCount > 0 && errorCount === 0) {
      setMessage({
        type: 'success',
        text: `Successfully uploaded ${successCount} file${successCount > 1 ? 's' : ''}!`,
      })
      // Clear files after successful upload
      setTimeout(() => {
        setFiles([])
        setUploadProgress([])
        const fileInput = document.getElementById('file-input') as HTMLInputElement
        if (fileInput) fileInput.value = ''
      }, 2000)
    } else if (successCount > 0 && errorCount > 0) {
      setMessage({
        type: 'error',
        text: `Uploaded ${successCount} file${successCount > 1 ? 's' : ''}, ${errorCount} failed`,
      })
    } else {
      setMessage({
        type: 'error',
        text: `Failed to upload ${errorCount} file${errorCount > 1 ? 's' : ''}`,
      })
    }

    setLoading(false)
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8">
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Upload Documents</h2>
          <p className="text-gray-600">
            Upload one or multiple documents to be processed and indexed in the knowledge base
          </p>
        </div>

        {/* Drag and Drop Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 ${
            dragActive
              ? 'border-blue-500 bg-blue-50/50'
              : 'border-gray-300 hover:border-gray-400 bg-gray-50/50'
          }`}
        >
          <input
            id="file-input"
            type="file"
            onChange={handleFileChange}
            accept=".txt,.md,.pdf,.doc,.docx"
            multiple
            className="hidden"
          />
          <label
            htmlFor="file-input"
            className="cursor-pointer flex flex-col items-center justify-center"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-4 shadow-lg">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <p className="text-lg font-medium text-gray-700 mb-1">
              {files.length === 0 
                ? 'Click or drag files here' 
                : `${files.length} file${files.length > 1 ? 's' : ''} selected`}
            </p>
            <p className="text-sm text-gray-500">
              Supports: TXT, MD, PDF, DOC, DOCX (multiple files allowed)
            </p>
          </label>
        </div>

        {/* Files List */}
        {files.length > 0 && (
          <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
            {files.map((file, index) => {
              const progress = uploadProgress[index]
              const isUploading = progress?.status === 'uploading'
              const isSuccess = progress?.status === 'success'
              const isError = progress?.status === 'error'

              return (
                <div
                  key={`${file.name}-${index}`}
                  className={`p-4 rounded-lg border ${
                    isSuccess
                      ? 'bg-green-50 border-green-200'
                      : isError
                      ? 'bg-red-50 border-red-200'
                      : isUploading
                      ? 'bg-blue-50 border-blue-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        isSuccess
                          ? 'bg-green-500'
                          : isError
                          ? 'bg-red-500'
                          : isUploading
                          ? 'bg-blue-500'
                          : 'bg-gray-400'
                      }`}>
                        {isSuccess ? (
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : isError ? (
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        ) : isUploading ? (
                          <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        ) : (
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`font-medium truncate ${
                          isSuccess ? 'text-green-900' : isError ? 'text-red-900' : 'text-gray-900'
                        }`}>
                          {file.name}
                        </p>
                        <p className="text-sm text-gray-500">
                          {(file.size / 1024).toFixed(2)} KB
                          {isSuccess && progress?.docId && (
                            <span className="ml-2 text-green-600">• ID: {progress.docId.slice(0, 8)}...</span>
                          )}
                          {isError && progress?.error && (
                            <span className="ml-2 text-red-600">• {progress.error}</span>
                          )}
                        </p>
                      </div>
                    </div>
                    {!loading && (
                      <button
                        onClick={() => removeFile(index)}
                        className="text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0 ml-2"
                        title="Remove file"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={loading || files.length === 0}
          className="mt-6 w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Uploading {files.length} file{files.length > 1 ? 's' : ''}...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Upload {files.length > 0 ? `${files.length} ` : ''}Document{files.length !== 1 ? 's' : ''}
            </>
          )}
        </button>

        {/* Message */}
        {message && (
          <div
            className={`mt-4 p-4 rounded-lg border ${
              message.type === 'success'
                ? 'bg-green-50 border-green-200 text-green-800'
                : 'bg-red-50 border-red-200 text-red-800'
            }`}
          >
            <div className="flex items-center gap-2">
              {message.type === 'success' ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              )}
              <p className="font-medium">{message.text}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
