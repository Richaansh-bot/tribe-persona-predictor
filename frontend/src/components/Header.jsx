import { useState, useEffect } from 'react'

export default function Header() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
      scrolled ? 'glass py-3' : 'py-6 bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 md:px-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="relative w-12 h-12">
            <svg viewBox="0 0 100 100" className="w-full h-full">
              <defs>
                <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#00e6c3" />
                  <stop offset="100%" stopColor="#1a73e8" />
                </linearGradient>
              </defs>
              <circle cx="50" cy="50" r="45" fill="none" stroke="url(#logoGrad)" strokeWidth="2" />
              <path d="M50 15 Q70 25 65 50 Q60 70 50 85 Q40 70 35 50 Q30 25 50 15" 
                    fill="none" stroke="url(#logoGrad)" strokeWidth="2" opacity="0.6" />
              <circle cx="50" cy="50" r="8" fill="url(#logoGrad)">
                <animate attributeName="r" values="8;10;8" dur="2s" repeatCount="indefinite" />
              </circle>
            </svg>
          </div>
          <div>
            <h1 className="font-display text-xl font-bold gradient-text-cyan-blue">
              TRIBE v2
            </h1>
            <p className="text-xs text-gray-500 font-mono tracking-wider">
              NEURAL PREDICTOR
            </p>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-8">
          {['Demo', 'Personas', 'Reactions', 'Insights'].map((item) => (
            <a
              key={item}
              href={`#${item.toLowerCase()}`}
              className="text-sm text-gray-400 hover:text-neural-400 transition-colors duration-300 relative group"
            >
              {item}
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-neural-500 group-hover:w-full transition-all duration-300" />
            </a>
          ))}
          <a
            href="https://github.com/Richaansh-bot/tribe-persona-predictor"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-neural px-4 py-2 rounded-lg text-sm font-medium"
          >
            View on GitHub
          </a>
        </nav>

        <button
          className="md:hidden p-2 text-neural-400"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {mobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden glass mt-2 mx-4 rounded-xl p-4">
          {['Demo', 'Personas', 'Reactions', 'Insights'].map((item) => (
            <a
              key={item}
              href={`#${item.toLowerCase()}`}
              className="block py-3 text-gray-400 hover:text-neural-400 transition-colors"
              onClick={() => setMobileMenuOpen(false)}
            >
              {item}
            </a>
          ))}
        </div>
      )}
    </header>
  )
}
