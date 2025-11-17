import threading
import time
import datetime  
from opcua import Client, ua, Server


# --- Configurações ---
OPC_UA_SERVER_CHAINED_URL = "opc.tcp://localhost:4841/freeopcua/server/"

# --- Buffers de Dados Compartilhados ---
log_lock = threading.Lock()
new_target_event = threading.Event()
current_drone_position = {'dx': 0.0, 'dy': 0.0, 'dz': 0.0}
new_target_received = {'tx': 0.0, 'ty': 0.0, 'tz': 0.0}
shared_data = {'dx':0.0, 'dy':0.0, 'dz':0.0, 'tx':0.0, 'ty':0.0, 'tz':0.0}
running = threading.Event()
running.set()

# --- Lógica de Conexão OPC-UA (Baseada no seu script) ---
def setup_opc_nodes(url=OPC_UA_SERVER_CHAINED_URL):
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
                tx = nodes['tx'].get_value()
                ty = nodes['ty'].get_value()
                tz = nodes['tz'].get_value()
                with log_lock:
                    shared_data['dx'] = dx
                    shared_data['dy'] = dy
                    shared_data['dz'] = dz
                    shared_data['tx'] = tx
                    shared_data['ty'] = ty
                    shared_data['tz'] = tz
            except Exception as e:
                print(f"[OPC Thread] Erro fatal ao ler dados: {e}")
                running.clear()
            time.sleep(0.1)
    except Exception as e:
        print(f"[OPC Thread] Erro fatal na inicialização: {e}")
    finally:
        if opc_client: opc_client.disconnect()
        print("[OPC Thread] Desconectado e parado.")
        running.clear()

# --- Thread 2: Lógica de Log MES ---
def log_mes_thread(log_file):
    print("[Log MES Thread] Iniciando...")
    while running.is_set():
        try:
            with log_lock:
                dx = shared_data['dx']
                dy = shared_data['dy']
                dz = shared_data['dz']
                tx = shared_data['tx']
                ty = shared_data['ty']
                tz = shared_data['tz']
            
            # Corrigir None -> 0.0
            dx = dx or 0.0
            dy = dy or 0.0
            dz = dz or 0.0
            tx = tx or 0.0
            ty = ty or 0.0
            tz = tz or 0.0

            ts_drone_str = datetime.datetime.utcnow().isoformat() + 'Z'
            log_line = f"{ts_drone_str},{dx:.4f},{dy:.4f},{dz:.4f},{tx:.2f},{ty:.2f},{tz:.2f}\n"
            log_file.write(log_line)
            log_file.flush()

        except Exception as e:
            print(f"[Log MES Thread] Erro ao logar dados: {e}")
        time.sleep(0.1)

    print("[Log MES Thread] Parado.")
    running.clear()

# --- MES ---
if __name__ == "__main__":
    print("--- Iniciando Cliente MES ---")
    log_filename ="mes.txt"

    try:
        with open(log_filename, "w") as log_file:
            print(f"Salvando log em -> {log_filename}")
            
            log_file.write("timestamp_iso,drone_x,drone_y,drone_z,target_x,target_y,target_z\n")
            
            opc_thread = threading.Thread(target=opc_ua_thread, daemon=True)
            log_thread = threading.Thread(target=log_mes_thread, args=(log_file,), daemon=True)
            
            opc_thread.start()
            log_thread.start()
            
            while running.is_set():
                if not opc_thread.is_alive() and not log_thread.is_alive():
                    running.clear()
                time.sleep(0.5)
        
        print(f"Arquivo '{log_filename}' salvo com sucesso.")

    except KeyboardInterrupt:
        print("\n[Main] Desligamento solicitado (Ctrl+C).")
        running.clear()
    except Exception as e:
        if running.is_set():
            print(f"Erro inesperado: {e}")
    finally:
        if 'opc_thread' in locals():
            opc_thread.join(timeout=1.0)
        if 'log_thread' in locals():
            log_thread.join(timeout=1.0)
        
        print("[Main] Desligamento completo.")