import { color } from '../styles/tokens'

export default function MapToolbar({
  showFloor, onToggleFloor, savedMapMeta,
  floorOpacity, onFloorOpacityChange,
  mapOk, savingMap, saveMsg, onSave,
  onCenter, hoverCoord,
}) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.5rem', flexShrink: 0,
                  background: color.bgPanel, borderRadius: '8px', padding: '0.4rem 0.7rem',
                  border: `1px solid ${color.border}` }}>

      {/* Clique no mapa → sempre adiciona waypoint */}
      <span style={{ fontSize: '0.72rem', color: color.textFaint, fontFamily: 'monospace' }}>
        clique = ＋waypoint
      </span>

      <div style={{ width: '1px', height: '20px', background: color.border, margin: '0 0.2rem' }} />

      {/* Centrar — disponível sempre */}
      <button onClick={onCenter}
        style={{ background: 'transparent', color: color.textFaint2, border: `1.5px solid ${color.border}`,
                 borderRadius: '6px', padding: '0.3rem 0.65rem', fontSize: '0.75rem',
                 fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
        ⊞ Centrar
      </button>

      {/* Planta / Salvar */}
      <button onClick={onToggleFloor}
        style={{ background: showFloor ? 'rgba(110,231,183,0.1)' : 'transparent',
                 color: showFloor ? color.success : color.textFaint2,
                 border: `1.5px solid ${showFloor ? color.success : color.border}`,
                 borderRadius: '6px', padding: '0.3rem 0.65rem', fontSize: '0.75rem',
                 fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
        🏭 {savedMapMeta ? 'Warehouse' : 'Mapa'}
      </button>

      {showFloor && (
        <input type="range" min="0" max="1" step="0.05" value={floorOpacity}
          aria-label="Opacidade da planta de fundo"
          onChange={e => onFloorOpacityChange(parseFloat(e.target.value))}
          style={{ width: '56px', accentColor: color.success, cursor: 'pointer' }} />
      )}

      {mapOk && (
        <button onClick={onSave} disabled={savingMap}
          style={{ background: 'transparent',
                   color: saveMsg === 'ok' ? color.success : saveMsg === 'erro' ? color.danger : color.indigo,
                   border: `1.5px solid ${saveMsg === 'ok' ? color.success : saveMsg === 'erro' ? color.danger : color.indigo}`,
                   borderRadius: '6px', padding: '0.3rem 0.65rem', fontSize: '0.75rem',
                   fontWeight: 600, cursor: savingMap ? 'not-allowed' : 'pointer',
                   opacity: savingMap ? 0.6 : 1, fontFamily: 'inherit' }}>
          {savingMap ? '⏳' : saveMsg === 'ok' ? '✓ Salvo' : saveMsg === 'erro' ? '✗ Erro' : '💾 Salvar'}
        </button>
      )}

      {/* Coordenadas de hover */}
      <div style={{ marginLeft: 'auto', fontFamily: 'monospace', fontSize: '0.72rem',
                    color: hoverCoord ? color.blue : color.textFaint3, minWidth: '120px', textAlign: 'right' }}>
        {hoverCoord
          ? `x ${hoverCoord.x.toFixed(2)}  y ${hoverCoord.y.toFixed(2)}`
          : mapOk ? 'scroll=zoom  btn2=pan' : <span style={{ color: color.warning }}>⏳ aguardando SLAM…</span>
        }
      </div>
    </div>
  )
}
