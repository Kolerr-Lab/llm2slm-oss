import { useMutation } from '@tanstack/react-query'
import { AlertCircle, CheckCircle, Play, Upload, XCircle } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Progress } from '../components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Textarea } from '../components/ui/textarea'

interface ConversionRequest {
  model_name: string
  provider: string
  config: Record<string, any>
  output_path?: string
}

interface ConversionResponse {
  task_id: string
  status: string
  message: string
}

interface TaskStatus {
  task_id: string
  status: string
  progress: number
  message: string
  result?: any
  error?: string
}

const Conversion = () => {
  const [modelName, setModelName] = useState('')
  const [provider, setProvider] = useState('')
  const [config, setConfig] = useState('{}')
  const [outputPath, setOutputPath] = useState('')
  const [currentTask, setCurrentTask] = useState<TaskStatus | null>(null)

  const startConversion = useMutation({
    mutationFn: async (data: ConversionRequest) => {
      const response = await fetch('/api/convert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })
      if (!response.ok) {
        throw new Error('Failed to start conversion')
      }
      return response.json() as Promise<ConversionResponse>
    },
    onSuccess: (data) => {
      setCurrentTask({
        task_id: data.task_id,
        status: 'pending',
        progress: 0,
        message: 'Conversion started...',
      })
      toast.success('Conversion started successfully')
      pollTaskStatus(data.task_id)
    },
    onError: (error) => {
      toast.error(`Failed to start conversion: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const pollTaskStatus = async (taskId: string) => {
    const poll = async () => {
      try {
        const response = await fetch(`/api/tasks/${taskId}`)
        if (!response.ok) {
          throw new Error('Failed to get task status')
        }
        const status: TaskStatus = await response.json()
        setCurrentTask(status)

        if (status.status === 'completed' || status.status === 'failed') {
          if (status.status === 'completed') {
            toast.success('Conversion completed successfully')
          } else {
            toast.error(`Conversion failed: ${status.error || 'Unknown error'}`)
          }
          return
        }

        // Continue polling
        setTimeout(poll, 2000)
      } catch (error) {
        toast.error('Failed to check task status')
        setCurrentTask(prev => prev ? { ...prev, status: 'failed', error: 'Failed to check status' } : null)
      }
    }
    poll()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!modelName.trim() || !provider) {
      toast.error('Please fill in all required fields')
      return
    }

    let parsedConfig: Record<string, any> = {}
    try {
      parsedConfig = JSON.parse(config)
    } catch {
      toast.error('Invalid JSON configuration')
      return
    }

    startConversion.mutate({
      model_name: modelName,
      provider,
      config: parsedConfig,
      output_path: outputPath || undefined,
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'running':
        return <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'default'
      case 'failed':
        return 'destructive'
      case 'running':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Model Conversion</h1>
        <p className="text-muted-foreground">
          Convert Large Language Models to Small Language Models
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Conversion Configuration</CardTitle>
            <CardDescription>
              Configure the model conversion parameters
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="model-name">Model Name *</Label>
                <Input
                  id="model-name"
                  placeholder="e.g., gpt-3.5-turbo"
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="provider">Provider *</Label>
                <Select value={provider} onValueChange={setProvider} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a provider" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="openai">OpenAI</SelectItem>
                    <SelectItem value="anthropic">Anthropic</SelectItem>
                    <SelectItem value="google">Google</SelectItem>
                    <SelectItem value="local">Local</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="config">Configuration (JSON)</Label>
                <Textarea
                  id="config"
                  placeholder='{"temperature": 0.7, "max_tokens": 100}'
                  value={config}
                  onChange={(e) => setConfig(e.target.value)}
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="output-path">Output Path (optional)</Label>
                <Input
                  id="output-path"
                  placeholder="e.g., ./models/my-slm"
                  value={outputPath}
                  onChange={(e) => setOutputPath(e.target.value)}
                />
              </div>

              <Button
                type="submit"
                disabled={startConversion.isPending}
                className="w-full"
              >
                {startConversion.isPending ? (
                  <>
                    <div className="mr-2 h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Starting Conversion...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Start Conversion
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Conversion Status</CardTitle>
            <CardDescription>
              Monitor the progress of your conversion task
            </CardDescription>
          </CardHeader>
          <CardContent>
            {currentTask ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(currentTask.status)}
                    <Badge variant={getStatusColor(currentTask.status)}>
                      {currentTask.status}
                    </Badge>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    Task ID: {currentTask.task_id}
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{currentTask.progress}%</span>
                  </div>
                  <Progress value={currentTask.progress} />
                </div>

                <div className="p-3 bg-muted rounded-md">
                  <p className="text-sm">{currentTask.message}</p>
                  {currentTask.error && (
                    <p className="text-sm text-destructive mt-1">
                      Error: {currentTask.error}
                    </p>
                  )}
                </div>

                {currentTask.result && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-sm text-green-800">
                      <CheckCircle className="inline h-4 w-4 mr-1" />
                      Conversion completed successfully!
                    </p>
                    <pre className="text-xs mt-2 text-green-700">
                      {JSON.stringify(currentTask.result, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
                <h3 className="mt-4 text-lg font-medium">No active conversion</h3>
                <p className="text-muted-foreground">
                  Configure and start a model conversion to see progress here
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Conversion
