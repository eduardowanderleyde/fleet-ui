const S = {
  input: { background: '#0d0f14', border: '1px solid #2a3142', borderRadius: '6px', color: '#e6e9ef', padding: '0.4rem 0.6rem', fontSize: '0.85rem', outline: 'none', fontFamily: 'monospace', width: '100%', boxSizing: 'border-box' },
}

function btn(bg, color, disabled = false) {
  return { background: bg, color, border: `1px solid ${color}`, borderRadius: '8px', padding: '0.45rem 0.9rem', fontSize: '0.85rem', fontWeight: 600, cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.55 : 1, fontFamily: 'inherit' }
}

export const ROBOT_PROFILES = [
  { id: 'custom', label: 'Custom (simulação local)', type: 'local' },
  { id: 'tb3_1',  label: 'TurtleBot3 #1',           type: 'ssh', host: '192.168.1.101' },
  { id: 'tb3_2',  label: 'TurtleBot3 #2',           type: 'ssh', host: '192.168.1.102' },
]

const connLightColor = { idle: '#4b5563', connecting: '#fbbf24', connected: '#6ee7b7', error: '#f87171' }

export default function ConnectionPanel({
  containerRef, isOpen, onToggle,
  profiles, extraProfiles, selectedProfile, onSelectProfile,
  connStatus, connMsg, onConnect, onDisconnect,
}) {
  const connLight = connLightColor[connStatus]

  return (
    <div ref={containerRef} style={{ position: 'relative' }}>
      <button onClick={onToggle} aria-expanded={isOpen} aria-haspopup="true"
        style={{ ...btn('#161a22', '#6366f1'), display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span aria-hidden="true" style={{ width: 10, height: 10, borderRadius: '50%', background: connLight, display: 'inline-block', boxShadow: connStatus === 'connected' ? `0 0 6px ${connLight}` : 'none' }} />
        Conectar robô <span aria-hidden="true" style={{ fontSize: '0.7rem', opacity: 0.7 }}>{isOpen ? '▲' : '▼'}</span>
      </button>
      {isOpen && (
        <div style={{ position: 'absolute', top: '2.5rem', left: 0, zIndex: 100, background: '#161a22', border: '1px solid #2a3142', borderRadius: '10px', padding: '1rem', width: '320px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}>
          <div style={{ fontSize: '0.78rem', color: '#8b92a8', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Selecionar robô</div>
          <div role="radiogroup" aria-label="Robô a conectar" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1rem' }}>
            {profiles.map(p => {
              const isSelected = selectedProfile === p.id
              const isExtra    = !!extraProfiles.find(ep => ep.id === p.id)
              return (
                <label key={p.id}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem 0.85rem', borderRadius: '8px', border: `1px solid ${isSelected ? '#6366f1' : '#2a3142'}`, background: isSelected ? 'rgba(99,102,241,0.1)' : 'transparent', cursor: 'pointer' }}>
                  <input type="radio" name="rp" checked={isSelected} onChange={() => onSelectProfile(p.id)} style={{ accentColor: '#6366f1', margin: 0 }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.85rem', color: isSelected ? '#e6e9ef' : '#a0aec0', fontWeight: isSelected ? 600 : 400 }}>{p.label}</div>
                    <div style={{ fontSize: '0.72rem', color: '#4b5563', marginTop: '0.1rem' }}>
                      {isExtra ? `SSH ${p.host} · descoberto` : p.type === 'ssh' ? `SSH ${p.host} · em breve` : 'localhost:8000'}
                    </div>
                  </div>
                </label>
              )
            })}
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button onClick={onConnect} disabled={connStatus === 'connecting'} style={{ ...btn('#065f46', '#6ee7b7'), flex: 1 }}>
              {connStatus === 'connecting' ? '⏳ Conectando…' : 'Conectar'}
            </button>
            {connStatus === 'connected' && (
              <button onClick={onDisconnect} style={btn('#3a1a1a', '#f87171')}>Desconectar</button>
            )}
          </div>
          {connMsg && <div role="status" style={{ marginTop: '0.6rem', fontSize: '0.78rem', color: connStatus === 'error' ? '#f87171' : '#6ee7b7' }}>{connMsg}</div>}
        </div>
      )}
    </div>
  )
}
