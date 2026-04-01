import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import api from '../api'

export default function UploadSection({ onUpload, onAnalyze, uploadedFile, isAnalyzing, disabled, onProgress }) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [processingStage, setProcessingStage] = useState('')
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('video/')) {
      onUpload(file)
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      onUpload(file)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const handleAnalyze = async () => {
    if (!uploadedFile || isAnalyzing) return

    try {
      setUploadProgress(0)
      setProcessingStage('uploading')

      // Call the real API
      const result = await api.analyzeVideo(
        uploadedFile,
        'analytical', // Will be overridden by parent
        (progress) => {
          setUploadProgress(progress.percent)
          setProcessingStage(progress.stage)
          if (onProgress) onProgress(progress)
        }
      )

      // Pass result to parent
      if (onAnalyze) {
        onAnalyze(result)
      }
    } catch (error) {
      console.error('Analysis failed:', error)
      alert(`Analysis failed: ${error.message}`)
    }
  }

  const getProgressText = () => {
    if (processingStage === 'uploading') {
      return `Uploading... ${uploadProgress}%`
    } else if (processingStage === 'processing') {
      return 'Processing with TRIBE v2...'
    }
    return 'Analyzing Brain Response...'
  }

  return (
    <div id="demo">
      <div className="text-center mb-12">
        <h2 className="font-display text-3xl md:text-4xl font-bold text-white mb-4">
          Upload Your <span className="gradient-text">Content</span>
        </h2>
        <p className="text-gray-400 max-w-xl mx-auto">
          Drop a video to analyze how the selected persona would react to it
          <span className="block mt-2 text-neural-400 text-sm">
            Powered by Meta's TRIBE v2 brain encoding model
          </span>
        </p>
      </div>

      <div className="max-w-2xl mx-auto">
        <motion.div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative rounded-3xl border-2 border-dashed transition-all duration-300 ${
            isDragging
              ? 'border-neural-500 bg-neural-500/10'
              : 'border-gray-700 hover:border-neural-500/50'
          }`}
        >
          {!uploadedFile ? (
            <div
              className="p-12 text-center cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                className="hidden"
              />
              
              <motion.div
                animate={isDragging ? { scale: 1.1 } : { scale: 1 }}
                className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-neural-500/20 to-cortex-500/20 flex items-center justify-center"
              >
                <svg className="w-10 h-10 text-neural-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </motion.div>
              
              <h3 className="font-display text-xl font-semibold text-white mb-2">
                Drag & Drop your video
              </h3>
              <p className="text-gray-500 mb-4">or click to browse</p>
              <p className="text-xs text-gray-600">
                Supports MP4, MOV, WebM • Max 500MB
              </p>
            </div>
          ) : (
            <div className="p-8">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-neural-500/20 to-cortex-500/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-neural-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h4 className="font-display font-semibold text-white truncate">
                    {uploadedFile.name}
                  </h4>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(uploadedFile.size)}
                  </p>
                </div>
                <button
                  onClick={() => onUpload(null)}
                  className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {isAnalyzing && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-400 mb-1">
                    <span>{getProgressText()}</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-neural-500 to-cortex-500"
                      initial={{ width: 0 }}
                      animate={{ width: `${uploadProgress}%` }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                </div>
              )}

              <button
                onClick={handleAnalyze}
                disabled={disabled || isAnalyzing}
                className={`w-full py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${
                  disabled || isAnalyzing
                    ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-neural-600 to-cortex-600 text-white hover:shadow-lg hover:shadow-neural-500/25'
                }`}
              >
                {isAnalyzing ? (
                  <span className="flex items-center justify-center gap-3">
                    <div className="spinner" />
                    {getProgressText()}
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    Analyze with TRIBE v2
                  </span>
                )}
              </button>

              {isAnalyzing && (
                <p className="mt-3 text-center text-xs text-gray-500">
                  This may take a few minutes depending on video length...
                </p>
              )}
            </div>
          )}
        </motion.div>

        {/* Sample Videos */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600 mb-4">Try with sample content</p>
          <div className="flex flex-wrap justify-center gap-3">
            {['Nature Documentary', 'City Timelapse', 'Concert Footage'].map((sample, i) => (
              <button
                key={i}
                onClick={() => onUpload({ name: `${sample}.mp4`, size: 15000000 })}
                className="px-4 py-2 rounded-lg glass-light text-sm text-gray-400 hover:text-white hover:border-neural-500/30 transition-all"
              >
                {sample}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
