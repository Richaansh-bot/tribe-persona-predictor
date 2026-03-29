import { motion } from 'framer-motion'

export default function PersonaSelector({ personas, selected, onSelect }) {
  return (
    <div id="personas">
      <div className="text-center mb-12">
        <h2 className="font-display text-3xl md:text-4xl font-bold text-white mb-4">
          Select Your <span className="gradient-text-cyan-blue">Persona</span>
        </h2>
        <p className="text-gray-400 max-w-xl mx-auto">
          Choose a personality type to see how different minds process the same content
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {Object.entries(personas).map(([key, persona], index) => (
          <motion.button
            key={key}
            onClick={() => onSelect(key)}
            className={`persona-card relative p-6 rounded-2xl glass-light cursor-pointer group ${
              selected === key ? 'selected border-2 border-neural-500' : 'border border-transparent hover:border-neural-500/30'
            }`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
          >
            {selected === key && (
              <motion.div
                className="absolute inset-0 rounded-2xl bg-gradient-to-br from-neural-500/20 to-cortex-500/20"
                layoutId="selectedPersona"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              />
            )}
            
            <div className="relative z-10 text-center">
              <div className="text-4xl mb-3">{persona.icon}</div>
              <h3 className="font-display font-semibold text-white text-sm mb-1">
                {persona.name}
              </h3>
              <p className="text-xs text-gray-500 leading-tight">
                {persona.description}
              </p>
            </div>

            {selected === key && (
              <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-neural-500 flex items-center justify-center">
                <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
            )}

            {/* Hover Glow */}
            <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-neural-500/10 to-cortex-500/10" />
            </div>
          </motion.button>
        ))}
      </div>

      {/* Selected Persona Details */}
      <motion.div
        key={selected}
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        className="mt-8 p-6 rounded-2xl glass"
      >
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="text-6xl">{personas[selected].icon}</div>
          <div className="text-center md:text-left">
            <h3 className="font-display text-xl font-bold text-white">
              {personas[selected].name} Persona
            </h3>
            <p className="text-gray-400 mt-1">{personas[selected].description}</p>
          </div>
          <div className="md:ml-auto grid grid-cols-2 gap-4 text-sm">
            {Object.entries(personas[selected].traits).map(([trait, value]) => (
              <div key={trait} className="flex items-center gap-2">
                <span className="text-gray-500 capitalize">{trait}:</span>
                <div className="w-20 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-neural-500 to-cortex-500 rounded-full"
                    style={{ width: `${value * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  )
}
