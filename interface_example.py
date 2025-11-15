import tkinter as tk
from tkinter import font
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# Importa a "cola" para unir Matplotlib e Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec  # Import para a grade

# ##################################################################
# --- 0. CONFIGURAÇÕES GLOBAIS ---
# Altere qualquer valor aqui para customizar o painel
# ##################################################################

# --- Geral ---
COR_TARGET = 'red'          # Cor do ponto/barra do Target
COR_RANDOM = 'blue'         # Cor do ponto/barra do Random

# --- Dimensões Gerais ---
# Largura e altura totais da área de gráficos (em "polegadas" do matplotlib)
TAMANHO_FIGURA_LARGURA = 12
TAMANHO_FIGURA_ALTURA = 5

# --- Controle XY (Gráfico da Esquerda) ---
XY_LIM_MIN = -5.0           # Valor mínimo dos eixos X e Y
XY_LIM_MAX = 5.0           # Valor máximo dos eixos X e Y
# A largura é definida pela proporção abaixo
PROPORCAO_LARGURA_XY = 2    # O gráfico XY será 2x mais largo que o Z

# --- Controle Z (Gráfico da Direita) ---
Z_LIM_MIN = 0.0            # Valor mínimo do eixo Z
Z_LIM_MAX = 5.0            # Valor máximo do eixo Z
# A largura é definida pela proporção abaixo
PROPORCAO_LARGURA_Z = 1     # Proporção de largura
LARGURA_BARRA_Z = 0.4       # Largura de cada barra (0.0 a 1.0)


# ##################################################################
# --- Fim das Configurações ---
# O restante do código usa as variáveis acima
# ##################################################################


# --- 1. Variáveis Globais (Iniciais) ---
posicao_target = {'x': 0.0, 'y': 0.0, 'z': 0.0}
posicao_random = {'x': 5.0, 'y': 5.0, 'z': 5.0}

# --- 2. Criação da Janela Principal (TKINTER) ---
root = tk.Tk()
root.title("Painel de Controle Interativo")

# --- 3. Configuração dos Gráficos Matplotlib (Usando Configs) ---
fig = plt.Figure(figsize=(TAMANHO_FIGURA_LARGURA, TAMANHO_FIGURA_ALTURA))

# Cria a grade com as proporções definidas
gs = GridSpec(1, 2, width_ratios=[PROPORCAO_LARGURA_XY, PROPORCAO_LARGURA_Z], figure=fig)

# Adiciona os plots na grade
ax_xy = fig.add_subplot(gs[0, 0])  # Ocupa a primeira célula (larga)
ax_z = fig.add_subplot(gs[0, 1])   # Ocupa a segunda célula (estreita)

# --- Configuração do Gráfico 1: Plano XY (Esquerda) ---
ax_xy.set_title("Controle XY: Clique aqui")
ax_xy.set_xlim(XY_LIM_MIN, XY_LIM_MAX)
ax_xy.set_ylim(XY_LIM_MIN, XY_LIM_MAX)
ax_xy.grid(True)
ax_xy.axhline(0, color='black', linewidth=0.5)
ax_xy.axvline(0, color='black', linewidth=0.5)

# --- Configuração do Gráfico 2: Eixo Z (Direita) ---
ax_z.set_title("Controle Z: Clique aqui")
ax_z.set_ylim(Z_LIM_MIN, Z_LIM_MAX) 
ax_z.set_ylabel("Valor de Z")
ax_z.set_xticks([0, 1])
ax_z.set_xticklabels(["Target", "Random"], rotation=30)
ax_z.grid(True, axis='y') 
ax_z.axhline(0, color='black', linewidth=0.5)

# --- 4. Criar os Plots (Usando Configs) ---
plot_target_xy, = ax_xy.plot([posicao_target['x']], [posicao_target['y']], 
                           marker='o', color=COR_TARGET, label='Target')
plot_random_xy, = ax_xy.plot([posicao_random['x']], [posicao_random['y']], 
                           marker='o', color=COR_RANDOM, label='Random')
ax_xy.legend()

bar_container = ax_z.bar([0, 1], [posicao_target['z'], posicao_random['z']], 
                         color=[COR_TARGET, COR_RANDOM], width=LARGURA_BARRA_Z)
barra_target_z = bar_container[0]
barra_random_z = bar_container[1]

fig.tight_layout(pad=1.0) 

# --- 5. "Embutir" o Gráfico no TKINTER ---
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# --- 6. Criar os Painéis de Controle ---
controls_frame = tk.Frame(root)
controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

# --- "Caixa Verde" (Esquerda) - Input do Target ---
frame_target = tk.LabelFrame(controls_frame, text="Definir Target")
frame_target.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

tk.Label(frame_target, text="X:").grid(row=0, column=0, padx=2, pady=2)
entry_target_x = tk.Entry(frame_target, width=8)
entry_target_x.grid(row=0, column=1)

tk.Label(frame_target, text="Y:").grid(row=0, column=2, padx=2, pady=2)
entry_target_y = tk.Entry(frame_target, width=8)
entry_target_y.grid(row=0, column=3)

tk.Label(frame_target, text="Z:").grid(row=0, column=4, padx=2, pady=2)
entry_target_z = tk.Entry(frame_target, width=8)
entry_target_z.grid(row=0, column=5)

# --- "Caixa Amarela" (Direita) - Display do Random ---
frame_random = tk.LabelFrame(controls_frame, text="Posição Random")
frame_random.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

str_random_x = tk.StringVar(value="0.00")
str_random_y = tk.StringVar(value="0.00")
str_random_z = tk.StringVar(value="0.00")

tk.Label(frame_random, text="X:").grid(row=0, column=0, padx=2, pady=2)
tk.Label(frame_random, textvariable=str_random_x, width=8, relief="sunken").grid(row=0, column=1)

tk.Label(frame_random, text="Y:").grid(row=0, column=2, padx=2, pady=2)
tk.Label(frame_random, textvariable=str_random_y, width=8, relief="sunken").grid(row=0, column=3)

tk.Label(frame_random, text="Z:").grid(row=0, column=4, padx=2, pady=2)
tk.Label(frame_random, textvariable=str_random_z, width=8, relief="sunken").grid(row=0, column=5)


# --- 7. Funções "Cola" e Lógica (Usando Configs) ---
def update_target_entries():
    entry_target_x.delete(0, tk.END)
    entry_target_x.insert(0, f"{posicao_target['x']:.2f}")
    
    entry_target_y.delete(0, tk.END)
    entry_target_y.insert(0, f"{posicao_target['y']:.2f}")
    
    entry_target_z.delete(0, tk.END)
    entry_target_z.insert(0, f"{posicao_target['z']:.2f}")

def apply_target_from_entries():
    try:
        x = float(entry_target_x.get())
        y = float(entry_target_y.get())
        z = float(entry_target_z.get())
        
        # Limita os valores aos definidos na configuração
        posicao_target['x'] = max(XY_LIM_MIN, min(XY_LIM_MAX, x))
        posicao_target['y'] = max(XY_LIM_MIN, min(XY_LIM_MAX, y))
        posicao_target['z'] = max(Z_LIM_MIN, min(Z_LIM_MAX, z))
        
        print(f"Target atualizado via texto: {posicao_target}")
        update_target_entries() # Re-sincroniza caso o valor tenha sido limitado
    except ValueError:
        print("Erro: Entrada de texto inválida. Use apenas números.")
        update_target_entries()

btn_apply = tk.Button(frame_target, text="Aplicar", command=apply_target_from_entries)
btn_apply.grid(row=0, column=6, padx=5)

def ao_clicar(event):
    if event.inaxes == ax_xy:
        x, y = event.xdata, event.ydata
        if x is None or y is None: return 
        # Limita o clique aos valores definidos na configuração
        posicao_target['x'] = max(XY_LIM_MIN, min(XY_LIM_MAX, x))
        posicao_target['y'] = max(XY_LIM_MIN, min(XY_LIM_MAX, y))
    elif event.inaxes == ax_z:
        z = event.ydata
        if z is None: return 
        # Limita o clique aos valores definidos na configuração
        posicao_target['z'] = max(Z_LIM_MIN, min(Z_LIM_MAX, z))
    else:
        return
    
    update_target_entries()

def update(frame):
    # --- Lógica do Random (Usando Configs) ---
    posicao_random['x'] += random.uniform(-0.5, 0.5)
    posicao_random['y'] += random.uniform(-0.5, 0.5)
    posicao_random['z'] += random.uniform(-0.5, 0.5)
    # Limita o movimento aos valores definidos na configuração
    posicao_random['x'] = max(XY_LIM_MIN, min(XY_LIM_MAX, posicao_random['x']))
    posicao_random['y'] = max(XY_LIM_MIN, min(XY_LIM_MAX, posicao_random['y']))
    posicao_random['z'] = max(Z_LIM_MIN, min(Z_LIM_MAX, posicao_random['z']))

    # --- Atualização dos Visuais ---
    plot_random_xy.set_data([posicao_random['x']], [posicao_random['y']])
    barra_random_z.set_height(posicao_random['z'])

    str_random_x.set(f"{posicao_random['x']:.2f}")
    str_random_y.set(f"{posicao_random['y']:.2f}")
    str_random_z.set(f"{posicao_random['z']:.2f}")
    
    plot_target_xy.set_data([posicao_target['x']], [posicao_target['y']])
    barra_target_z.set_height(posicao_target['z'])
    
    return plot_random_xy, barra_random_z, plot_target_xy, barra_target_z

# --- 8. Iniciar a Aplicação ---
canvas.mpl_connect('button_press_event', ao_clicar)
ani = animation.FuncAnimation(fig, update, interval=100, blit=True)
update_target_entries()
tk.mainloop()

print("Janela fechada.")