// Tokens de cor nomeados — cada um mapeia 1:1 pro hex que já estava em uso
// espalhado pelo app (não consolida tons próximos nem muda nenhuma cor
// renderizada; só dá nome ao que já existia, pra parar de repetir o mesmo
// hex em dezenas de lugares). Usado por App.jsx, MapView, MapToolbar,
// ConnectionPanel, DiscoveryPanel — os arquivos tocados nesta sessão.
// ConfigForm/AgentFleetPanel/SimulationPanel ainda têm cópia própria de S/btn
// (código mais antigo, não convertido agora).

export const color = {
  bgApp:      '#0d0f14',
  bgPanel:    '#161a22',
  bgDisabled: '#1a1f2e',

  border:     '#2a3142',
  borderDark: '#1e2535',

  text:        '#e6e9ef',
  textMuted:   '#8b92a8',
  textMuted2:  '#a0aec0',
  textFaint:   '#4b5563',
  textFaint2:  '#6b7280',
  textFaint3:  '#374151',

  success:       '#6ee7b7',
  successDark:   '#065f46',
  successBg:     '#1a3a2a',

  danger:    '#f87171',
  dangerBg:  '#3a1a1a',

  warning: '#fbbf24',

  indigo:      '#6366f1',
  indigoLight: '#a5b4fc',
  indigoDark:  '#1e1b4b',

  blue:   '#93c5fd',
  blue2:  '#3b82f6',

  purple:      '#a78bfa',
  purpleLight: '#c4b5fd',
}

export function btn(bg, fg, disabled = false) {
  return {
    background: bg, color: fg, border: `1px solid ${fg}`, borderRadius: '8px',
    padding: '0.45rem 0.9rem', fontSize: '0.85rem', fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.55 : 1,
    fontFamily: 'inherit',
  }
}

export const S = {
  input: {
    background: color.bgApp, border: `1px solid ${color.border}`, borderRadius: '6px',
    color: color.text, padding: '0.4rem 0.6rem', fontSize: '0.85rem', outline: 'none',
    fontFamily: 'monospace', width: '100%', boxSizing: 'border-box',
  },
}
