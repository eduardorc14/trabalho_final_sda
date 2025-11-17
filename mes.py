# /* Por fim, crie um segundo cliente OPCUA em outro programa, encapsulado dentro de outro
# servidor OPCUA, numa arquitetura que chamamos de chained server. O servidor fornecer´a as
# mesmas informa¸c˜oes do drone para outro cliente, chamado MES, que ir´a ler dados do processo
# para salvar em um arquivo chamado “mes.txt”. */

##########################################

import threading
import time
import datetime  
from opcua import Client, ua, Server


# --- Configurações ---
OPC_UA_SERVER_URL = "opc.tcp://localhost:53530/OPCUA/SimulationServer"

# --- Buffers de Dados Compartilhados ---
data_lock = threading.Lock()
new_target_event = threading.Event()
current_drone_position = {'dx': 0.0, 'dy': 0.0, 'dz': 0.0}
new_target_received = {'tx': 0.0, 'ty': 0.0, 'tz': 0.0}
shared_data = {'dx':0.0, 'dy':0.0, 'dz':0.0, 'tx':0.0, 'ty':0.0, 'tz':0.0}
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
                tx = nodes['tx'].get_value()
                ty = nodes['ty'].get_value()
                tz = nodes['tz'].get_value()
                with data_lock:
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
        running.clear()# --- Thread 1: Lógica OPC-UA --

# --- Thread 2: Lógica OPC-UA-Server ---
def server_opc_ua_thread():
    print("[OPC-UA Server Thread] Iniciando...")
    server = Server()
    server.set_endpoint("opc.tcp://localhost:4841/freeopcua/server/")
    server.set_server_name("Drone_Chained_OPCUA_Server")

    idx = server.register_namespace("DroneData")

    # Criando objetos
    drone_obj = server.nodes.objects.add_object(idx, "Drone")

    # Criando nós de variáveis
    node_dx = drone_obj.add_variable(idx, "DroneX", 0.0)
    node_dy = drone_obj.add_variable(idx, "DroneY", 0.0)
    node_dz = drone_obj.add_variable(idx, "DroneZ", 0.0)

    node_tx = drone_obj.add_variable(idx, "TargetX", 0.0)
    node_ty = drone_obj.add_variable(idx, "TargetY", 0.0)
    node_tz = drone_obj.add_variable(idx, "TargetZ", 0.0)

    server.start()
    print("[CHAINED SERVER] Servidor OPC UA iniciado!")

    try:
        while running.is_set():
            with data_lock:
                # Atualiza os valores das variáveis no servidor OPC-UA
                node_dx.set_value(shared_data['dx'])
                node_dy.set_value(shared_data['dy'])
                node_dz.set_value(shared_data['dz'])
                node_tx.set_value(shared_data['tx'])
                node_ty.set_value(shared_data['ty'])
                node_tz.set_value(shared_data['tz'])
            
                for key, valor in shared_data.items():
                    print(f"[CHAINED SERVER] {key} = {valor}")

            time.sleep(0.1)
    except Exception as e:
        print(f"[CHAINED SERVER] Erro fatal: {e}")
    finally:
        server.stop()
        print("[CHAINED SERVER] Servidor OPC UA parado.")
        running.clear()

# --- Inicia Server ---
if __name__ == "__main__":
    print("--- Mes.py Chained Server ---")
    opc_thread = threading.Thread(target=opc_ua_thread, name="OPC_Thread")
    server_opc_thread = threading.Thread(target=server_opc_ua_thread, name="SERVE_OPC_Thread")
    opc_thread.start()
    server_opc_thread.start()
    try:
        while running.is_set():
            time.sleep(1)
            if not opc_thread.is_alive() or not server_opc_thread.is_alive():
                if running.is_set():
                    print("[Main] Detectado que uma thread parou inesperadamente.")
                running.clear()
    except KeyboardInterrupt:
        print("\n[Main] Desligamento solicitado (Ctrl+C).")
        running.clear()
    print("[Main] Aguardando threads finalizarem...")
    if opc_thread.is_alive(): opc_thread.join()
    if server_opc_thread.is_alive(): server_opc_thread.join()
    print("[Main] Desligamento completo.")