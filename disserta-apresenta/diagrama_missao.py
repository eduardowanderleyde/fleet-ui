import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

RED, DARK, MID, LIGHT, GREEN = '#DB1E2F', '#333333', '#666666', '#F3F4F6', '#2E7D32'
plt.rcParams['font.family'] = 'Arial'

# --sem-titulo: versão para slide/dissertação (o título fica no slide ou na legenda da figura)
SEM_TITULO = '--sem-titulo' in sys.argv
TOP = 5.6 if SEM_TITULO else 6.4
fig = plt.figure(figsize=(13.33, TOP), dpi=200)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 13.33); ax.set_ylim(0, TOP); ax.axis('off')

def box(x, y, w, h, fc=LIGHT, ec='#D0D3D9', ls='-', lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.12',
                                fc=fc, ec=ec, ls=ls, lw=lw))

def arrow(x0, x1, y, ls='-'):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle='-|>', mutation_scale=22,
                                 color=MID, lw=2, ls=ls))

if not SEM_TITULO:
    ax.text(0.45, 6.0, 'Como funciona uma missão robótica no Fleet UI', fontsize=22, color=DARK, va='center')

W, H, Y = 2.85, 3.55, 1.95
xs = [0.45, 3.62, 6.79, 9.96]
stages = [
    ('1', 'Missão em português', 'o pesquisador escreve', None,
     ['“Durante a ronda dos três', 'corredores do sul, o tb2 parou', 'com falha. O tb1 já terminou o', 'central. Realoque o que falta.”'], 'italic'),
    ('2', 'Interpretar', 'LLM (Claude)', None,
     ['Quais zonas faltam?', '  corredor oeste, corredor leste', 'Quem pode ir?', '  ✓ tb1, tb3 (MUUT)', '  ✗ tb2 (com falha)', '  ✗ tb4 (FUUT, só observa)'], 'normal'),
    ('3', 'Decidir quem faz o quê', 'cálculo de caminho (ótimo)', None,
     ['Distância real pelo mapa,', 'contornando estantes', 'Testa todas as divisões e', 'escolhe a que termina antes', '  tb1 → corredor leste', '  tb3 → corredor oeste'], 'normal'),
    ('4', 'Executar', 'Nav2 no Gazebo (Fase 2)', 'pendente',
     ['Cada robô percorre', 'suas zonas', 'Grava os sensores (MCAP)', 'Mede tempo real e', 'repetibilidade (RMSE)'], 'normal'),
]
for i, (num, title, sub, tag, lines, style) in enumerate(stages):
    x = xs[i]; pending = tag is not None
    box(x, Y, W, H, fc='white' if pending else LIGHT, ec=MID if pending else '#D0D3D9', ls=(0, (4, 3)) if pending else '-')
    ax.add_patch(plt.Circle((x + 0.38, Y + H - 0.38), 0.24, color=RED if not pending else MID))
    ax.text(x + 0.38, Y + H - 0.38, num, color='white', fontsize=14, ha='center', va='center', fontweight='bold')
    ax.text(x + 0.75, Y + H - 0.30, title, fontsize=13, fontweight='bold', color=DARK, va='center')
    ax.text(x + 0.75, Y + H - 0.62, sub, fontsize=10.5, color=RED if not pending else MID, va='center')
    for k, line in enumerate(lines):
        color = DARK
        if line.strip().startswith('✗'): color = RED
        if line.strip().startswith('✓') or '→' in line: color = GREEN
        sym = line.strip()[:1] in ('✓', '✗')
        ax.text(x + 0.25, Y + H - 1.10 - k * 0.34, line, fontsize=11, color=color, va='center',
                style=style, fontweight='bold' if '→' in line else 'normal',
                fontfamily='Segoe UI Symbol' if sym else 'Arial')
    if i < 3:
        arrow(x + W + 0.02, xs[i + 1] - 0.02, Y + H / 2, ls='--' if i == 2 else '-')

# faixa de resultados
ax.text(0.45, 1.55, 'O que o piloto mediu (15 missões, 200 decisões)', fontsize=13, fontweight='bold', color=DARK, va='center')
res = [
    ('Painel atual (ordem fixa)', 'até +106% acima do ótimo', RED),
    ('LLM só com o mapa', 'entende 100%, mas erra até +54% no espaço\ne muda de resposta (5/10 missões estáveis)', RED),
    ('LLM com as distâncias reais', 'ótimo em 50/50 (mesmo custo\nem todas as repetições)', GREEN),
]
rw = 4.02
for i, (t, d, c) in enumerate(res):
    x = 0.45 + i * (rw + 0.15)
    box(x, 0.2, rw, 1.1, fc='white', ec=c, lw=1.6)
    ax.text(x + 0.2, 1.02, t, fontsize=11.5, fontweight='bold', color=c, va='center')
    ax.text(x + 0.2, 0.58, d, fontsize=10.5, color=DARK, va='center', linespacing=1.3)

ax.text(12.81, 1.55 if SEM_TITULO else 6.0, '—— feito (Fase 1)    - - - próximo passo (Fase 2)', fontsize=9.5, color=MID, ha='right', va='center')
if SEM_TITULO:
    fig.savefig('diagrama_missao_slide.png', facecolor='white')
    fig.savefig('../dissertacao/figuras/diagrama_missao.pdf', facecolor='white')
else:
    fig.savefig('diagrama_missao.png', facecolor='white')
    fig.savefig('diagrama_missao.svg', facecolor='white')
print('ok')
