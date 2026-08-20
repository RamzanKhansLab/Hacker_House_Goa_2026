import { FormEvent, useEffect, useRef, useState } from 'react'
import { Answer, askText, askVoice, getBackendState } from './api'

const EXAMPLES = ['What is retrieval augmented generation?', 'How does hybrid retrieval work?', 'RAG क्या है?']
const RECORDING_TYPES = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/ogg']
type VoicePhase = 'idle' | 'requesting' | 'listening' | 'transcribing' | 'retrieving' | 'complete' | 'error'

const phaseText: Record<VoicePhase, string> = {
  idle: 'Ready when you are.', requesting: 'Requesting microphone access...', listening: 'VAANI is listening...',
  transcribing: 'Transcribing your recording...', retrieving: 'Searching knowledge and grounding...',
  complete: 'Grounded response ready.', error: 'Voice session needs attention.',
}
const formatMs = (value: number | undefined) => `${Math.round(value || 0)} ms`
const extensionFor = (mime: string) => mime.startsWith('audio/ogg') ? 'ogg' : 'webm'
const languageName = (language: string) => new Intl.DisplayNames(['en'], { type: 'language' }).of(language) || language.toUpperCase()

export default function App() {
  const [query, setQuery] = useState('')
  const [language, setLanguage] = useState('')
  const [history, setHistory] = useState<Answer[]>([])
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)
  const [voiceOpen, setVoiceOpen] = useState(false)
  const [voicePhase, setVoicePhase] = useState<VoicePhase>('idle')
  const [backend, setBackend] = useState<'checking' | 'ready' | 'unavailable'>('checking')
  const recorder = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])
  const discardRecording = useRef(false)
  const stream = useRef<MediaStream | null>(null)
  const analyser = useRef<AnalyserNode | null>(null)
  const audioContext = useRef<AudioContext | null>(null)
  const animationFrame = useRef<number | null>(null)
  const waveform = useRef<HTMLCanvasElement | null>(null)
  const feed = useRef<HTMLElement | null>(null)
  const recordingStartedAt = useRef<number>(0)

  useEffect(() => { void getBackendState().then(setBackend) }, [])
  useEffect(() => () => cleanupAudio(), [])
  useEffect(() => { feed.current?.scrollTo({ top: feed.current.scrollHeight, behavior: 'smooth' }) }, [history, pending])

  function cleanupAudio() {
    if (animationFrame.current) cancelAnimationFrame(animationFrame.current)
    animationFrame.current = null
    stream.current?.getTracks().forEach(track => track.stop())
    stream.current = null
    analyser.current = null
    if (audioContext.current && audioContext.current.state !== 'closed') void audioContext.current.close()
    audioContext.current = null
    recorder.current = null
  }

  function drawWaveform() {
    const canvas = waveform.current; const node = analyser.current; const context = canvas?.getContext('2d')
    if (!canvas || !node || !context) return
    const values = new Uint8Array(node.fftSize)
    const render = () => {
      if (!waveform.current || !analyser.current) return
      analyser.current.getByteTimeDomainData(values)
      context.clearRect(0, 0, canvas.width, canvas.height)
      context.strokeStyle = '#bff59d'; context.lineWidth = 2; context.beginPath()
      values.forEach((value, index) => {
        const x = index / (values.length - 1) * canvas.width; const y = value / 128 * canvas.height / 2
        index ? context.lineTo(x, y) : context.moveTo(x, y)
      })
      context.stroke(); animationFrame.current = requestAnimationFrame(render)
    }
    render()
  }

  function addAnswer(answer: Answer) {
    setHistory(items => [...items, answer])
    setQuery('')
  }

  async function runText(event: FormEvent) {
    event.preventDefault()
    const submitted = query.trim(); if (!submitted) return
    setPending(true); setError('')
    try { addAnswer(await askText(submitted, language || undefined)) }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'The service is temporarily unavailable.') }
    finally { setPending(false) }
  }

  async function startRecording() {
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      setVoicePhase('error'); setError('Audio recording is not supported by this browser. Please use a current Chrome, Edge, or Firefox browser.'); return
    }
    setError(''); setVoiceOpen(true); setVoicePhase('requesting')
    try {
      const input = await navigator.mediaDevices.getUserMedia({ audio: true }); stream.current = input
      const mime = RECORDING_TYPES.find(type => MediaRecorder.isTypeSupported(type)) || ''
      const media = mime ? new MediaRecorder(input, { mimeType: mime }) : new MediaRecorder(input)
      const context = new AudioContext(); const source = context.createMediaStreamSource(input); const node = context.createAnalyser()
      node.fftSize = 256; source.connect(node); audioContext.current = context; analyser.current = node; chunks.current = []; discardRecording.current = false; recordingStartedAt.current = performance.now()
      media.ondataavailable = event => { if (event.data.size) chunks.current.push(event.data) }
      media.onerror = () => { cleanupAudio(); setVoicePhase('error'); setError('Recording failed. Please try again.') }
      media.onstop = () => { if (!discardRecording.current) void sendRecording(media) }
      recorder.current = media; media.start(); setVoicePhase('listening'); drawWaveform()
    } catch (caught) {
      setVoicePhase('error')
      setError(caught instanceof DOMException && caught.name === 'NotAllowedError' ? 'Microphone permission was denied. You can type a question instead.' : 'Could not start recording. Please try again.')
    }
  }

  function stopRecording() {
    if (recorder.current?.state === 'recording') recorder.current.stop()
  }
  function closeVoice() {
    discardRecording.current = true
    if (recorder.current?.state === 'recording') recorder.current.stop()
    cleanupAudio(); setVoiceOpen(false); setVoicePhase('idle')
  }

  async function sendRecording(media: MediaRecorder) {
    if (animationFrame.current) cancelAnimationFrame(animationFrame.current)
    animationFrame.current = null; stream.current?.getTracks().forEach(track => track.stop())
    if (!chunks.current.length) { cleanupAudio(); setVoicePhase('error'); setError('No audio was captured. Please try again.'); return }
    const mime = media.mimeType || 'audio/webm'
    const filename = `vaani-question.${extensionFor(mime)}`
    const recording = new Blob(chunks.current, { type: mime })
    console.info('VAANI voice recording ready', {
      mime,
      bytes: recording.size,
      duration_ms: Math.round(performance.now() - recordingStartedAt.current),
      filename,
    })
    cleanupAudio(); setVoicePhase('transcribing'); setPending(true)
    try {
      const result = await askVoice(recording, filename, language || undefined)
      setVoicePhase('retrieving'); addAnswer(result); setVoicePhase('complete')
    } catch (caught) {
      setVoicePhase('error'); setError(caught instanceof Error ? caught.message : 'Speech recognition failed. Please try again.')
    } finally { setPending(false) }
  }

  return <div className="app-layout">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">V</span><div><b>VAANI AI</b><small>Voice RAG for Indic knowledge</small></div></div>
      <button className="new-session" onClick={() => { setHistory([]); setQuery(''); setError('') }}>+ New conversation</button>
      <label className="side-label" htmlFor="language">SPOKEN / OUTPUT LANGUAGE</label>
      <select id="language" value={language} onChange={event => setLanguage(event.target.value)}><option value="">Auto-detect</option><option value="en">English</option><option value="hi">Hindi</option><option value="mr">Marathi</option><option value="ta">Tamil</option><option value="te">Telugu</option><option value="bn">Bengali</option><option value="gu">Gujarati</option><option value="kn">Kannada</option><option value="ml">Malayalam</option><option value="ur">Urdu</option></select>
      <p className="side-label">RECENT QUERIES</p><nav className="recent" aria-label="Recent queries">{history.length ? history.slice(-6).reverse().map(item => <button key={item.request_id} onClick={() => setQuery(item.transcript || item.query)}>{item.transcript || item.query}</button>) : <p>Start a conversation to see recent queries.</p>}</nav>
      <p className="sidebar-note">{backend === 'ready' ? 'Knowledge engine ready' : backend === 'checking' ? 'Connecting to knowledge engine...' : 'Backend unavailable'}</p>
    </aside>
    <main className="chat-shell">
      <header className="topbar"><div><b>VAANI AI</b><span>Knowledge, heard. Answers, grounded.</span></div><span className={`status ${backend}`}>{backend === 'ready' ? 'Engine ready' : backend === 'checking' ? 'Connecting' : 'Unavailable'}</span></header>
      <section className="chat-feed" ref={feed} aria-live="polite">
        {!history.length && !pending && <Welcome onExample={setQuery} />}
        {history.map(result => <Conversation key={result.request_id} result={result} />)}
        {pending && <div className="assistant-row"><div className="avatar">V</div><div className="thinking"><span></span><span></span><span></span> VAANI is retrieving grounded evidence...</div></div>}
        {error && <p className="error" role="alert">{error}</p>}
      </section>
      <form className="chat-composer" onSubmit={runText}><textarea aria-label="Ask VAANI AI" value={query} onChange={event => setQuery(event.target.value)} placeholder="Ask VAANI anything about the indexed knowledge base..." maxLength={1000} /><div><button type="button" className="voice-trigger" onClick={() => void startRecording()} disabled={pending || backend === 'unavailable'}>Voice query</button><small>{language ? languageName(language) : 'Auto-detect language'}</small><button className="send" disabled={pending || !query.trim()} aria-label="Send query">↑</button></div></form>
      <p className="demo-footnote">Audio is uploaded to VAANI's voice API. In demo mode the API explicitly uses a mock transcript; real transcription requires Sarvam credentials.</p>
    </main>
    {voiceOpen && <VoicePanel phase={voicePhase} onStop={stopRecording} onClose={closeVoice} canvas={waveform} />}
  </div>
}

function Welcome({ onExample }: { onExample: (query: string) => void }) {
  return <div className="welcome"><p className="eyebrow">MULTILINGUAL VOICE RAG</p><h1>Knowledge, heard.<br /><i>Answers, grounded.</i></h1><p>Ask a question by voice or text. VAANI retrieves indexed evidence, applies guardrails, and reports the measured pipeline latency.</p><div>{EXAMPLES.map(example => <button key={example} onClick={() => onExample(example)}>{example}</button>)}</div></div>
}

function Conversation({ result }: { result: Answer }) {
  const question = result.transcript || result.query
  const retrieval = (result.latency.embedding_ms || 0) + (result.latency.dense_retrieval_ms || 0) + (result.latency.lexical_retrieval_ms || 0) + (result.latency.fusion_ms || 0) + (result.latency.reranking_ms || 0)
  return <article className="conversation"><div className="user-row"><div className="user-bubble">{question}</div><div className="user-avatar">YOU</div></div><div className="assistant-row"><div className="avatar">V</div><div className="assistant-content"><div className="answer-meta"><span className={result.grounded ? 'pass' : 'guardrail'}>{result.grounded ? 'GROUNDED' : result.guardrail_status.replaceAll('_', ' ')}</span><span>{result.demo_mode ? 'DEMO MODE' : 'LIVE PROVIDERS'}</span><span>{languageName(result.language)}</span><span>{formatMs(result.latency.end_to_end_ms)} total</span></div><div className="answer-bubble">{result.answer}</div><details className="evidence"><summary>Retrieved evidence and performance</summary><div className="evidence-grid"><section><h2>Evidence</h2>{result.sources.length ? <ol>{result.sources.map(source => <li key={source.chunk_id}><b>{source.title || source.document_id}</b><small>{source.language.toUpperCase()} · relevance {source.score.toFixed(2)}</small><p>{source.snippet}</p></li>)}</ol> : <p>No sources were returned because the guardrail withheld weak context.</p>}</section><section className="metrics"><h2>Measured performance</h2><p className={retrieval < 200 ? 'fast' : ''}>Retrieval path <b>{formatMs(retrieval)}</b>{retrieval < 200 && <small>under 200 ms</small>}</p><p>STT <b>{formatMs(result.latency.stt_ms)}</b></p><p>Dense retrieval <b>{formatMs(result.latency.dense_retrieval_ms)}</b></p><p>BM25 retrieval <b>{formatMs(result.latency.lexical_retrieval_ms)}</b></p><p>Generation <b>{formatMs(result.latency.llm_ms)}</b></p><p>RAG total <b>{formatMs(result.latency.rag_total_ms)}</b></p></section></div></details></div></div></article>
}

function VoicePanel({ phase, onStop, onClose, canvas }: { phase: VoicePhase; onStop: () => void; onClose: () => void; canvas: React.RefObject<HTMLCanvasElement | null> }) {
  const listening = phase === 'listening'
  return <div className="voice-backdrop" role="dialog" aria-modal="true" aria-labelledby="voice-title"><section className="voice-panel"><button className="close" onClick={onClose} aria-label="Close voice assistant">×</button><p className="eyebrow">VOICE SESSION</p><h2 id="voice-title">VAANI AI</h2><div className={`orb ${listening ? 'listening' : ''}`}>V</div><canvas ref={canvas} className="waveform" width="320" height="70" /><p className="voice-state" aria-live="polite">{phaseText[phase]}</p><div className="pipeline"><span className={phase !== 'idle' ? 'done' : ''}>Query understood</span><span className={['retrieving', 'complete'].includes(phase) ? 'done' : ''}>Searching knowledge</span><span className={phase === 'complete' ? 'done' : ''}>Grounding response</span></div>{listening ? <button className="stop" onClick={onStop}>Stop recording</button> : <button className="quiet" onClick={onClose}>{phase === 'complete' ? 'View response' : 'Close'}</button>}</section></div>
}
