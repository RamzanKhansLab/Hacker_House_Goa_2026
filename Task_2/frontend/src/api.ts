export type Source = {
  chunk_id: string
  document_id: string
  language: string
  score: number
  snippet: string
  title?: string | null
}

export type Answer = {
  request_id: string
  query: string
  transcript?: string | null
  language: string
  answer: string
  sources: Source[]
  grounded: boolean
  confidence: number
  guardrail_status: string
  demo_mode: boolean
  latency: Record<string, number>
}

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function parse(response: Response): Promise<Answer> {
  const body = await response.json()
  if (!response.ok) throw new Error(body.detail || 'The service is temporarily unavailable.')
  return body as Answer
}

export async function askText(query: string, language?: string): Promise<Answer> {
  const response = await fetch(`${apiUrl}/api/v1/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, language: language || undefined }),
  })
  return parse(response)
}

export async function askVoice(blob: Blob, languageHint?: string): Promise<Answer> {
  const form = new FormData()
  form.append('audio', blob, 'voice-question.webm')
  if (languageHint) form.append('language_hint', languageHint)
  const response = await fetch(`${apiUrl}/api/v1/voice`, { method: 'POST', body: form })
  return parse(response)
}
