import { BarChart3, Brain, Settings, TestTube } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { Button } from './ui/button'

const Navbar = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Brain },
    { path: '/conversion', label: 'Conversion', icon: Settings },
    { path: '/testing', label: 'Testing', icon: TestTube },
    { path: '/metrics', label: 'Metrics', icon: BarChart3 },
  ]

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link to="/" className="flex items-center space-x-2">
              <Brain className="h-6 w-6" />
              <span className="font-bold text-xl">LLM2SLM</span>
            </Link>
          </div>

          <div className="flex items-center space-x-1">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Button
                key={path}
                variant={location.pathname === path ? "default" : "ghost"}
                size="sm"
                asChild
              >
                <Link to={path} className="flex items-center space-x-2">
                  <Icon className="h-4 w-4" />
                  <span>{label}</span>
                </Link>
              </Button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
