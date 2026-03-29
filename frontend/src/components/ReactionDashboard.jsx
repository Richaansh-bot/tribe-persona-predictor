import { motion } from 'framer-motion'

const REACTION_COLORS = {
  Attention: { from: '#00e6c3', to: '#00b899' },
  Engagement: { from: '#00e6c3', to: '#1a73e8' },
  Valence: { from: '#1a73e8', to: '#4d99ff' },
  Arousal: { from: '#ff3333', to: '#cc0000' },
  Memory: { from: '#00e6c3', to: '#1a73e8' },
  Aesthetics: { from: '#1a73e8', to: '#00e6c3' },
  Novelty: { from: '#ff3333', to: '#00e6c3' },
  Social: { from: '#4d99ff', to: '#00e6c3' },
  Curiosity: { from: '#00e6c3', to: '#ff3333' }
}

export default function ReactionDashboard({ reactions }) {
  const sortedReactions = [...reactions].sort((a, b) => b.score - a.score)

  return (
    <div className="glass rounded-3xl p-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neural-500/20 to-cortex-500/20 flex items-center justify-center">
          <svg className="w-5 h-5 text-neural-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div>
          <h3 className="font-display text-xl font-bold text-white">Reaction Analysis</h3>
          <p className="text-sm text-gray-500">9 reaction dimensions predicted</p>
        </div>
      </div>

      <div className="space-y-5">
        {sortedReactions.map((reaction, index) => {
          const colors = REACTION_COLORS[reaction.type] || { from: '#00e6c3', to: '#1a73e8' }
          
          return (
            <motion.div
              key={reaction.type}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full`} style={{ backgroundColor: colors.from }} />
                  <span className="font-medium text-white">{reaction.type}</span>
                  {index < 3 && (
                    <span className="px-2 py-0.5 rounded-full text-xs bg-neural-500/20 text-neural-400">
                      Top
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4">
                  <ConfidenceMeter value={reaction.confidence} />
                  <span className="font-mono text-lg font-bold text-white w-16 text-right">
                    {(reaction.score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              
              <div className="reaction-bar">
                <motion.div
                  className="reaction-bar-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${reaction.score * 100}%` }}
                  transition={{ duration: 1, delay: index * 0.1, ease: 'easeOut' }}
                  style={{
                    background: `linear-gradient(90deg, ${colors.from}, ${colors.to})`
                  }}
                />
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-8 pt-6 border-t border-gray-800 grid grid-cols-3 gap-4">
        {[
          { label: 'Avg. Score', value: (reactions.reduce((a, r) => a + r.score, 0) / reactions.length * 100).toFixed(0) + '%' },
          { label: 'Peak Reaction', value: sortedReactions[0]?.type || 'N/A' },
          { label: 'Total Confidence', value: (reactions.reduce((a, r) => a + r.confidence, 0) / reactions.length * 100).toFixed(0) + '%' }
        ].map((stat, i) => (
          <div key={i} className="text-center">
            <div className="font-display text-2xl font-bold gradient-text-cyan-blue">
              {stat.value}
            </div>
            <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ConfidenceMeter({ value }) {
  const circumference = 2 * Math.PI * 24
  const strokeDashoffset = circumference * (1 - value)
  
  return (
    <div className="confidence-meter">
      <svg className="confidence-ring w-full h-full -rotate-90" viewBox="0 0 60 60">
        <circle
          cx="30"
          cy="30"
          r="24"
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth="4"
        />
        <circle
          cx="30"
          cy="30"
          r="24"
          fill="none"
          stroke="url(#confidenceGrad)"
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: 'stroke-dashoffset 1s ease-out' }}
        />
        <defs>
          <linearGradient id="confidenceGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00e6c3" />
            <stop offset="100%" stopColor="#1a73e8" />
          </linearGradient>
        </defs>
      </svg>
      <div className="confidence-value text-xs text-gray-400">
        {(value * 100).toFixed(0)}
      </div>
    </div>
  )
}
