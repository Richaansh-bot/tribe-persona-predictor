import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import api from '../api'

export default function UploadSection({ onUpload, onAnalyze, uploadedFile, isAnalyzing: externalIsAnalyzing, disabled, onProgress }) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [processingStage, setProcessingStage] = useState('')
  const [useTribeMode, setUseTribeMode] = useState(false)
  const [localIsAnalyzing, setLocalIsAnalyzing] = useState(false)
  const [gpuAvailable, setGpuAvailable] = useState(null)
  const fileInputRef = useRef(null)
  
  // Check GPU availability on mount
  useEffect(() => {
    api.healthCheck().then(data => {
      setGpuAvailable(data.cuda_available || false)
    }).catch(() => {
      setGpuAvailable(false)
    })
  }, [])

  // Use either external or local analyzing state
  const isAnalyzing = localIsAnalyzing || externalIsAnalyzing

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

    // Check GPU if TRIBE mode selected
    if (useTribeMode && gpuAvailable === false) {
      const proceed = window.confirm(
        'TRIBE v2 requires a GPU (CUDA) which is not available on this system.\n\n' +
        'The analysis will use the enhanced CPU fallback which provides fast, meaningful predictions.\n\n' +
        'Proceed with CPU fallback?'
      )
      if (!proceed) return
    }

    setLocalIsAnalyzing(true)
    setUploadProgress(0)
    setProcessingStage('uploading')

    try {
      const result = await api.analyzeVideo(
        uploadedFile,
        'analytical',
        (progress) => {
          setUploadProgress(progress.percent)
          setProcessingStage(progress.stage)
          if (onProgress) onProgress(progress)
        },
        useTribeMode
      )

      if (onAnalyze) {
        onAnalyze(result)
      }
      
      setLocalIsAnalyzing(false)
    } catch (error) {
      console.error('Analysis failed:', error)
      setLocalIsAnalyzing(false)
      alert(`Analysis failed: ${error.message}`)
    }
  }

  const getProgressText = () => {
    if (uploadProgress < 30) return 'Uploading video...'
    if (uploadProgress < 60) return useTribeMode ? 'Extracting video features...' : 'Analyzing content...'
    if (uploadProgress < 90) return useTribeMode ? 'TRIBE v2 brain encoding...' : 'Generating predictions...'
    return 'Finalizing results...'
  }

  return (
    <div id="demo">
      <div className="text-center mb-8">
        <h2 className="font-display text-3xl md:text-4xl font-bold text-white mb-4">
          Upload Your <span className="gradient-text">Content</span>
        </h2>
        <p className="text-gray-400 max-w-xl mx-auto">
          Drop a video to analyze how the selected persona would react to it
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="max-w-2xl mx-auto mb-8">
        <div className="flex items-center justify-between bg-gray-900/50 rounded-2xl p-4 border border-gray-800">
          <div className="flex items-center gap-4">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
              useTribeMode ? 'bg-purple-500/20' : 'bg-emerald-500/20'
            }`}>
              {useTribeMode ? (
                <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              )}
            </div>
            <div>
              <h4 className="font-semibold text-white">
                {useTribeMode ? 'TRIBE v2 Mode' : 'Fast Mode'}
              </h4>
              <p className="text-sm text-gray-500">
                {useTribeMode 
                  ? 'Real brain encoding - requires GPU' 
                  : 'Persona-based predictions - instant results'}
              </p>
            </div>
          </div>
          
          {/* Toggle Switch */}
          <div className="flex items-center gap-3">
            {/* GPU Status Badge */}
            {gpuAvailable !== null && (
              <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${
                gpuAvailable 
                  ? 'bg-emerald-500/20 text-emerald-400' 
                  : 'bg-gray-700/50 text-gray-400'
              }`}>
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z"/>
                </svg>
                {gpuAvailable ? 'GPU' : 'CPU'}
              </div>
            )}
            
            <button
              onClick={() => setUseTribeMode(!useTribeMode)}
              disabled={gpuAvailable === false}
              className={`relative w-14 h-8 rounded-full transition-colors duration-300 flex items-center ${
                useTribeMode ? 'bg-purple-500' : 'bg-gray-700'
              } ${gpuAvailable === false ? 'opacity-50 cursor-not-allowed' : ''}`}
              style={{ paddingLeft: useTribeMode ? '28px' : '4px', paddingRight: useTribeMode ? '4px' : '28px' }}
            >
              <span
                className={`w-6 h-6 rounded-full bg-white shadow-lg transition-all duration-300 flex-shrink-0`}
              />
              <span className={`absolute text-xs font-bold transition-colors duration-300 ${
                useTribeMode ? 'left-1.5 text-purple-200' : 'right-1.5 text-gray-400'
              }`}>
                {useTribeMode ? 'T' : 'F'}
              </span>
            </button>
          </div>
        </div>
        
        {/* Status Messages */}
        {gpuAvailable === false && (
          <div className="mt-3 p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-amber-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <p className="text-amber-400 font-medium text-sm">
                  GPU not detected - TRIBE v2 unavailable
                </p>
                <p className="text-amber-400/70 text-xs mt-1">
                  TRIBE v2 requires CUDA-compatible GPU. Using <span className="text-emerald-400 font-medium">Fast Mode</span> with enhanced CPU analysis for instant, meaningful predictions.
                </p>
              </div>
            </div>
          </div>
        )}
        
        {useTribeMode && gpuAvailable === true && (
          <p className="text-center text-purple-400 text-sm mt-3">
            TRIBE v2 Mode: Real brain encoding using Facebook's TRIBE v2 model
          </p>
        )}
        
        {useTribeMode && gpuAvailable === null && (
          <p className="text-center text-gray-500 text-sm mt-3 animate-pulse">
            Checking GPU availability...
          </p>
        )}
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
                <div className="mb-4 p-4 bg-gray-900/50 rounded-xl border border-gray-800">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${useTribeMode && gpuAvailable ? 'bg-purple-500 animate-pulse' : 'bg-emerald-500 animate-pulse'}`} />
                      <span className="text-sm font-medium text-white">
                        {processingStage === 'uploading' ? 'Uploading video...' : 
                         processingStage === 'processing' ? 'Processing...' : 
                         useTribeMode && gpuAvailable ? 'TRIBE v2 Brain Encoding...' : 'Analyzing...'}
                      </span>
                    </div>
                    <span className={`text-sm font-mono ${useTribeMode && gpuAvailable ? 'text-purple-400' : 'text-emerald-400'}`}>
                      {uploadProgress}%
                    </span>
                  </div>
                  
                  {/* Progress bar */}
                  <div className="h-3 bg-gray-800 rounded-full overflow-hidden mb-3">
                    <motion.div
                      className={`h-full ${useTribeMode && gpuAvailable ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gradient-to-r from-emerald-500 to-teal-500'}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${uploadProgress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                  
                  {/* Stage indicators */}
                  <div className="flex justify-between text-xs text-gray-500">
                    <span className={uploadProgress >= 10 ? 'text-gray-400' : ''}>Upload</span>
                    <span className={uploadProgress >= 30 ? 'text-gray-400' : ''}>Extract</span>
                    <span className={uploadProgress >= 60 ? 'text-gray-400' : ''}>Analyze</span>
                    <span className={uploadProgress >= 90 ? 'text-gray-400' : ''}>Complete</span>
                  </div>
                  
                  {/* Time estimate for TRIBE mode */}
                  {useTribeMode && gpuAvailable && uploadProgress < 100 && (
                    <p className="text-xs text-gray-500 mt-2 text-center">
                      TRIBE v2 mode: May take 5-10 minutes depending on video length
                    </p>
                  )}
                </div>
              )}

              <button
                onClick={handleAnalyze}
                disabled={disabled || isAnalyzing}
                className={`w-full py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${
                  disabled || isAnalyzing
                    ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                    : useTribeMode && gpuAvailable
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg hover:shadow-purple-500/25'
                      : 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:shadow-lg hover:shadow-emerald-500/25'
                }`}
              >
                {isAnalyzing ? (
                  <span className="flex items-center justify-center gap-3">
                    <div className="spinner" />
                    {useTribeMode && gpuAvailable ? 'TRIBE v2 Processing...' : 'Analyzing...'}
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    {useTribeMode && gpuAvailable ? 'Analyze with TRIBE v2' : 'Analyze with Fast Mode'}
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
