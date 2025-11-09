# Nome do arquivo: CLP.py
# (Corrigido: Timestamps em ISO 8601)

import socket
import threading
import time
import datetime # <-- ADICIONADO
from opcua import Client, ua

# --- Configurações ---
OPC_UA_SERVER_URL = "opc.tcp://localhost:53530/OPCUA/SimulationServer"
TCP_SERVER_HOST = '127.0.0.1'
TCP_SERVER_PORT = 65432

# --- Buffers de Dados Compartilhados ---
data_lock = threading.Lock()
new_target_event = threading.Event()
current_drone_position = {'dx': 0.0, 'dy': 0.0, 'dz': 0.0}
new_target_received = {'tx': 0.0, 'ty': 0.0, 'tz': 0.0}
running = threading.Event()
running.set()

# --- Lógica de Conexão OPC-UA (Baseada no seu script) ---
def setup_opc_nodes(url=OPC_UA_SERVER_URL):
    client = Client(url)
    client.connect()
    print(f"[OPC Thread] Conectado a {url}")
    root = client.get_objects_node()
    drone_folder = None
    try:
        drone_folder = root.get_child(["3:Drone"])
    except Exception:
        for n in root.get_children():
            try:
                if n.get_browse_name().Name.lower() == "drone":
                    drone_folder = n
                    break
            except Exception: pass
    if drone_folder is None:
        raise RuntimeError("Pasta 'Drone' não encontrada no servidor OPC UA.")
    name_to_node = {}
    for v in drone_folder.get_children():
        try:
            nm = v.get_browse_name().Name.lower()
            name_to_node[nm] = v
        except Exception: pass
    nodes_map = {
        'dx': name_to_node.get("dronex"), 'dy': name_to_node.get("droney"),
        'dz': name_to_node.get("dronez"), 'tx': name_to_node.get("targetx"),
        'ty': name_to_node.get("targety"), 'tz': name_to_node.get("targetz")
    }
    if not all(nodes_map.values()):
        found = ", ".join(k for k, v in nodes_map.items() if v)
        raise RuntimeError(f"Não foi possível encontrar todas as 6 variáveis. Encontradas: [{found}]")
    print("[OPC Thread] Todos os 6 nós (dx, dy, dz, tx, ty, tz) foram encontrados.")
    return client, nodes_map

# --- Thread 1: Lógica OPC-UA ---
def opc_ua_thread():
    print("[OPC Thread] Iniciando...")
    opc_client = None
    try:
        opc_client, nodes = setup_opc_nodes()
        while running.is_set():
            try:
                dx = nodes['dx'].get_value()
                dy = nodes['dy'].get_value()
                dz = nodes['dz'].get_value()
                with data_lock:
                    current_drone_position['dx'] = dx
                    current_drone_position['dy'] = dy
                    current_drone_position['dz'] = dz
            except Exception as e:
                print(f"[OPC Thread] Erro fatal ao ler dados: {e}")
                running.clear()
            if new_target_event.is_set():
                new_target_event.clear()
                with data_lock:
                    local_target_copy = new_target_received.copy()
                try:
                    tx, ty, tz = local_target_copy['tx'], local_target_copy['ty'], local_target_copy['tz']
                    print(f"[OPC Thread] Escrevendo novo alvo: tx={tx}, ty={ty}, tz={tz}")
                    nodes['tx'].set_value(tx, ua.VariantType.Float)
                    nodes['ty'].set_value(ty, ua.VariantType.Float)
                    nodes['tz'].set_value(tz, ua.VariantType.Float)
                except Exception as e:
                    print(f"[OPC Thread] Erro ao escrever alvo: {e}")
            for _ in range(5):
                if not running.is_set(): break
                time.sleep(0.01)
    except Exception as e:
        print(f"[OPC Thread] Erro fatal na inicialização: {e}")
    finally:
        if opc_client: opc_client.disconnect()
        print("[OPC Thread] Desconectado e parado.")
        running.clear()

# --- Thread 2: Lógica do Servidor TCP (SUB-THREADS) ---
def tcp_sender_task(conn, addr):
    print(f"[TCP Sender] Iniciado para {addr}")
    try:
        while running.is_set():
            with data_lock:
                local_pos_copy = current_drone_position.copy()
            
            # *** MUDANÇA AQUI ***
            # Gera timestamp em ISO 8601 (UTC)
            timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            dx, dy, dz = local_pos_copy['dx'], local_pos_copy['dy'], local_pos_copy['dz']
            
            # *** MUDANÇA AQUI ***
            message = f"{timestamp_str},{dx:.4f},{dy:.4f},{dz:.4f}\n" 
            conn.sendall(message.encode('utf-8'))
            time.sleep(0.1)
    except (BrokenPipeError, ConnectionResetError, OSError):
        print(f"[TCP Sender] Cliente {addr} desconectado (ou socket fechado).")
    finally:
        print(f"[TCP Sender] Task para {addr} parada.")

def tcp_receiver_task(conn, addr):
    print(f"[TCP Receiver] Iniciado para {addr}")
    buffer = ""
    try:
        conn.settimeout(1.0)
        while running.is_set():
            try:
                data = conn.recv(1024)
                if not data:
                    break 
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if not message: continue
                    try:
                        parts = message.split(',')
                        
                        # *** MUDANÇA AQUI ***
                        # O timestamp agora é uma string, não um float
                        ts_recebido_str = parts[0]
                        
                        tx, ty, tz = float(parts[1]), float(parts[2]), float(parts[3])
                        
                        # *** MUDANÇA AQUI ***
                        print(f"[TCP Receiver] (TS: {ts_recebido_str}) Alvo recebido de {addr}: tx={tx}, ty={ty}, tz={tz}")
                        
                        with data_lock:
                            new_target_received['tx'] = tx
                            new_target_received['ty'] = ty
                            new_target_received['tz'] = tz
                        new_target_event.set()
                    except (IndexError, ValueError) as e:
                        print(f"[TCP Receiver] Mensagem mal formatada de {addr}: '{message}'. Erro: {e}")
            except socket.timeout:
                continue 
    except (ConnectionResetError, BrokenPipeError, OSError):
        print(f"[TCP Receiver] Cliente {addr} desconectado.")
    finally:
        print(f"[TCP Receiver] Task para {addr} parada.")
        try: conn.close()
        except: pass

# --- Thread 2: Lógica PRINCIPAL do Servidor TCP ---
def tcp_server_thread():
    print("[TCP Server] Iniciando...")
    server_socket = None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(1.0)
        server_socket.bind((TCP_SERVER_HOST, TCP_SERVER_PORT))
        server_socket.listen()
        print(f"[TCP Server] Ouvindo em {TCP_SERVER_HOST}:{TCP_SERVER_PORT}")
        while running.is_set():
            print("\n[TCP Server] Aguardando um novo cliente...")
            conn = None
            try:
                conn, addr = server_socket.accept()
                print(f"[TCP Server] Cliente {addr} conectado. Servidor ocupado.")
                sender = threading.Thread(target=tcp_sender_task, args=(conn, addr), daemon=True)
                receiver = threading.Thread(target=tcp_receiver_task, args=(conn, addr), daemon=True)
                sender.start()
                receiver.start()
                sender.join()
                receiver.join()
                print(f"[TCP Server] Cliente {addr} desconectado. Servidor disponível.")
            except socket.timeout:
                continue
            except OSError:
                 if not running.is_set(): break 
            except Exception as e:
                if running.is_set(): print(f"[TCP Server] Erro na conexão do cliente: {e}")
                if conn: conn.close()
    except Exception as e:
        print(f"[TCP Server] Erro fatal: {e}")
    finally:
        if server_socket: server_socket.close()
        print("[TCP Server] Parado.")
        running.clear() 

# --- Inicia o CLP ---
if __name__ == "__main__":
    print("--- CLP.py (A Ponte) [VERSÃO 'UM CLIENTE POR VEZ'] ---")
    opc_thread = threading.Thread(target=opc_ua_thread, name="OPC_Thread")
    tcp_thread = threading.Thread(target=tcp_server_thread, name="TCP_Thread")
    opc_thread.start()
    tcp_thread.start()
    try:
        while running.is_set():
            time.sleep(1)
            if not opc_thread.is_alive() or not tcp_thread.is_alive():
                if running.is_set():
                    print("[Main] Detectado que uma thread parou inesperadamente.")
                running.clear()
    except KeyboardInterrupt:
        print("\n[Main] Desligamento solicitado (Ctrl+C).")
        running.clear()
    print("[Main] Aguardando threads finalizarem...")
    if opc_thread.is_alive(): opc_thread.join()
    if tcp_thread.is_alive(): tcp_thread.join()
    print("[Main] Desligamento completo.")