import { useQuery } from '@tanstack/react-query'
import { Activity, BarChart3, Download, RefreshCw, TrendingUp } from 'lucide-react'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

interface MetricsData {
  total_conversions: number
  successful_conversions: number
  failed_conversions: number
  average_conversion_time: number
  total_inference_requests: number
  average_inference_latency: number
  model_sizes: Array<{
    name: string
    size_mb: number
    conversion_time: number
  }>
  performance_over_time: Array<{
    timestamp: string
    conversions: number
    inference_requests: number
    average_latency: number
  }>
}

const Metrics = () => {
  const { data: metrics, isLoading, error, refetch } = useQuery<MetricsData>({
    queryKey: ['metrics'],
    queryFn: async () => {
      const response = await fetch('/api/metrics')
      if (!response.ok) {
        throw new Error('Failed to fetch metrics')
      }
      return response.json()
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`
    return `${(seconds / 3600).toFixed(1)}h`
  }

  const formatFileSize = (bytes: number) => {
    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`
  }

  const exportMetrics = () => {
    if (!metrics) return

    const dataStr = JSON.stringify(metrics, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)

    const exportFileDefaultName = `llm2slm-metrics-${new Date().toISOString().split('T')[0]}.json`

    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
            <CardDescription>Failed to load metrics data</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {error instanceof Error ? error.message : 'Unknown error occurred'}
            </p>
            <Button
              variant="outline"
              size="sm"
              className="mt-4"
              onClick={() => refetch()}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Metrics</h1>
          <p className="text-muted-foreground">
            Performance analytics and conversion statistics
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button variant="outline" onClick={exportMetrics}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Conversions</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.total_conversions || 0}</div>
            <p className="text-xs text-muted-foreground">
              {metrics?.successful_conversions || 0} successful
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.total_conversions ?
                ((metrics.successful_conversions / metrics.total_conversions) * 100).toFixed(1) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              {metrics?.failed_conversions || 0} failed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Conversion Time</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.average_conversion_time ? formatDuration(metrics.average_conversion_time) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Per conversion
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inference Requests</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.total_inference_requests || 0}</div>
            <p className="text-xs text-muted-foreground">
              {metrics?.average_inference_latency ? `${metrics.average_inference_latency.toFixed(0)}ms avg` : 'N/A'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Model Sizes */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Converted Models</CardTitle>
          <CardDescription>
            Size and performance metrics for converted models
          </CardDescription>
        </CardHeader>
        <CardContent>
          {metrics?.model_sizes && metrics.model_sizes.length > 0 ? (
            <div className="space-y-4">
              {metrics.model_sizes.map((model, index) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium">{model.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      Size: {formatFileSize(model.size_mb * 1024 * 1024)}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline">
                      {formatDuration(model.conversion_time)}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-medium">No Models Yet</h3>
              <p className="text-muted-foreground">
                Start converting models to see metrics here
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Performance Over Time */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Trends</CardTitle>
          <CardDescription>
            Conversion and inference activity over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          {metrics?.performance_over_time && metrics.performance_over_time.length > 0 ? (
            <div className="space-y-4">
              {metrics.performance_over_time.slice(-10).map((entry, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded">
                  <div className="text-sm">
                    {new Date(entry.timestamp).toLocaleDateString()}
                  </div>
                  <div className="flex space-x-4 text-sm">
                    <span>{entry.conversions} conversions</span>
                    <span>{entry.inference_requests} requests</span>
                    <span>{entry.average_latency.toFixed(0)}ms avg latency</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <TrendingUp className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-medium">No Historical Data</h3>
              <p className="text-muted-foreground">
                Performance trends will appear here as you use the system
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Metrics
