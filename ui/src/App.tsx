import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import Navbar from './components/Navbar'
import Conversion from './pages/Conversion'
import Dashboard from './pages/Dashboard'
import Metrics from './pages/Metrics'
import Testing from './pages/Testing'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-background">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/conversion" element={<Conversion />} />
              <Route path="/testing" element={<Testing />} />
              <Route path="/metrics" element={<Metrics />} />
            </Routes>
          </main>
        </div>
        <Toaster />
      </Router>
    </QueryClientProvider>
  )
}

export default App
