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

function App() {
  const [selectedPersona, setSelectedPersona] = useState('analytical')
  const [uploadedFile, setUploadedFile] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [reactions, setReactions] = useState([])
  const [brainRegions, setBrainRegions] = useState([])
  const [insights, setInsights] = useState({})
  const [analysisResult, setAnalysisResult] = useState(null)

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

  const handleAnalyzeResult = (result) => {
    // Handle real API result
    setIsAnalyzing(true)
    
    // The UploadSection handles the API call, this is called with the result
    if (result && result.reactions) {
      // Transform API response to frontend format
      const transformedReactions = result.reactions.map(r => ({
        type: r.type,
        score: r.score,
        confidence: r.confidence
      }))
      
      const transformedBrainRegions = result.brain_regions.map(r => ({
        name: r.name,
        activation: r.activation,
        color: r.color
      }))
      
      setReactions(transformedReactions)
      setBrainRegions(transformedBrainRegions)
      setAnalysisResult(result)
      setAnalysisComplete(true)
    }
    
    setIsAnalyzing(false)
  }

  const generateInsights = () => {
    if (!reactions || reactions.length === 0) return {}
    
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
      retention: reactions.find(r => r.type === 'Memory')?.score || 0,
      usingTribe: analysisResult?.using_tribe || false,
      processingTime: analysisResult?.processing_time || 0
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
              onAnalyze={handleAnalyzeResult}
              uploadedFile={uploadedFile}
              isAnalyzing={isAnalyzing}
              disabled={!uploadedFile}
            />
          </div>
        </section>
        
        {analysisComplete && (
          <>
            <section className="py-20 px-4 md:px-8 max-w-7xl mx-auto">
              <div className="text-center mb-8">
                <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm ${
                  analysisResult?.using_tribe 
                    ? 'bg-purple-500/20 text-purple-400' 
                    : 'bg-emerald-500/20 text-emerald-400'
                }`}>
                  {analysisResult?.using_tribe ? (
                    <>
                      <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
                      Powered by TRIBE v2 (GPU) • {analysisResult?.processing_time?.toFixed(1)}s
                    </>
                  ) : (
                    <>
                      <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                      Enhanced Analysis (CPU) • {analysisResult?.processing_time?.toFixed(1)}s
                    </>
                  )}
                </div>
              </div>
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
