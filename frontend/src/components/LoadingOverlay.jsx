import { motion, AnimatePresence } from 'framer-motion'

export default function LoadingOverlay() {
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
      >
        <div className="text-center">
          {/* Brain Loader */}
          <div className="relative w-32 h-32 mx-auto mb-8">
            <svg viewBox="0 0 100 100" className="w-full h-full">
              <defs>
                <linearGradient id="loadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#00e6c3">
                    <animate attributeName="stopColor" values="#00e6c3;#1a73e8;#00e6c3" dur="2s" repeatCount="indefinite" />
                  </stop>
                  <stop offset="100%" stopColor="#1a73e8">
                    <animate attributeName="stopColor" values="#1a73e8;#00e6c3;#1a73e8" dur="2s" repeatCount="indefinite" />
                  </stop>
                </linearGradient>
              </defs>
              
              {/* Outer ring */}
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="2"
              />
              
              {/* Animated ring */}
              <motion.circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="url(#loadGrad)"
                strokeWidth="2"
                strokeLinecap="round"
                strokeDasharray="283"
                strokeDashoffset="283"
                animate={{ strokeDashoffset: [283, 0, -283] }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                style={{ transformOrigin: 'center', transform: 'rotate(-90deg)' }}
              />
              
              {/* Brain paths */}
              {[...Array(3)].map((_, i) => (
                <motion.path
                  key={i}
                  d={`M ${30 + i * 20} 40 Q 50 ${30 + i * 10} ${70 - i * 20} 50`}
                  fill="none"
                  stroke="url(#loadGrad)"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: [0, 1, 0], opacity: [0, 1, 0] }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: i * 0.3
                  }}
                />
              ))}
              
              {/* Center pulse */}
              <motion.circle
                cx="50"
                cy="50"
                r="8"
                fill="url(#loadGrad)"
                animate={{ scale: [1, 1.3, 1], opacity: [1, 0.5, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            </svg>
            
            {/* Orbiting dots */}
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 rounded-full bg-neural-500"
                style={{ top: '50%', left: '50%' }}
                animate={{
                  x: [0, Math.cos(i * 2.1) * 50],
                  y: [0, Math.sin(i * 2.1) * 50],
                  scale: [1, 0.5, 1]
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  delay: i * 0.2
                }}
              />
            ))}
          </div>

          <motion.h2
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="font-display text-xl font-bold text-white mb-2"
          >
            Analyzing Brain Response
          </motion.h2>
          
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-gray-400 mb-6"
          >
            Processing through TRIBE v2 neural network
          </motion.p>

          {/* Progress steps */}
          <div className="flex items-center justify-center gap-4 text-sm">
            {['Encoding', 'Processing', 'Predicting', 'Generating'].map((step, i) => (
              <motion.div
                key={step}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.2 }}
                className="flex items-center gap-2"
              >
                <motion.div
                  className="w-2 h-2 rounded-full bg-neural-500"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                />
                <span className="text-gray-500">{step}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
