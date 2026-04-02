export default function Footer() {
  return (
    <footer className="py-12 px-4 border-t border-gray-800">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10">
              <svg viewBox="0 0 100 100" className="w-full h-full">
                <defs>
                  <linearGradient id="footerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#00e6c3" />
                    <stop offset="100%" stopColor="#1a73e8" />
                  </linearGradient>
                </defs>
                <circle cx="50" cy="50" r="45" fill="none" stroke="url(#footerGrad)" strokeWidth="2" />
                <circle cx="50" cy="50" r="8" fill="url(#footerGrad)" />
              </svg>
            </div>
            <div>
              <div className="font-display font-bold text-white">TRIBE v2 Persona Predictor</div>
              <div className="text-xs text-gray-500">by <span className="text-neural-400 font-medium">Richansh</span></div>
            </div>
          </div>

          <div className="flex items-center gap-6 text-sm text-gray-500">
            <a href="https://github.com/Richaansh-bot/tribe-persona-predictor" target="_blank" rel="noopener noreferrer" className="hover:text-neural-400 transition-colors flex items-center gap-1">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              GitHub
            </a>
            <a href="https://ai.meta.com/research/publications/a-foundation-model-of-vision-audition-and-language-for-in-silico-neuroscience/" target="_blank" rel="noopener noreferrer" className="hover:text-neural-400 transition-colors">
              Paper
            </a>
            <a href="https://huggingface.co/facebook/tribev2" target="_blank" rel="noopener noreferrer" className="hover:text-neural-400 transition-colors">
              HuggingFace
            </a>
          </div>

          <div className="text-sm text-gray-400">
            <span className="text-neural-400 font-medium">Built by Richansh</span> • Powered by TRIBE v2
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-800 text-center text-xs text-gray-600">
          Powered by Meta's TRIBE v2 brain encoding model • Open source project
        </div>
      </div>
    </footer>
  )
}
