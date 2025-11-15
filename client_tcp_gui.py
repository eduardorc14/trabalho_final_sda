# Nome do arquivo: Interface_CLP_Completa.py
#
# Combina a GUI de controle (Matplotlib + Tkinter) com o
# cliente TCP de logging e controle.
#
# A GUI define 'posicao_target'.
# O CLP (servidor) envia a 'posicao_drone' (ex-random).
#

import tkinter as tk
from tkinter import font
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import socket
import threading
import time
import datetime
import sys

# Importa a "cola" para unir Matplotlib e Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec

# ##################################################################
# --- 0. CONFIGURAÇÕES GLOBAIS ---
# ##################################################################

# --- Configs de Rede ---
CLP_HOST = '127.0.0.1'
CLP_PORT = 65432
LOG_FILENAME = "historiador.txt"
# Frequência de envio (segundos). 0.1 = 10x por segundo
TAXA_ENVIO_TARGET = 0.1

# --- Configs de Aparência ---
COR_TARGET = 'red'
COR_DRONE = 'blue'  # Renomeado de COR_RANDOM
TAMANHO_FIGURA_LARGURA = 12
TAMANHO_FIGURA_ALTURA = 5
XY_LIM_MIN, XY_LIM_MAX = -10.0, 10.0
Z_LIM_MIN, Z_LIM_MAX = -10.0, 10.0
PROPORCAO_LARGURA_XY = 2
PROPORCAO_LARGURA_Z = 1
LARGURA_BARRA_Z = 0.4

# ##################################################################
# --- 1. ESTADO GLOBAL COMPARTILHADO ---
# (Variáveis usadas por múltiplas threads)
# ##################################################################

# Posição do Alvo (controlada pela GUI, lida pela sender_thread)
posicao_target = {'x': 0.0, 'y': 0.0, 'z': 0.0}
target_lock = threading.Lock()

# Posição do Drone (recebida pela receiver_thread, lida pela GUI)
posicao_drone = {'x': 5.0, 'y': 5.0, 'z': 5.0}
drone_lock = threading.Lock()

# Controle de execução
running = threading.Event()
running.set()
log_lock = threading.Lock()

# ##################################################################
# --- 2. WIDGETS GLOBAIS DA GUI ---
# (Definidos como None, inicializados em start_gui)
# ##################################################################
root_window = None
entry_target_x, entry_target_y, entry_target_z = None, None, None
str_drone_x, str_drone_y, str_drone_z = None, None, None
plot_target_xy, plot_drone_xy = None, None
barra_target_z, barra_drone_z = None, None

# ##################################################################
# --- 3. FUNÇÕES DA INTERFACE GRÁFICA (GUI) ---
# (Rodam na Thread Principal)
# ##################################################################

def start_gui():
    """Cria e inicia a interface gráfica principal do Tkinter."""
    global root_window, fig, canvas, ani
    global entry_target_x, entry_target_y, entry_target_z
    global str_drone_x, str_drone_y, str_drone_z
    global plot_target_xy, plot_drone_xy
    global barra_target_z, barra_drone_z

    print("[GUI] Iniciando interface gráfica...")
    root_window = tk.Tk()
    root_window.title("Painel de Controle Interativo - Cliente CLP")

    # --- Configuração dos Gráficos Matplotlib ---
    fig = plt.Figure(figsize=(TAMANHO_FIGURA_LARGURA, TAMANHO_FIGURA_ALTURA))
    gs = GridSpec(1, 2, width_ratios=[PROPORCAO_LARGURA_XY, PROPORCAO_LARGURA_Z], figure=fig)
    ax_xy = fig.add_subplot(gs[0, 0])
    ax_z = fig.add_subplot(gs[0, 1])

    ax_xy.set_title("Controle XY: Clique aqui")
    ax_xy.set_xlim(XY_LIM_MIN, XY_LIM_MAX)
    ax_xy.set_ylim(XY_LIM_MIN, XY_LIM_MAX)
    ax_xy.grid(True)
    ax_xy.axhline(0, color='black', linewidth=0.5)
    ax_xy.axvline(0, color='black', linewidth=0.5)

    ax_z.set_title("Controle Z: Clique aqui")
    ax_z.set_ylim(Z_LIM_MIN, Z_LIM_MAX)
    ax_z.set_ylabel("Valor de Z")
    ax_z.set_xticks([0, 1])
    ax_z.set_xticklabels(["Target", "Drone"], rotation=30)
    ax_z.grid(True, axis='y')
    ax_z.axhline(0, color='black', linewidth=0.5)

    # --- Criar os Plots ---
    with target_lock:
        t_pos = posicao_target.copy()
    with drone_lock:
        d_pos = posicao_drone.copy()

    plot_target_xy, = ax_xy.plot([t_pos['x']], [t_pos['y']],
                               marker='o', color=COR_TARGET, label='Target')
    plot_drone_xy, = ax_xy.plot([d_pos['x']], [d_pos['y']],
                               marker='o', color=COR_DRONE, label='Drone (Random)')
    ax_xy.legend()

    bar_container = ax_z.bar([0, 1], [t_pos['z'], d_pos['z']],
                             color=[COR_TARGET, COR_DRONE], width=LARGURA_BARRA_Z)
    barra_target_z = bar_container[0]
    barra_drone_z = bar_container[1]
    fig.tight_layout(pad=1.0)

    # --- "Embutir" o Gráfico no TKINTER ---
    canvas = FigureCanvasTkAgg(fig, master=root_window)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # --- Criar os Painéis de Controle ---
    controls_frame = tk.Frame(root_window)
    controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    # --- Caixa de Input do Target ---
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
    
    btn_apply = tk.Button(frame_target, text="Aplicar", command=apply_target_from_entries)
    btn_apply.grid(row=0, column=6, padx=5)

    # --- Caixa de Display do Drone (Random) ---
    frame_drone = tk.LabelFrame(controls_frame, text="Posição Drone (Recebida)")
    frame_drone.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
    
    str_drone_x = tk.StringVar(value="0.00")
    str_drone_y = tk.StringVar(value="0.00")
    str_drone_z = tk.StringVar(value="0.00")

    tk.Label(frame_drone, text="X:").grid(row=0, column=0, padx=2, pady=2)
    tk.Label(frame_drone, textvariable=str_drone_x, width=8, relief="sunken").grid(row=0, column=1)
    tk.Label(frame_drone, text="Y:").grid(row=0, column=2, padx=2, pady=2)
    tk.Label(frame_drone, textvariable=str_drone_y, width=8, relief="sunken").grid(row=0, column=3)
    tk.Label(frame_drone, text="Z:").grid(row=0, column=4, padx=2, pady=2)
    tk.Label(frame_drone, textvariable=str_drone_z, width=8, relief="sunken").grid(row=0, column=5)

    # --- Iniciar Animação e Loop ---
    canvas.mpl_connect('button_press_event', ao_clicar)
    ani = animation.FuncAnimation(fig, update_animation_frame, interval=100, blit=True)
    update_target_entries() # Coloca valores iniciais
    
    root_window.protocol("WM_DELETE_WINDOW", on_gui_closing) # Pega o clique no "X"
    print("[GUI] Interface iniciada. Rodando mainloop...")
    tk.mainloop()
    print("[GUI] Mainloop terminado.")

def on_gui_closing():
    """Chamada quando a janela da GUI é fechada."""
    print("[GUI] Janela fechada pelo usuário.")
    running.clear() # Sinaliza para todas as threads pararem
    if root_window:
        root_window.quit()
        root_window.destroy()

def update_target_entries():
    """Atualiza as caixas de texto com o valor da variável global."""
    global posicao_target, target_lock
    global entry_target_x, entry_target_y, entry_target_z

    with target_lock:
        t_pos = posicao_target.copy()
        
    if entry_target_x: # Verifica se os widgets já foram criados
        entry_target_x.delete(0, tk.END)
        entry_target_x.insert(0, f"{t_pos['x']:.2f}")
        entry_target_y.delete(0, tk.END)
        entry_target_y.insert(0, f"{t_pos['y']:.2f}")
        entry_target_z.delete(0, tk.END)
        entry_target_z.insert(0, f"{t_pos['z']:.2f}")

def apply_target_from_entries():
    """Lê as caixas de texto e atualiza a variável global."""
    global posicao_target, target_lock
    global entry_target_x, entry_target_y, entry_target_z
    
    try:
        x = float(entry_target_x.get())
        y = float(entry_target_y.get())
        z = float(entry_target_z.get())
        
        with target_lock:
            posicao_target['x'] = max(XY_LIM_MIN, min(XY_LIM_MAX, x))
            posicao_target['y'] = max(XY_LIM_MIN, min(XY_LIM_MAX, y))
            posicao_target['z'] = max(Z_LIM_MIN, min(Z_LIM_MAX, z))
            
        print(f"[GUI] Target atualizado via texto: {posicao_target}")
        update_target_entries() # Re-sincroniza
    except (ValueError, TypeError):
        print("[GUI] Erro: Entrada de texto inválida. Use apenas números.")
        update_target_entries()

def ao_clicar(event):
    """Chamada quando o gráfico Matplotlib é clicado."""
    global posicao_target, target_lock
    
    new_pos = {}
    if event.inaxes == event.canvas.figure.axes[0]: # ax_xy
        x, y = event.xdata, event.ydata
        if x is None or y is None: return 
        new_pos['x'] = max(XY_LIM_MIN, min(XY_LIM_MAX, x))
        new_pos['y'] = max(XY_LIM_MIN, min(XY_LIM_MAX, y))
    elif event.inaxes == event.canvas.figure.axes[1]: # ax_z
        z = event.ydata
        if z is None: return 
        new_pos['z'] = max(Z_LIM_MIN, min(Z_LIM_MAX, z))
    else:
        return
    
    with target_lock:
        posicao_target.update(new_pos)
    
    update_target_entries()

def update_animation_frame(frame):
    """Função da animação. Atualiza os visuais com dados das globais."""
    global posicao_drone, drone_lock
    global str_drone_x, str_drone_y, str_drone_z
    global plot_target_xy, plot_drone_xy
    global barra_target_z, barra_drone_z

    # 1. Pega os valores atuais das variáveis globais
    with target_lock:
        t_pos = posicao_target.copy()
    with drone_lock:
        d_pos = posicao_drone.copy()

    # 2. Atualiza os plots do 'drone' (ex-random)
    plot_drone_xy.set_data([d_pos['x']], [d_pos['y']])
    barra_drone_z.set_height(d_pos['z'])

    # 3. Atualiza os labels de texto do 'drone'
    if str_drone_x: # Verifica se os widgets já foram criados
        str_drone_x.set(f"{d_pos['x']:.2f}")
        str_drone_y.set(f"{d_pos['y']:.2f}")
        str_drone_z.set(f"{d_pos['z']:.2f}")
    
    # 4. Atualiza os plots do 'target'
    plot_target_xy.set_data([t_pos['x']], [t_pos['y']])
    barra_target_z.set_height(t_pos['z'])
    
    # 5. Retorna os objetos atualizados
    return plot_drone_xy, barra_drone_z, plot_target_xy, barra_target_z

# ##################################################################
# --- 4. FUNÇÕES DE REDE (TCP) ---
# (Rodam em Threads separadas)
# ##################################################################

def receiver_thread(s, log_file):
    """Recebe dados do CLP, atualiza 'posicao_drone' e escreve no log."""
    global running, posicao_drone, drone_lock, posicao_target, target_lock
    print("[Receiver] Iniciado e pronto para logar.")
    buffer = ""
    while running.is_set():
        try:
            data = s.recv(1024)
            if not data:
                print("\n[Receiver] Conexão perdida com o CLP.")
                break
            
            buffer += data.decode('utf-8')
            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                if not message: continue
                try:
                    parts = message.split(',')
                    ts_drone_str = parts[0]
                    dx, dy, dz = float(parts[1]), float(parts[2]), float(parts[3])
                    
                    # ATUALIZA A VARIÁVEL GLOBAL DO DRONE
                    with drone_lock:
                        posicao_drone['x'] = dx
                        posicao_drone['y'] = dy
                        posicao_drone['z'] = dz
                        
                    # Pega o target atual para o log
                    with target_lock:
                        t_pos = posicao_target.copy()
                    tx, ty, tz = t_pos['x'], t_pos['y'], t_pos['z']
                    
                    # Escreve no log
                    log_line = f"{ts_drone_str},{dx:.4f},{dy:.4f},{dz:.4f},{tx:.2f},{ty:.2f},{tz:.2f}\n"
                    with log_lock:
                        log_file.write(log_line)
                        
                except (ValueError, IndexError):
                    print(f"[Receiver] Mensagem mal formatada recebida: {message}")
                    pass
        except socket.timeout:
            continue 
        except (ConnectionResetError, OSError) as e:
            if running.is_set():
                print(f"\n[Receiver] Conexão perdida: {e}")
            break
            
    print("[Receiver] Parado.")
    running.clear() # Avisa as outras threads para pararem

def gui_sender_thread(s):
    """Envia 'posicao_target' para o CLP se ela mudar."""
    global running, posicao_target, target_lock
    
    print("[Sender] Iniciado. Monitorando 'posicao_target'...")
    last_sent = {}
    
    while running.is_set():
        try:
            with target_lock:
                target_to_send = posicao_target.copy()
                
            # Envia apenas se for diferente do último envio
            if target_to_send != last_sent:
                tx, ty, tz = target_to_send['x'], target_to_send['y'], target_to_send['z']
                
                timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
                message = f"{timestamp_str},{tx},{ty},{tz}\n" 
                
                s.sendall(message.encode('utf-8'))
                print(f"[Sender] ✅ Alvo {tx,ty,tz} enviado.")
                last_sent = target_to_send
                
            time.sleep(TAXA_ENVIO_TARGET) # Controla a taxa de envio
            
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            if running.is_set():
                print(f"❌ [Sender] Conexão perdida com o CLP: {e}")
            break
        except Exception as e:
            if running.is_set():
                print(f"❌ [Sender] Erro inesperado: {e}")
            break
            
    print("[Sender] Parado.")
    running.clear() # Avisa as outras threads para pararem

# ##################################################################
# --- 5. FUNÇÃO PRINCIPAL (MAIN) ---
# (Como solicitado, o 'main' agora é uma função)
# ##################################################################

def main():
    """Função principal: conecta, inicia threads e abre a GUI."""
    print(f"--- Cliente CLP GUI (Painel + Historiador) ---")
    s = None 
    recv_thread = None
    send_thread = None
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Conectando ao CLP em {CLP_HOST}:{CLP_PORT}...")
        s.connect((CLP_HOST, CLP_PORT))
        s.settimeout(1.0)
        print("Conectado!")
        
        with open(LOG_FILENAME, "w") as log_file:
            print(f"Salvando log em -> {LOG_FILENAME}")
            log_file.write("timestamp_iso,drone_x,drone_y,drone_z,target_x,target_y,target_z\n")
            
            # Inicia as threads de rede
            recv_thread = threading.Thread(target=receiver_thread, args=(s, log_file), daemon=True)
            send_thread = threading.Thread(target=gui_sender_thread, args=(s,), daemon=True)
            
            recv_thread.start()
            send_thread.start()
            
            # Inicia a GUI (esta função BLOQUEIA a thread main até a janela fechar)
            start_gui()
            
        print(f"Arquivo '{LOG_FILENAME}' salvo com sucesso.")

    except ConnectionRefusedError:
        print(f"\n❌ ERRO: Não foi possível conectar.")
        print(f"   Verifique se o 'CLP.py' está rodando na porta {CLP_PORT}.")
    except KeyboardInterrupt:
        print("\n[Main] Desligamento solicitado (Ctrl+C).")
    except Exception as e:
        if running.is_set():
            print(f"[Main] Erro inesperado: {e}")
    finally:
        print("[Main] Iniciando desligamento...")
        running.clear()
        if s: 
            s.close()
            print("[Main] Socket fechado.")
        
        # Espera as threads terminarem
        if recv_thread and recv_thread.is_alive():
            recv_thread.join(timeout=1.0)
        if send_thread and send_thread.is_alive():
            send_thread.join(timeout=1.0)
            
        print("[Main] Desligamento completo.")

# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    main()