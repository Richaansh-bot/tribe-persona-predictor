import { motion } from 'framer-motion'

export default function BrainVisualization({ regions }) {
  const maxActivation = Math.max(...regions.map(r => r.activation))

  return (
    <div className="glass rounded-3xl p-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neural-500/20 to-cortex-500/20 flex items-center justify-center">
          <svg className="w-5 h-5 text-neural-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h3 className="font-display text-xl font-bold text-white">Brain Activation</h3>
          <p className="text-sm text-gray-500">Cortical response map</p>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Brain SVG */}
        <div className="flex-1 flex items-center justify-center">
          <div className="brain-viz relative">
            <svg viewBox="0 0 200 200" className="w-full max-w-xs">
              <defs>
                <radialGradient id="brainGrad" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#00e6c3" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#1a73e8" stopOpacity="0.1" />
                </radialGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              
              {/* Brain Outline */}
              <ellipse
                cx="100" cy="100" rx="80" ry="70"
                fill="url(#brainGrad)"
                stroke="rgba(0, 230, 195, 0.3)"
                strokeWidth="2"
                className="brain-region"
              />
              
              {/* Neural Paths */}
              {[...Array(12)].map((_, i) => {
                const angle = (i / 12) * Math.PI * 2
                const x1 = 100 + Math.cos(angle) * 30
                const y1 = 100 + Math.sin(angle) * 25
                const x2 = 100 + Math.cos(angle) * 70
                const y2 = 100 + Math.sin(angle) * 60
                return (
                  <motion.path
                    key={i}
                    d={`M ${x1} ${y1} Q ${100 + Math.cos(angle) * 50} ${100 + Math.sin(angle) * 45} ${x2} ${y2}`}
                    fill="none"
                    stroke="rgba(0, 230, 195, 0.4)"
                    strokeWidth="1"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, delay: i * 0.1 }}
                  />
                )
              })}
              
              {/* Activation Nodes */}
              {regions.map((region, i) => {
                const angle = (i / regions.length) * Math.PI * 2 - Math.PI / 2
                const radius = 45 + region.activation * 30
                const x = 100 + Math.cos(angle) * radius
                const y = 100 + Math.sin(angle) * radius * 0.8
                const size = 4 + region.activation * 8
                
                return (
                  <motion.g key={region.name}>
                    <motion.circle
                      cx={x}
                      cy={y}
                      r={size}
                      fill={region.color}
                      filter="url(#glow)"
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ 
                        scale: [1, 1.2, 1],
                        opacity: [0.8, 1, 0.8]
                      }}
                      transition={{
                        scale: { duration: 2, repeat: Infinity },
                        opacity: { duration: 2, repeat: Infinity },
                        delay: i * 0.2
                      }}
                    />
                    <motion.circle
                      cx={x}
                      cy={y}
                      r={size * 2}
                      fill="none"
                      stroke={region.color}
                      strokeWidth="1"
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: [1.5, 2], opacity: [0.5, 0] }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        delay: i * 0.2
                      }}
                    />
                  </motion.g>
                )
              })}
              
              {/* Center Core */}
              <circle cx="100" cy="100" r="12" fill="#00e6c3" filter="url(#glow)">
                <animate attributeName="r" values="12;14;12" dur="2s" repeatCount="indefinite" />
              </circle>
            </svg>
            
            {/* Orbiting Particles */}
            <div className="absolute inset-0 animate-rotate-slow pointer-events-none">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="absolute w-2 h-2 rounded-full bg-neural-500"
                  style={{
                    top: `${30 + i * 20}%`,
                    left: `${50 + Math.sin(i) * 40}%`,
                    animationDelay: `${i * 0.5}s`
                  }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Region Legend */}
        <div className="lg:w-64 space-y-3">
          <h4 className="font-display font-semibold text-gray-400 text-sm uppercase tracking-wider">
            Cortical Regions
          </h4>
          {regions.sort((a, b) => b.activation - a.activation).map((region, index) => (
            <motion.div
              key={region.name}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-3 group cursor-pointer"
            >
              <div
                className="w-3 h-3 rounded-full transition-transform group-hover:scale-125"
                style={{ backgroundColor: region.color }}
              />
              <span className="flex-1 text-sm text-gray-400 group-hover:text-white transition-colors">
                {region.name}
              </span>
              <span className="font-mono text-sm font-semibold text-white">
                {(region.activation * 100).toFixed(0)}%
              </span>
              {region.activation === maxActivation && (
                <span className="px-1.5 py-0.5 rounded text-xs bg-neural-500/20 text-neural-400">
                  Max
                </span>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="mt-8 pt-6 border-t border-gray-800">
        <h4 className="font-display font-semibold text-gray-400 text-sm uppercase tracking-wider mb-4">
          Neural Activity Over Time
        </h4>
        <div className="h-16 relative">
          <svg className="w-full h-full" viewBox="0 0 400 60" preserveAspectRatio="none">
            <defs>
              <linearGradient id="waveGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#00e6c3" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#00e6c3" stopOpacity="0" />
              </linearGradient>
            </defs>
            <motion.path
              d="M 0 40 Q 50 20 100 35 T 200 30 T 300 35 T 400 25"
              fill="none"
              stroke="url(#waveGrad)"
              strokeWidth="2"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 2 }}
            />
            <motion.path
              d="M 0 40 Q 50 20 100 35 T 200 30 T 300 35 T 400 25 V 60 H 0 Z"
              fill="url(#waveGrad)"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 1 }}
            />
          </svg>
        </div>
      </div>
    </div>
  )
}
