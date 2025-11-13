import tkinter as tk
from tkinter import font
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# Importa a "cola" para unir Matplotlib e Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- 1. Variáveis Globais (Como antes) ---
posicao_target = {'x': 0.0, 'y': 0.0, 'z': 0.0}
posicao_random = {'x': 5.0, 'y': 5.0, 'z': 5.0}

# --- 2. Criação da Janela Principal (AGORA COM TKINTER) ---
# 'root' é a nossa janela principal da aplicação
root = tk.Tk()
root.title("Painel de Controle Interativo")

# --- 3. Configuração dos Gráficos Matplotlib (Como antes) ---
# A 'figura' agora é criada sem 'plt.subplots' para melhor integração
fig = plt.Figure(figsize=(12, 5))
(ax_xy, ax_z) = fig.subplots(1, 2)

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

# --- 4. Criar os Plots (Como antes) ---
plot_target_xy, = ax_xy.plot([posicao_target['x']], [posicao_target['y']], 'ro', label='Target')
plot_random_xy, = ax_xy.plot([posicao_random['x']], [posicao_random['y']], 'bo', label='Random')
ax_xy.legend()

bar_container = ax_z.bar([0, 1], [posicao_target['z'], posicao_random['z']], color=['red', 'blue'])
barra_target_z = bar_container[0]
barra_random_z = bar_container[1]

# --- 5. "Embutir" o Gráfico no TKINTER ---
# Esta é a parte mágica: cria um 'canvas' do Tkinter a partir da 'fig'
canvas = FigureCanvasTkAgg(fig, master=root)
# 'pack' é o comando do Tkinter para colocar o widget na janela
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# --- 6. Criar os Painéis de Controle (O SEU PEDIDO) ---

# Cria um 'frame' principal para os controles, abaixo do gráfico
controls_frame = tk.Frame(root)
controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

# --- "Caixa Verde" (Esquerda) - Input do Target ---
frame_target = tk.LabelFrame(controls_frame, text="Definir Target")
frame_target.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

# Widgets de Texto para o Target
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

# StringVars são variáveis do Tkinter que atualizam 'Labels' automaticamente
str_random_x = tk.StringVar(value="0.00")
str_random_y = tk.StringVar(value="0.00")
str_random_z = tk.StringVar(value="0.00")

# Labels para mostrar os valores
tk.Label(frame_random, text="X:").grid(row=0, column=0, padx=2, pady=2)
tk.Label(frame_random, textvariable=str_random_x, width=8, relief="sunken").grid(row=0, column=1)

tk.Label(frame_random, text="Y:").grid(row=0, column=2, padx=2, pady=2)
tk.Label(frame_random, textvariable=str_random_y, width=8, relief="sunken").grid(row=0, column=3)

tk.Label(frame_random, text="Z:").grid(row=0, column=4, padx=2, pady=2)
tk.Label(frame_random, textvariable=str_random_z, width=8, relief="sunken").grid(row=0, column=5)


# --- 7. Funções "Cola" e Lógica Atualizada ---

# Função para atualizar os campos de texto com os valores do 'target'
def update_target_entries():
    # Limpa a caixa e insere o novo valor
    entry_target_x.delete(0, tk.END)
    entry_target_x.insert(0, f"{posicao_target['x']:.2f}")
    
    entry_target_y.delete(0, tk.END)
    entry_target_y.insert(0, f"{posicao_target['y']:.2f}")
    
    entry_target_z.delete(0, tk.END)
    entry_target_z.insert(0, f"{posicao_target['z']:.2f}")

# Função para LER os campos de texto e atualizar a variável 'target'
def apply_target_from_entries():
    try:
        # Pega o texto da caixa (Entry) e converte para float
        x = float(entry_target_x.get())
        y = float(entry_target_y.get())
        z = float(entry_target_z.get())
        
        # Atualiza a variável global
        posicao_target['x'] = x
        posicao_target['y'] = y
        posicao_target['z'] = z
        
        print(f"Target atualizado via texto: {posicao_target}")
    except ValueError:
        print("Erro: Entrada de texto inválida. Use apenas números.")
        # Se der erro, re-sincroniza as caixas com o valor antigo
        update_target_entries()

# Adiciona um botão "Aplicar" no frame do Target
btn_apply = tk.Button(frame_target, text="Aplicar", command=apply_target_from_entries)
btn_apply.grid(row=0, column=6, padx=5)


# --- Função de Clique (Atualizada) ---
def ao_clicar(event):
    if event.inaxes == ax_xy:
        x, y = event.xdata, event.ydata
        if x is None or y is None: return 
        posicao_target['x'] = x
        posicao_target['y'] = y
    elif event.inaxes == ax_z:
        z = event.ydata
        if z is None: return 
        z = max(-10, min(10, z))
        posicao_target['z'] = z
    else:
        return
    
    # NOVO: Após o clique, atualiza as caixas de texto
    update_target_entries()
    # Não precisa mais do draw_idle(), a animação cuida disso


# --- Função de Animação (Atualizada) ---
def update(frame):
    # 1. Atualiza 'random' (como antes)
    posicao_random['x'] += random.uniform(-0.5, 0.5)
    posicao_random['y'] += random.uniform(-0.5, 0.5)
    posicao_random['z'] += random.uniform(-0.5, 0.5)
    for eixo in ['x', 'y', 'z']:
        posicao_random[eixo] = max(-10, min(10, posicao_random[eixo]))

    # 2. Atualiza os plots do 'random' (como antes)
    plot_random_xy.set_data([posicao_random['x']], [posicao_random['y']])
    barra_random_z.set_height(posicao_random['z'])

    # 3. NOVO: Atualiza os labels de texto do 'random'
    str_random_x.set(f"{posicao_random['x']:.2f}")
    str_random_y.set(f"{posicao_random['y']:.2f}")
    str_random_z.set(f"{posicao_random['z']:.2f}")
    
    # 4. Atualiza os plots do 'target' (como antes)
    # A 'posicao_target' pode ter sido mudada pelo clique OU pelo texto
    plot_target_xy.set_data([posicao_target['x']], [posicao_target['y']])
    barra_target_z.set_height(posicao_target['z'])
    
    # 5. Print contínuo (como antes)
    print(f"Target: {posicao_target}  |  Random: {posicao_random}")
    
    return plot_random_xy, barra_random_z, plot_target_xy, barra_target_z

# --- 8. Iniciar a Aplicação ---

# Conecta o evento de clique (como antes)
canvas.mpl_connect('button_press_event', ao_clicar)

# Inicia a animação (como antes)
ani = animation.FuncAnimation(fig, update, interval=100, blit=True)

# Coloca os valores iniciais nas caixas de texto do 'target'
update_target_entries()

# NOVO: Inicia o 'loop' principal do TKINTER (substitui o plt.show())
tk.mainloop()

print("Janela fechada.")