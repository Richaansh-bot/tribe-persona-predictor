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
              <div className="font-display font-bold text-white">TRIBE v2</div>
              <div className="text-xs text-gray-500">Neural Persona Predictor</div>
            </div>
          </div>

          <div className="flex items-center gap-6 text-sm text-gray-500">
            <a href="https://github.com/Richaansh-bot/tribe-persona-predictor" target="_blank" rel="noopener noreferrer" className="hover:text-neural-400 transition-colors">
              GitHub
            </a>
            <a href="https://ai.meta.com/research/publications/a-foundation-model-of-vision-audition-and-language-for-in-silico-neuroscience/" target="_blank" rel="noopener noreferrer" className="hover:text-neural-400 transition-colors">
              Paper
            </a>
            <a href="https://huggingface.co/facebook/tribev2" target="_blank" rel="noopener noreferrer" className="hover:text-neural-400 transition-colors">
              HuggingFace
            </a>
          </div>

          <div className="text-sm text-gray-600">
            Built by Richansh • Powered by TRIBE v2
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-800 text-center text-xs text-gray-600">
          Powered by Meta's TRIBE v2 brain encoding model • Open source project
        </div>
      </div>
    </footer>
  )
}
