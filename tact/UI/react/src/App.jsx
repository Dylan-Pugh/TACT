import { useState } from 'react'
import ConfigForm from './components/ConfigForm'
import CleanPage from './components/CleanPage'
import TransformPage from './components/TransformPage'
import BioDataUtilsPage from './components/BioDataUtilsPage'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('upload');

  const handleUploadSuccess = () => {
    setCurrentView('clean');
  };

  return (
    <>
      <header className="app-header">
        <h1>TACT</h1>
        <p>Temporal Adjustment Calculation Tool</p>
        <nav className="app-nav">
          <button
            className={currentView === 'upload' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setCurrentView('upload')}
          >
            Upload
          </button>
          <button
            className={currentView === 'clean' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setCurrentView('clean')}
          >
            Clean
          </button>
          <button
            className={currentView === 'transform' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setCurrentView('transform')}
          >
            Transform
          </button>
          <button
            className={currentView === 'bioUtils' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setCurrentView('bioUtils')}
          >
            Biological Utilities
          </button>
        </nav>
      </header>
      <main>
        {currentView === 'upload' && <ConfigForm onUploadSuccess={handleUploadSuccess} />}
        {currentView === 'clean' && <CleanPage />}
        {currentView === 'transform' && <TransformPage />}
        {currentView === 'bioUtils' && <BioDataUtilsPage />}
      </main>
    </>
  )
}

export default App
