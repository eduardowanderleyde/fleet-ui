export default function MapToolbar({
  showFloor, onToggleFloor, savedMapMeta,
  floorOpacity, onFloorOpacityChange,
  mapOk, savingMap, saveMsg, onSave,
  onCenter, hoverCoord,
}) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0,
                  background: '#161a22', borderRadius: '8px', padding: '0.4rem 0.7rem',
                  border: '1px solid #2a3142' }}>

      {/* Clique no mapa → sempre adiciona waypoint */}
      <span style={{ fontSize: '0.72rem', color: '#4b5563', fontFamily: 'monospace' }}>
        clique = ＋waypoint
      </span>

      <div style={{ width: '1px', height: '20px', background: '#2a3142', margin: '0 0.2rem' }} />

      {/* Centrar — disponível sempre */}
      <button onClick={onCenter}
        style={{ background: 'transparent', color: '#6b7280', border: '1.5px solid #2a3142',
                 borderRadius: '6px', padding: '0.3rem 0.65rem', fontSize: '0.75rem',
                 fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
        ⊞ Centrar
      </button>

      {/* Planta / Salvar */}
      <button onClick={onToggleFloor}
        style={{ background: showFloor ? 'rgba(110,231,183,0.1)' : 'transparent',
                 color: showFloor ? '#6ee7b7' : '#6b7280',
                 border: `1.5px solid ${showFloor ? '#6ee7b7' : '#2a3142'}`,
                 borderRadius: '6px', padding: '0.3rem 0.65rem', fontSize: '0.75rem',
                 fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
        🏭 {savedMapMeta ? 'Warehouse' : 'Mapa'}
      </button>

      {showFloor && (
        <input type="range" min="0" max="1" step="0.05" value={floorOpacity}
          aria-label="Opacidade da planta de fundo"
          onChange={e => onFloorOpacityChange(parseFloat(e.target.value))}
          style={{ width: '56px', accentColor: '#6ee7b7', cursor: 'pointer' }} />
      )}

      {mapOk && (
        <button onClick={onSave} disabled={savingMap}
          style={{ background: 'transparent',
                   color: saveMsg === 'ok' ? '#6ee7b7' : saveMsg === 'erro' ? '#f87171' : '#6366f1',
                   border: `1.5px solid ${saveMsg === 'ok' ? '#6ee7b7' : saveMsg === 'erro' ? '#f87171' : '#6366f1'}`,
                   borderRadius: '6px', padding: '0.3rem 0.65rem', fontSize: '0.75rem',
                   fontWeight: 600, cursor: savingMap ? 'not-allowed' : 'pointer',
                   opacity: savingMap ? 0.6 : 1, fontFamily: 'inherit' }}>
          {savingMap ? '⏳' : saveMsg === 'ok' ? '✓ Salvo' : saveMsg === 'erro' ? '✗ Erro' : '💾 Salvar'}
        </button>
      )}

      {/* Coordenadas de hover */}
      <div style={{ marginLeft: 'auto', fontFamily: 'monospace', fontSize: '0.72rem',
                    color: hoverCoord ? '#93c5fd' : '#374151', minWidth: '120px', textAlign: 'right' }}>
        {hoverCoord
          ? `x ${hoverCoord.x.toFixed(2)}  y ${hoverCoord.y.toFixed(2)}`
          : mapOk ? 'scroll=zoom  btn2=pan' : <span style={{ color: '#fbbf24' }}>⏳ aguardando SLAM…</span>
        }
      </div>
    </div>
  )
}
