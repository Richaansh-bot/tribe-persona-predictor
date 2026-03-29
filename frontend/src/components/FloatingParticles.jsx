import { useEffect, useState } from 'react'

export default function FloatingParticles() {
  const [particles, setParticles] = useState([])

  useEffect(() => {
    const newParticles = [...Array(20)].map((_, i) => ({
      id: i,
      left: Math.random() * 100,
      delay: Math.random() * 15,
      duration: 15 + Math.random() * 10,
      size: 1 + Math.random() * 2
    }))
    setParticles(newParticles)
  }, [])

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="absolute rounded-full bg-neural-500"
          style={{
            left: `${particle.left}%`,
            width: particle.size,
            height: particle.size,
            opacity: 0.3,
            animation: `float-particle ${particle.duration}s linear infinite`,
            animationDelay: `${particle.delay}s`
          }}
        />
      ))}
      
      {/* Gradient orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-neural-500/5 blur-3xl animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-cortex-500/5 blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
    </div>
  )
}
