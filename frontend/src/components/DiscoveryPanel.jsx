const S = {
  input: { background: '#0d0f14', border: '1px solid #2a3142', borderRadius: '6px', color: '#e6e9ef', padding: '0.4rem 0.6rem', fontSize: '0.85rem', outline: 'none', fontFamily: 'monospace', width: '100%', boxSizing: 'border-box' },
}

function btn(bg, color, disabled = false) {
  return { background: bg, color, border: `1px solid ${color}`, borderRadius: '8px', padding: '0.45rem 0.9rem', fontSize: '0.85rem', fontWeight: 600, cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.55 : 1, fontFamily: 'inherit' }
}

export default function DiscoveryPanel({
  containerRef, isOpen, onToggle,
  subnet, onSubnetChange, sshUser, onSshUserChange,
  discovering, discovered, discoverError, onDiscover,
  testingSSH, onTestSSH,
}) {
  return (
    <div ref={containerRef} style={{ position: 'relative' }}>
      <button onClick={onToggle} aria-expanded={isOpen} aria-haspopup="true"
        style={{ ...btn('#161a22', '#fbbf24'), display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        🔍 Procurar <span aria-hidden="true" style={{ fontSize: '0.7rem', opacity: 0.7 }}>{isOpen ? '▲' : '▼'}</span>
      </button>
      {isOpen && (
        <div style={{ position: 'absolute', top: '2.5rem', left: 0, zIndex: 100, background: '#161a22', border: '1px solid #2a3142', borderRadius: '10px', padding: '1rem', width: '380px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}>
          <div style={{ fontSize: '0.78rem', color: '#8b92a8', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Descoberta na rede</div>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <input placeholder="Subnet (ex: 192.168.1) — auto" aria-label="Subnet a varrer" value={subnet} onChange={e => onSubnetChange(e.target.value)} style={{ ...S.input, flex: 1 }} />
            <input placeholder="user SSH" aria-label="Usuário SSH" value={sshUser} onChange={e => onSshUserChange(e.target.value)} style={{ ...S.input, width: '80px' }} />
          </div>
          <button onClick={onDiscover} disabled={discovering} style={{ ...btn('#161a22', '#fbbf24'), width: '100%', marginBottom: '0.75rem' }}>
            {discovering ? '⏳ Varrendo…' : '▶ Varrer rede'}
          </button>
          {discoverError && <div role="alert" style={{ color: '#f87171', fontSize: '0.78rem' }}>{discoverError}</div>}
          {discovered.map(h => {
            const st = testingSSH[h.ip]
            const stColor = st === 'ok' ? '#6ee7b7' : st === 'no_ros' ? '#fbbf24' : st === 'error' ? '#f87171' : '#8b92a8'
            return (
              <div key={h.ip} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', background: '#0d0f14', borderRadius: '6px', padding: '0.4rem 0.65rem', border: '1px solid #2a3142', marginTop: '0.4rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.82rem', fontFamily: 'monospace' }}>{h.ip}</div>
                  <div style={{ fontSize: '0.7rem', color: '#4b5563' }}>{h.hostname}</div>
                </div>
                <button onClick={() => onTestSSH(h.ip)} disabled={st === 'testing'} style={{ ...btn('#161a22', stColor), fontSize: '0.72rem', padding: '0.25rem 0.5rem' }}>
                  {st === 'testing' ? '⏳' : st === 'ok' ? '✓ ROS2' : st === 'no_ros' ? '⚠ sem ROS' : st === 'error' ? '✗' : 'Testar'}
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
