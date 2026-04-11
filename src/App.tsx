import type { CSSProperties, ReactNode } from 'react'
import { useState } from 'react'
import shellImage from '../images/shell.png'
import starfishImage from '../images/starfish.png'
import waterImage from '../images/water.png'

type RewriteMode = 'General' | 'Sympathetic'

type RewriteResponse = {
  rewritten: string
  explanations: string[]
  scores: {
    clarity: number
    directness: number
    assertiveness: number
  }
  improved_phrases: string[]
}

const MODES: RewriteMode[] = ['General', 'Sympathetic']

const initialText =
  'Hi, I just wanted to check in and see if you had any updates when you get a chance.'

const styles = {
  page: {
    minHeight: '100vh',
    padding: '28px 16px 36px',
    color: '#f7f8fb',
  },
  shell: {
    width: '100%',
    maxWidth: '1180px',
    margin: '0 auto',
  },
  masthead: {
    display: 'grid',
    gridTemplateColumns: 'minmax(0, 1.2fr) minmax(320px, 0.8fr)',
    gap: '22px',
    alignItems: 'end',
    marginBottom: '18px',
  },
  brandBlock: {
    padding: '8px 2px 0',
  },
  title: {
    margin: 0,
    fontFamily: 'Iowan Old Style, Georgia, serif',
    fontWeight: 600,
    fontSize: 'clamp(4rem, 10vw, 7.5rem)',
    lineHeight: 0.88,
    letterSpacing: '-0.055em',
    color: '#ffffff',
  },
  subtitle: {
    margin: '18px 0 0',
    maxWidth: '580px',
    color: '#eef1f7',
    fontSize: '1.28rem',
    lineHeight: 1.75,
  },
  subtitleHighlight: {
    color: '#B8B8F3',
    fontSize: '1.38em',
    fontWeight: 700,
    letterSpacing: '-0.02em',
    textShadow: '0 0 24px rgba(184, 184, 243, 0.2)',
  },
  sideNote: {
    padding: '18px 0 8px',
    color: '#d4dbea',
    fontSize: '0.98rem',
    lineHeight: 1.75,
  },
  collage: {
    position: 'relative',
    minHeight: '250px',
    borderRadius: '30px',
    overflow: 'hidden',
    background: '#171b1e',
    border: '1px solid rgba(184, 184, 243, 0.14)',
  },
  collageWater: {
    position: 'absolute',
    inset: 'auto 0 0 0',
    height: '54%',
    backgroundImage: `linear-gradient(180deg, rgba(23,27,30,0) 0%, rgba(23,27,30,0.22) 100%), url(${waterImage})`,
    backgroundPosition: 'center bottom',
    backgroundSize: 'cover',
    opacity: 0.48,
    filter: 'saturate(0.8)',
  },
  collageGlow: {
    position: 'absolute',
    top: '-60px',
    right: '20px',
    width: '220px',
    height: '220px',
    borderRadius: '999px',
    background: 'radial-gradient(circle, rgba(184, 184, 243, 0.28), rgba(184, 184, 243, 0))',
  },
  collageShell: {
    position: 'absolute',
    right: '-8px',
    bottom: '14px',
    width: '250px',
    transform: 'rotate(5deg)',
    opacity: 0.88,
    mixBlendMode: 'screen' as const,
    filter: 'drop-shadow(0 18px 30px rgba(0, 0, 0, 0.35))',
  },
  collageStarfish: {
    position: 'absolute',
    left: '18px',
    top: '22px',
    width: '96px',
    transform: 'rotate(-14deg)',
    opacity: 0.94,
    filter: 'drop-shadow(0 14px 24px rgba(0, 0, 0, 0.28))',
  },
  collageCaption: {
    position: 'absolute',
    left: '22px',
    bottom: '18px',
    maxWidth: '190px',
    color: '#ffffff',
    fontSize: '0.92rem',
    lineHeight: 1.55,
  },
  mainGrid: {
    display: 'grid',
    gridTemplateColumns: 'minmax(300px, 390px) minmax(0, 1fr)',
    gap: '18px',
    alignItems: 'start',
  },
  inputPanel: {
    padding: '22px',
    borderRadius: '26px',
    background: '#171b1e',
    border: '1px solid rgba(255,255,255,0.06)',
    display: 'grid',
    gap: '16px',
    position: 'sticky' as const,
    top: '20px',
  },
  panelTitle: {
    margin: 0,
    color: '#ffffff',
    fontSize: '1.02rem',
    letterSpacing: '0.01em',
  },
  panelText: {
    margin: 0,
    color: '#d4dbea',
    fontSize: '0.95rem',
    lineHeight: 1.65,
  },
  label: {
    display: 'block',
    marginBottom: '10px',
    color: '#f4f6fb',
    fontSize: '0.88rem',
  },
  textarea: {
    width: '100%',
    minHeight: '210px',
    resize: 'vertical' as const,
    borderRadius: '18px',
    border: '1px solid rgba(184, 184, 243, 0.18)',
    background: '#0f1215',
    color: '#ffffff',
    padding: '16px',
    outline: 'none',
    lineHeight: 1.72,
  },
  select: {
    width: '100%',
    borderRadius: '16px',
    border: '1px solid rgba(184, 184, 243, 0.18)',
    background: '#0f1215',
    color: '#ffffff',
    padding: '14px 16px',
    outline: 'none',
  },
  button: {
    width: '100%',
    border: 'none',
    borderRadius: '18px',
    background: '#B8B8F3',
    color: '#14181b',
    padding: '15px 18px',
    fontSize: '1rem',
    fontWeight: 800,
    cursor: 'pointer',
  },
  helper: {
    margin: 0,
    color: '#cdd6e6',
    fontSize: '0.92rem',
    lineHeight: 1.6,
  },
  error: {
    margin: 0,
    color: '#ffd9d9',
  },
  outputStack: {
    display: 'grid',
    gap: '18px',
  },
  featuredCard: {
    padding: '26px 26px 28px',
    borderRadius: '30px',
    background: '#171b1e',
    border: '1px solid rgba(255,255,255,0.06)',
  },
  featuredRewrite: {
    background: 'linear-gradient(180deg, #1a2427 0%, #162023 100%)',
    border: '1px solid rgba(184, 184, 243, 0.12)',
  },
  featuredText: {
    margin: 0,
    color: '#f7fbff',
    fontSize: '1.08rem',
    lineHeight: 1.85,
    whiteSpace: 'pre-wrap' as const,
  },
  lowerGrid: {
    display: 'grid',
    gridTemplateColumns: 'minmax(0, 1fr) minmax(280px, 0.85fr)',
    gap: '18px',
    alignItems: 'start',
  },
  sectionTitle: {
    margin: '0 0 12px',
    color: '#ffffff',
    fontSize: '0.98rem',
  },
  bodyText: {
    margin: 0,
    color: '#eef2f8',
    lineHeight: 1.8,
    whiteSpace: 'pre-wrap' as const,
  },
  highlight: {
    background: '#B8B8F3',
    color: '#151a1d',
    borderRadius: '7px',
    padding: '2px 5px',
  },
  rail: {
    display: 'grid',
    gap: '18px',
  },
  noteCard: {
    padding: '20px 20px 20px 34px',
    borderRadius: '22px',
    background: '#171b1e',
    border: '1px solid rgba(255,255,255,0.06)',
    color: '#eef2f8',
    lineHeight: 1.65,
    margin: 0,
  },
  scoreCard: {
    padding: '22px',
    borderRadius: '24px',
    background: 'linear-gradient(180deg, rgba(184, 184, 243, 0.12) 0%, rgba(23, 27, 30, 1) 100%)',
    border: '2px solid #B8B8F3',
    boxShadow: '0 0 0 1px rgba(184, 184, 243, 0.08) inset',
    minHeight: '120px',
    display: 'grid',
    alignContent: 'start',
  },
  scoreGrid: {
    display: 'grid',
    gap: '12px',
  },
  scoreRow: {
    display: 'grid',
    gap: '8px',
    padding: '12px 14px',
    borderRadius: '16px',
    background: 'rgba(184, 184, 243, 0.08)',
    border: '1px solid rgba(184, 184, 243, 0.14)',
  },
  scoreLabel: {
    display: 'flex',
    justifyContent: 'space-between',
    color: '#f5f7fd',
    fontSize: '0.92rem',
  },
  scoreTrack: {
    width: '100%',
    height: '10px',
    borderRadius: '999px',
    background: 'rgba(255,255,255,0.08)',
    overflow: 'hidden',
  },
  scoreFill: {
    height: '100%',
    borderRadius: '999px',
    background: '#488286',
  },
  empty: {
    margin: 0,
    color: '#d1d8e8',
  },
} satisfies Record<string, CSSProperties>

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function highlightMessage(text: string, phrases: string[]) {
  if (!text) return text

  const filtered = [...new Set(phrases.map((phrase) => phrase.trim()).filter(Boolean))]
  if (filtered.length === 0) return text

  const pattern = new RegExp(`(${filtered.map(escapeRegExp).join('|')})`, 'gi')
  const parts = text.split(pattern)

  return parts.map((part, index) => {
    const match = filtered.find((phrase) => phrase.toLowerCase() === part.toLowerCase())
    if (!match) return <span key={`${part}-${index}`}>{part}</span>

    return (
      <span key={`${part}-${index}`} style={styles.highlight}>
        {part}
      </span>
    )
  })
}

function clampScore(value: number) {
  return Math.max(0, Math.min(100, value))
}

function Section({
  title,
  children,
  style,
}: {
  title: string
  children: ReactNode
  style?: CSSProperties
}) {
  return (
    <section style={style}>
      <h2 style={styles.sectionTitle}>{title}</h2>
      {children}
    </section>
  )
}

export default function App() {
  const [text, setText] = useState(initialText)
  const [mode, setMode] = useState<RewriteMode>('General')
  const [result, setResult] = useState<RewriteResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const highlightedOriginal = highlightMessage(text, result?.improved_phrases ?? [])

  async function handleRewrite() {
    if (!text.trim()) {
      setError('Enter a message to rewrite.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/rewrite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, mode }),
      })

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }

      const data = (await response.json()) as RewriteResponse
      setResult(data)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to rewrite the message right now.',
      )
    } finally {
      setLoading(false)
    }
  }

  const scoreEntries: Array<[string, number]> = result
    ? [
        ['Clarity', clampScore(result.scores.clarity)],
        ['Directness', clampScore(result.scores.directness)],
        ['Assertiveness', clampScore(result.scores.assertiveness)],
      ]
    : [
        ['Clarity', 86],
        ['Directness', 79],
        ['Assertiveness', 84],
      ]
  const overallScore = Math.round(
    scoreEntries.reduce((total, [, value]) => total + value, 0) / scoreEntries.length,
  )
  const allScoreEntries: Array<[string, number]> = [['Confidence', overallScore], ...scoreEntries]

  return (
    <main style={styles.page}>
      <div style={styles.shell}>
        <header style={styles.masthead}>
          <div style={styles.brandBlock}>
            <h1 style={styles.title}>Siren</h1>
            <p style={styles.subtitle}>
              <span style={styles.subtitleHighlight}>Voices that cannot be ignored.</span>
            </p>
          </div>
        </header>

        <div style={styles.mainGrid}>
          <aside style={styles.inputPanel}>
            <div style={styles.collage}>
              <div style={styles.collageGlow} />
              <div style={styles.collageWater} />
              <img src={shellImage} alt="" style={styles.collageShell} />
              <img src={starfishImage} alt="" style={styles.collageStarfish} />

            </div>

            <div>
              <h2 style={styles.panelTitle}>Input</h2>
              <p style={styles.panelText}>
                Paste an email draft, and Siren rewrites it in a stronger voice.
              </p>
            </div>

            <div>
              <label htmlFor="message" style={styles.label}>
                Original draft
              </label>
              <textarea
                id="message"
                style={styles.textarea}
                value={text}
                onChange={(event) => setText(event.target.value)}
                placeholder="Paste a message that needs a stronger tone."
              />
            </div>

            <div>
              <label htmlFor="mode" style={styles.label}>
                Tone
              </label>
              <select
                id="mode"
                style={styles.select}
                value={mode}
                onChange={(event) => setMode(event.target.value as RewriteMode)}
              >
                {MODES.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>

            <button style={styles.button} onClick={handleRewrite} disabled={loading}>
              {loading ? 'Rewriting...' : 'Rewrite with Siren'}
            </button>
            <p style={styles.helper}>Clearer asks. Cleaner tone. Less hedging.</p>
            {error ? <p style={styles.error}>{error}</p> : null}
          </aside>

          <div style={styles.outputStack}>
            <Section title="Original message" style={styles.featuredCard}>
              <p style={styles.featuredText}>{highlightedOriginal}</p>
            </Section>

            <Section title="Rewritten message" style={{ ...styles.featuredCard, ...styles.featuredRewrite }}>
              <p style={styles.featuredText}>
                {result?.rewritten ?? ''}
              </p>
            </Section>

            <div style={styles.lowerGrid}>
              <div style={styles.rail}>
                <Section title="Why it changed" style={undefined}>
                  {result?.explanations.length ? (
                    <ul style={styles.noteCard}>
                      {result.explanations.map((item) => (
                        <li key={item} style={{ marginBottom: '8px' }}>
                          {item}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </Section>

                <Section title="Message score" style={styles.scoreCard}>
                  <div style={styles.scoreGrid}>
                    {allScoreEntries.map(([label, value]) => (
                      <div key={label} style={styles.scoreRow}>
                        <div style={styles.scoreLabel}>
                          <span>{label}</span>
                          <span>{value}%</span>
                        </div>
                        <div style={styles.scoreTrack}>
                          <div style={{ ...styles.scoreFill, width: `${value}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </Section>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
