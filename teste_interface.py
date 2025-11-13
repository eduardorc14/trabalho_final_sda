import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# --- 1. Variáveis Globais ---
posicao_target = {'x': 0, 'y': 0, 'z': 0}
posicao_random = {'x': 5, 'y': 5, 'z': 5}

# --- 2. Configuração da Janela e Gráficos ---
fig, (ax_xy, ax_z) = plt.subplots(1, 2, figsize=(12, 6))

# --- Gráfico 1: Plano XY (Esquerda) ---
ax_xy.set_title("Controle XY: Clique aqui")
ax_xy.set_xlim(-10, 10)
ax_xy.set_ylim(-10, 10)
ax_xy.grid(True)
ax_xy.axhline(0, color='black', linewidth=0.5)
ax_xy.axvline(0, color='black', linewidth=0.5)

# --- Gráfico 2: Eixo Z (Direita) ---
ax_z.set_title("Controle Z: Clique aqui")
ax_z.set_ylim(-10, 10) 
ax_z.set_ylabel("Valor de Z")
ax_z.set_xticks([0, 1])
ax_z.set_xticklabels(["Target (Vermelho)", "Random (Azul)"])
ax_z.grid(True, axis='y') 
ax_z.axhline(0, color='black', linewidth=0.5)

# --- 3. Criar os Plots ---
# Gráfico XY
plot_target_xy, = ax_xy.plot([posicao_target['x']], [posicao_target['y']], 'ro', label='Target')
plot_random_xy, = ax_xy.plot([posicao_random['x']], [posicao_random['y']], 'bo', label='Random')
ax_xy.legend()

# Gráfico Z (Barras)
bar_container = ax_z.bar([0, 1], [posicao_target['z'], posicao_random['z']], color=['red', 'blue'])
barra_target_z = bar_container[0]
barra_random_z = bar_container[1]


# --- 4. Função de Clique (Prints removidos daqui) ---
def ao_clicar(event):
    
    # --- Se o clique foi no gráfico XY (Esquerda) ---
    if event.inaxes == ax_xy:
        x, y = event.xdata, event.ydata
        if x is None or y is None: return 
        
        posicao_target['x'] = x
        posicao_target['y'] = y
        
        # A atualização visual ainda é necessária,
        # mas agora a 'update' vai garantir que ela permaneça
        plot_target_xy.set_data([posicao_target['x']], [posicao_target['y']])

    # --- Se o clique foi no gráfico Z (Direita) ---
    elif event.inaxes == ax_z:
        z = event.ydata
        if z is None: return 
        
        z = max(-10, min(10, z))
        posicao_target['z'] = z
        barra_target_z.set_height(z)

    else:
        return
    
    # Podemos usar draw_idle() para dar uma resposta mais rápida ao clique
    # antes do próximo frame da animação
    fig.canvas.draw_idle()

# --- 5. Função de Animação (COM AS CORREÇÕES) ---
def update(frame):
    # 1. Atualiza a variável 'random'
    posicao_random['x'] += random.uniform(-0.5, 0.5)
    posicao_random['y'] += random.uniform(-0.5, 0.5)
    posicao_random['z'] += random.uniform(-0.5, 0.5)

    # 2. Limita o movimento
    for eixo in ['x', 'y', 'z']:
        posicao_random[eixo] = max(-10, min(10, posicao_random[eixo]))

    # 3. Atualiza os gráficos do 'random'
    plot_random_xy.set_data([posicao_random['x']], [posicao_random['y']])
    barra_random_z.set_height(posicao_random['z'])

    # --- CORREÇÃO 2: PRINT CONTÍNUO ---
    # Imprime os valores do target e random a todo instante
    print(f"Target: x={posicao_target['x']:.2f}, y={posicao_target['y']:.2f}, z={posicao_target['z']:.2f}  |  "
          f"Random: x={posicao_random['x']:.2f}, y={posicao_random['y']:.2f}, z={posicao_random['z']:.2f}")

    # --- CORREÇÃO 1: CORRIGE O BUG VISUAL ---
    # Retorna TODOS os objetos que são animados (target e random)
    return plot_random_xy, barra_random_z, plot_target_xy, barra_target_z

# --- 6. Conectar Eventos e Iniciar ---
fig.canvas.mpl_connect('button_press_event', ao_clicar)
# O 'blit=True' agora vai funcionar corretamente
ani = animation.FuncAnimation(fig, update, interval=100, blit=True)

plt.tight_layout()
plt.show()

print("Janela fechada.")