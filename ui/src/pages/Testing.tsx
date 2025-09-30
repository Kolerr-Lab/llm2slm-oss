import { useMutation } from '@tanstack/react-query'
import { CheckCircle, Clock, MessageSquare, Send, XCircle } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Textarea } from '../components/ui/textarea'

interface InferenceRequest {
  model_path: string
  prompt: string
  config?: Record<string, any>
}

interface InferenceResponse {
  response: string
  latency_ms: number
  tokens_used?: number
}

const Testing = () => {
  const [modelPath, setModelPath] = useState('')
  const [prompt, setPrompt] = useState('')
  const [config, setConfig] = useState('{"temperature": 0.7, "max_tokens": 100}')
  const [response, setResponse] = useState<InferenceResponse | null>(null)

  const runInference = useMutation({
    mutationFn: async (data: InferenceRequest) => {
      const response = await fetch('/api/infer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })
      if (!response.ok) {
        throw new Error('Failed to run inference')
      }
      return response.json() as Promise<InferenceResponse>
    },
    onSuccess: (data) => {
      setResponse(data)
      toast.success('Inference completed successfully')
    },
    onError: (error) => {
      toast.error(`Inference failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setResponse(null)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!modelPath.trim() || !prompt.trim()) {
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

    runInference.mutate({
      model_path: modelPath,
      prompt,
      config: parsedConfig,
    })
  }

  const loadExamplePrompt = () => {
    setPrompt("Explain the concept of machine learning in simple terms.")
  }

  const loadExampleConfig = () => {
    setConfig(JSON.stringify({
      temperature: 0.7,
      max_tokens: 150,
      top_p: 0.9,
      frequency_penalty: 0.0,
      presence_penalty: 0.0
    }, null, 2))
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Model Testing</h1>
        <p className="text-muted-foreground">
          Test your converted Small Language Models with inference requests
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Inference Configuration</CardTitle>
            <CardDescription>
              Configure your model and prompt for testing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="model-path">Model Path *</Label>
                <Input
                  id="model-path"
                  placeholder="e.g., ./models/my-slm"
                  value={modelPath}
                  onChange={(e) => setModelPath(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="prompt">Prompt *</Label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={loadExamplePrompt}
                  >
                    Load Example
                  </Button>
                </div>
                <Textarea
                  id="prompt"
                  placeholder="Enter your prompt here..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={4}
                  required
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="config">Configuration (JSON)</Label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={loadExampleConfig}
                  >
                    Load Example
                  </Button>
                </div>
                <Textarea
                  id="config"
                  value={config}
                  onChange={(e) => setConfig(e.target.value)}
                  rows={6}
                />
              </div>

              <Button
                type="submit"
                disabled={runInference.isPending}
                className="w-full"
              >
                {runInference.isPending ? (
                  <>
                    <div className="mr-2 h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Running Inference...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Run Inference
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Response</CardTitle>
            <CardDescription>
              Model output and performance metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            {response ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Badge variant="default" className="flex items-center space-x-1">
                    <CheckCircle className="h-3 w-3" />
                    <span>Success</span>
                  </Badge>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center space-x-1">
                      <Clock className="h-3 w-3" />
                      <span>{response.latency_ms}ms</span>
                    </div>
                    {response.tokens_used && (
                      <div className="flex items-center space-x-1">
                        <MessageSquare className="h-3 w-3" />
                        <span>{response.tokens_used} tokens</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="p-4 bg-muted rounded-md">
                  <h4 className="font-medium mb-2">Response:</h4>
                  <div className="text-sm whitespace-pre-wrap">
                    {response.response}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <div className="font-medium text-blue-800">Latency</div>
                    <div className="text-blue-600">{response.latency_ms} ms</div>
                  </div>
                  {response.tokens_used && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                      <div className="font-medium text-green-800">Tokens Used</div>
                      <div className="text-green-600">{response.tokens_used}</div>
                    </div>
                  )}
                </div>
              </div>
            ) : runInference.isError ? (
              <div className="text-center py-8">
                <XCircle className="mx-auto h-12 w-12 text-destructive" />
                <h3 className="mt-4 text-lg font-medium text-destructive">Inference Failed</h3>
                <p className="text-muted-foreground">
                  {runInference.error instanceof Error ? runInference.error.message : 'Unknown error occurred'}
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-4"
                  onClick={() => runInference.reset()}
                >
                  Try Again
                </Button>
              </div>
            ) : (
              <div className="text-center py-8">
                <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground" />
                <h3 className="mt-4 text-lg font-medium">No Response Yet</h3>
                <p className="text-muted-foreground">
                  Configure your model and prompt, then run inference to see the response here
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Testing Tips</CardTitle>
            <CardDescription>
              Best practices for testing your converted models
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h4 className="font-medium mb-2">Prompt Engineering</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Use clear, specific instructions</li>
                  <li>• Provide context when needed</li>
                  <li>• Test with various prompt lengths</li>
                  <li>• Experiment with different temperatures</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">Performance Monitoring</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Monitor latency and token usage</li>
                  <li>• Test with different configurations</li>
                  <li>• Compare results across models</li>
                  <li>• Check for consistent behavior</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Testing
