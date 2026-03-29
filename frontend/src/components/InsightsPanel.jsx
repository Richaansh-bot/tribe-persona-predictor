import { motion } from 'framer-motion'

export default function InsightsPanel({ insights, persona, reactions }) {
  const getEngagementColor = (level) => {
    switch (level) {
      case 'high': return 'from-neural-500 to-neural-400'
      case 'moderate': return 'from-cortex-500 to-neural-400'
      default: return 'from-gray-600 to-gray-500'
    }
  }

  const getEmotionIcon = (level) => {
    switch (level) {
      case 'intense': return '🔥'
      case 'moderate': return '💫'
      default: return '😌'
    }
  }

  const insightCards = [
    {
      title: 'Engagement Level',
      icon: '👁️',
      value: insights.engagement?.toUpperCase() || 'N/A',
      description: insights.engagement === 'high' 
        ? 'This persona will be highly engaged with the content'
        : insights.engagement === 'moderate'
        ? 'Moderate attention expected throughout'
        : 'Content may struggle to maintain interest',
      color: getEngagementColor(insights.engagement)
    },
    {
      title: 'Emotional Response',
      icon: getEmotionIcon(insights.emotion),
      value: insights.emotion?.toUpperCase() || 'N/A',
      description: insights.emotion === 'intense'
        ? 'Strong emotional reactions predicted'
        : insights.emotion === 'moderate'
        ? 'Balanced emotional engagement'
        : 'Calm, measured emotional response expected',
      color: 'from-synapse-500 to-synapse-400'
    },
    {
      title: 'Cognitive Processing',
      icon: '🧠',
      value: insights.cognitive?.toUpperCase() || 'N/A',
      description: insights.cognitive === 'high'
        ? 'Deep cognitive processing - high learning potential'
        : insights.cognitive === 'moderate'
        ? 'Standard information processing expected'
        : 'Minimal cognitive engagement predicted',
      color: 'from-cortex-500 to-neural-500'
    },
    {
      title: 'Dominant Reaction',
      icon: '⭐',
      value: insights.dominant || 'N/A',
      description: `The strongest predicted response is ${insights.dominant?.toLowerCase() || 'unknown'}`,
      color: 'from-neural-500 to-cortex-400'
    },
    {
      title: 'Memory Retention',
      icon: '💾',
      value: `${((insights.retention || 0) * 100).toFixed(0)}%`,
      description: insights.retention > 0.6
        ? 'High likelihood of long-term memory encoding'
        : insights.retention > 0.4
        ? 'Moderate memory retention expected'
        : 'Content may not be easily remembered',
      color: 'from-cortex-600 to-cortex-400'
    }
  ]

  return (
    <div id="insights">
      <div className="text-center mb-12">
        <h2 className="font-display text-3xl md:text-4xl font-bold text-white mb-4">
          Neural <span className="gradient-text">Insights</span>
        </h2>
        <p className="text-gray-400 max-w-xl mx-auto">
          Predicted responses for the {persona.name.toLowerCase()} persona based on brain encoding
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {insightCards.map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass rounded-2xl p-6 group hover:border-neural-500/30 transition-all duration-300"
          >
            <div className="flex items-start gap-4">
              <div className="text-3xl">{card.icon}</div>
              <div className="flex-1">
                <h3 className="text-sm text-gray-500 uppercase tracking-wider mb-1">
                  {card.title}
                </h3>
                <div className={`font-display text-2xl font-bold bg-gradient-to-r ${card.color} -webkit-background-clip-text -webkit-text-fill-color-transparent bg-clip-text`}>
                  {card.value}
                </div>
              </div>
            </div>
            <p className="mt-4 text-sm text-gray-400 leading-relaxed">
              {card.description}
            </p>
            
            {/* Decorative gradient line */}
            <div className={`mt-4 h-1 rounded-full bg-gradient-to-r ${card.color} opacity-50 group-hover:opacity-100 transition-opacity`} />
          </motion.div>
        ))}
      </div>

      {/* Content Recommendation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="mt-12 glass rounded-3xl p-8"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-neural-500/20 to-cortex-500/20 flex items-center justify-center">
            <svg className="w-6 h-6 text-neural-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h3 className="font-display text-xl font-bold text-white">Content Optimization</h3>
            <p className="text-sm text-gray-500">Recommended adjustments for this persona</p>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              title: 'Optimal Length',
              value: insights.cognitive === 'high' ? '15-25 min' : insights.cognitive === 'moderate' ? '10-15 min' : '5-10 min',
              description: 'Based on attention span prediction'
            },
            {
              title: 'Emotional Tone',
              value: insights.emotion === 'intense' ? 'High Drama' : insights.emotion === 'moderate' ? 'Balanced' : 'Calm & Steady',
              description: 'Recommended emotional intensity'
            },
            {
              title: 'Visual Style',
              value: persona.traits?.visual > 0.6 ? 'Visually Rich' : 'Standard',
              description: 'Based on learning preference'
            }
          ].map((rec, i) => (
            <div key={i} className="p-4 rounded-xl bg-gradient-to-br from-gray-900/50 to-gray-900/30 border border-gray-800">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{rec.title}</div>
              <div className="font-display text-lg font-bold text-white mb-1">{rec.value}</div>
              <div className="text-sm text-gray-400">{rec.description}</div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Reaction Comparison Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mt-8 glass rounded-3xl p-8"
      >
        <h3 className="font-display text-xl font-bold text-white mb-6">Reaction Radar</h3>
        
        <div className="relative w-full max-w-md mx-auto aspect-square">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            {/* Grid circles */}
            {[25, 50, 75, 100].map((r) => (
              <circle
                key={r}
                cx="100"
                cy="100"
                r={r}
                fill="none"
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="1"
              />
            ))}
            
            {/* Grid lines */}
            {reactions.map((_, i) => {
              const angle = (i / reactions.length) * 360 - 90
              const rad = angle * Math.PI / 180
              return (
                <line
                  key={i}
                  x1="100"
                  y1="100"
                  x2={100 + Math.cos(rad) * 100}
                  y2={100 + Math.sin(rad) * 100}
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="1"
                />
              )
            })}
            
            {/* Reaction polygon */}
            <motion.polygon
              points={reactions.map((r, i) => {
                const angle = (i / reactions.length) * 360 - 90
                const rad = angle * Math.PI / 180
                const value = r.score * 100
                return `${100 + Math.cos(rad) * value} ${100 + Math.sin(rad) * value}`
              }).join(' ')}
              fill="url(#radarGrad)"
              stroke="#00e6c3"
              strokeWidth="2"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 1, delay: 0.3 }}
            />
            
            <defs>
              <linearGradient id="radarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00e6c3" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#1a73e8" stopOpacity="0.4" />
              </linearGradient>
            </defs>
            
            {/* Labels */}
            {reactions.map((r, i) => {
              const angle = (i / reactions.length) * 360 - 90
              const rad = angle * Math.PI / 180
              const x = 100 + Math.cos(rad) * 115
              const y = 100 + Math.sin(rad) * 115
              return (
                <text
                  key={i}
                  x={x}
                  y={y}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="text-[8px] fill-gray-500"
                  transform={`rotate(${angle + 90}, ${x}, ${y})`}
                >
                  {r.type.slice(0, 6)}
                </text>
              )
            })}
          </svg>
        </div>
      </motion.div>
    </div>
  )
}
