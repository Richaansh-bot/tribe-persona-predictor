import { useState, useEffect } from 'react'
import Header from './components/Header'
import HeroSection from './components/HeroSection'
import PersonaSelector from './components/PersonaSelector'
import UploadSection from './components/UploadSection'
import ReactionDashboard from './components/ReactionDashboard'
import BrainVisualization from './components/BrainVisualization'
import InsightsPanel from './components/InsightsPanel'
import Footer from './components/Footer'
import LoadingOverlay from './components/LoadingOverlay'
import FloatingParticles from './components/FloatingParticles'

const PERSONAS = {
  analytical: {
    name: 'Analytical',
    icon: '🧠',
    description: 'Logical, detail-oriented, systematic thinker',
    traits: { openness: 0.7, conscientiousness: 0.8, extraversion: 0.3, emotional: 0.3 }
  },
  creative: {
    name: 'Creative',
    icon: '✨',
    description: 'Open, imaginative, unconventional approach',
    traits: { openness: 0.9, conscientiousness: 0.4, extraversion: 0.6, emotional: 0.7 }
  },
  emotional: {
    name: 'Emotional',
    icon: '💗',
    description: 'High empathy, deeply affected by content',
    traits: { openness: 0.6, conscientiousness: 0.5, extraversion: 0.5, emotional: 0.9 }
  },
  social: {
    name: 'Social',
    icon: '👥',
    description: 'Values connections, seeks social validation',
    traits: { openness: 0.7, conscientiousness: 0.5, extraversion: 0.9, emotional: 0.6 }
  },
  pragmatic: {
    name: 'Pragmatic',
    icon: '⚡',
    description: 'Practical, results-focused, efficient',
    traits: { openness: 0.4, conscientiousness: 0.9, extraversion: 0.5, emotional: 0.3 }
  },
  tech_savvy: {
    name: 'Tech Savvy',
    icon: '🔮',
    description: 'Comfortable with technology, innovative',
    traits: { openness: 0.8, conscientiousness: 0.7, extraversion: 0.4, emotional: 0.4 }
  }
}

const SAMPLE_REACTIONS = [
  { type: 'Attention', score: 0.72, confidence: 0.89 },
  { type: 'Engagement', score: 0.68, confidence: 0.85 },
  { type: 'Valence', score: 0.65, confidence: 0.82 },
  { type: 'Arousal', score: 0.58, confidence: 0.78 },
  { type: 'Memory', score: 0.75, confidence: 0.91 },
  { type: 'Aesthetics', score: 0.82, confidence: 0.88 },
  { type: 'Novelty', score: 0.61, confidence: 0.76 },
  { type: 'Social', score: 0.54, confidence: 0.72 },
  { type: 'Curiosity', score: 0.69, confidence: 0.84 }
]

const BRAIN_REGIONS = [
  { name: 'Frontal', activation: 0.78, color: '#00e6c3' },
  { name: 'Parietal', activation: 0.65, color: '#00b899' },
  { name: 'Temporal', activation: 0.72, color: '#1a73e8' },
  { name: 'Occipital', activation: 0.85, color: '#4d99ff' },
  { name: 'Cingulate', activation: 0.58, color: '#ff3333' },
  { name: 'Insula', activation: 0.62, color: '#cc0000' },
  { name: 'Subcortical', activation: 0.45, color: '#990000' }
]

function App() {
  const [selectedPersona, setSelectedPersona] = useState('analytical')
  const [uploadedFile, setUploadedFile] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [reactions, setReactions] = useState([])
  const [brainRegions, setBrainRegions] = useState([])
  const [insights, setInsights] = useState({})

  useEffect(() => {
    const handleScroll = () => {
      const reveals = document.querySelectorAll('.reveal')
      reveals.forEach(el => {
        const windowHeight = window.innerHeight
        const elementTop = el.getBoundingClientRect().top
        if (elementTop < windowHeight - 100) {
          el.classList.add('visible')
        }
      })
    }
    window.addEventListener('scroll', handleScroll)
    handleScroll()
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleFileUpload = (file) => {
    setUploadedFile(file)
    setAnalysisComplete(false)
  }

  const handleAnalyze = async () => {
    if (!uploadedFile) return
    
    setIsAnalyzing(true)
    
    // Simulate analysis with TRIBE v2
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // Generate persona-specific reactions
    const persona = PERSONAS[selectedPersona]
    const baseReactions = SAMPLE_REACTIONS.map(r => ({
      ...r,
      score: Math.min(1, r.score * (0.7 + Math.random() * 0.3) + 
        (persona.traits[r.type.toLowerCase()] || 0.3) * 0.2),
      confidence: Math.min(1, r.confidence * (0.9 + Math.random() * 0.1))
    }))
    
    const baseBrain = BRAIN_REGIONS.map(r => ({
      ...r,
      activation: Math.min(1, r.activation * (0.6 + Math.random() * 0.4) + 
        (persona.traits.emotional || 0.5) * 0.2)
    }))
    
    setReactions(baseReactions)
    setBrainRegions(baseBrain)
    setIsAnalyzing(false)
    setAnalysisComplete(true)
  }

  const generateInsights = () => {
    const avgEngagement = reactions
      .filter(r => ['Attention', 'Engagement'].includes(r.type))
      .reduce((a, b) => a + b.score, 0) / 2
    
    const avgEmotion = reactions
      .filter(r => ['Valence', 'Arousal'].includes(r.type))
      .reduce((a, b) => a + b.score, 0) / 2
    
    const avgCognitive = reactions
      .filter(r => ['Memory', 'Curiosity', 'Novelty'].includes(r.type))
      .reduce((a, b) => a + b.score, 0) / 3

    return {
      engagement: avgEngagement > 0.7 ? 'high' : avgEngagement > 0.4 ? 'moderate' : 'low',
      emotion: avgEmotion > 0.6 ? 'intense' : avgEmotion > 0.4 ? 'moderate' : 'calm',
      cognitive: avgCognitive > 0.6 ? 'high' : avgCognitive > 0.4 ? 'moderate' : 'low',
      dominant: reactions.sort((a, b) => b.score - a.score)[0]?.type || 'Unknown',
      retention: reactions.find(r => r.type === 'Memory')?.score || 0
    }
  }

  useEffect(() => {
    if (analysisComplete) {
      setInsights(generateInsights())
    }
  }, [analysisComplete, reactions])

  return (
    <div className="min-h-screen neural-grid relative">
      <FloatingParticles />
      <div className="noise-overlay" />
      
      <Header />
      
      <main>
        <HeroSection />
        
        <section className="py-20 px-4 md:px-8 max-w-7xl mx-auto">
          <div className="reveal">
            <PersonaSelector
              personas={PERSONAS}
              selected={selectedPersona}
              onSelect={setSelectedPersona}
            />
          </div>
          
          <div className="reveal stagger-2 mt-20">
            <UploadSection
              onUpload={handleFileUpload}
              onAnalyze={handleAnalyze}
              uploadedFile={uploadedFile}
              isAnalyzing={isAnalyzing}
              disabled={!uploadedFile}
            />
          </div>
        </section>
        
        {analysisComplete && (
          <>
            <section className="py-20 px-4 md:px-8 max-w-7xl mx-auto">
              <div className="grid lg:grid-cols-2 gap-12">
                <div className="reveal">
                  <BrainVisualization regions={brainRegions} />
                </div>
                <div className="reveal stagger-2">
                  <ReactionDashboard reactions={reactions} />
                </div>
              </div>
            </section>
            
            <section className="py-20 px-4 md:px-8 max-w-7xl mx-auto">
              <div className="reveal">
                <InsightsPanel
                  insights={insights}
                  persona={PERSONAS[selectedPersona]}
                  reactions={reactions}
                />
              </div>
            </section>
          </>
        )}
      </main>
      
      <Footer />
      
      {isAnalyzing && <LoadingOverlay />}
    </div>
  )
}

export default App
