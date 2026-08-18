import { FormEvent, useEffect, useRef, useState } from 'react'
import { Answer, askText, askVoice } from './api'

const EXAMPLES = [
  'What is retrieval augmented generation?',
  'How does hybrid retrieval work?',
  'RAG क्या है?',
]

function formatMs(value: number | undefined) {
  return `${Math.round(value || 0)} ms`
}

export default function App() {
  const [query, setQuery] = useState(EXAMPLES[0])
  const [language, setLanguage] = useState('')
  const [answer, setAnswer] = useState<Answer | null>(null)
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)
  const [recording, setRecording] = useState(false)
  const recorder = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])

  useEffect(() => () => recorder.current?.stream.getTracks().forEach(track => track.stop()), [])

  async function runText(event: FormEvent) {
    event.preventDefault()
    if (!query.trim()) return
    setPending(true); setError('')
    try { setAnswer(await askText(query, language || undefined)) }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'The service is temporarily unavailable.') }
    finally { setPending(false) }
  }

  async function toggleRecording() {
    if (recording) { recorder.current?.stop(); return }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const media = new MediaRecorder(stream)
      chunks.current = []
      media.ondataavailable = event => { if (event.data.size) chunks.current.push(event.data) }
      media.onstop = async () => {
        setRecording(false); stream.getTracks().forEach(track => track.stop())
        if (!chunks.current.length) return
        setPending(true); setError('')
        try { setAnswer(await askVoice(new Blob(chunks.current, { type: media.mimeType || 'audio/webm' }), language || undefined)) }
        catch (caught) { setError(caught instanceof Error ? caught.message : 'Speech recognition failed. Please try again.') }
        finally { setPending(false) }
      }
      recorder.current = media; media.start(); setRecording(true)
    } catch { setError('Microphone access is required for a voice question.') }
  }

  return <main className="shell">
    <section className="hero">
      <p className="eyebrow">HACKER HOUSE GOA · TASK 02</p>
      <h1>Knowledge, heard.<br /><i>Answers, grounded.</i></h1>
      <p className="lede">A multilingual voice RAG workspace with hybrid search, source-level evidence, and guardrails before generation.</p>
      <div className="chips">{EXAMPLES.map(example => <button key={example} onClick={() => setQuery(example)}>{example}</button>)}</div>
    </section>

    <section className="workspace" aria-label="Ask the knowledge base">
      <form onSubmit={runText} className="composer">
        <label htmlFor="question">Ask the indexed knowledge base</label>
        <textarea id="question" value={query} onChange={event => setQuery(event.target.value)} maxLength={1000} />
        <div className="composer-actions">
          <select aria-label="Language hint" value={language} onChange={event => setLanguage(event.target.value)}>
            <option value="">Auto-detect language</option><option value="en">English</option><option value="hi">Hindi</option>
            <option value="mr">Marathi</option><option value="ta">Tamil</option><option value="te">Telugu</option>
          </select>
          <button type="button" className={`voice ${recording ? 'recording' : ''}`} onClick={toggleRecording} disabled={pending}>
            <span aria-hidden="true">●</span> {recording ? 'Stop & send' : 'Ask by voice'}
          </button>
          <button className="submit" disabled={pending}>{pending ? 'Searching…' : 'Ask →'}</button>
        </div>
      </form>
      <p className="demo-note">Voice uploads remain on the backend. Demo mode uses a safe, deterministic transcript when no Sarvam key is configured.</p>

      {error && <p role="alert" className="error">{error}</p>}
      {answer && <AnswerCard result={answer} />}
    </section>
  </main>
}

function AnswerCard({ result }: { result: Answer }) {
  const latencyRows = [['RAG total', result.latency.rag_total_ms], ['Speech-to-text', result.latency.stt_ms], ['End to end', result.latency.end_to_end_ms]]
  return <article className="answer-card">
    <div className="answer-meta"><span className={result.grounded ? 'pass' : 'guardrail'}>{result.guardrail_status.replaceAll('_', ' ')}</span><span>{result.demo_mode ? 'DEMO MODE' : 'LIVE PROVIDERS'}</span><span>{Math.round(result.confidence * 100)}% confidence</span></div>
    {result.transcript && <p className="transcript">“{result.transcript}”</p>}
    <h2>{result.answer}</h2>
    <div className="answer-grid">
      <section><h3>Retrieved sources</h3>{result.sources.length ? <ol className="sources">{result.sources.map(source => <li key={source.chunk_id}><b>{source.title || source.document_id}</b><small>{source.language.toUpperCase()} · score {source.score.toFixed(2)}</small><p>{source.snippet}</p></li>)}</ol> : <p className="muted">No sources were returned because the guardrail withheld weak context.</p>}</section>
      <aside><h3>Latency</h3>{latencyRows.map(([label, value]) => <div className="metric" key={String(label)}><span>{label}</span><b>{formatMs(Number(value))}</b></div>)}<p className="muted">STT is displayed separately from the RAG pipeline.</p></aside>
    </div>
  </article>
}
