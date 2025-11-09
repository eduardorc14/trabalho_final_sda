# Nome do arquivo: client_tcp.py
# (Corrigido: Timestamps em ISO 8601)

import socket
import threading
import time
import datetime # <-- ADICIONADO
import sys

# --- Configurações ---
CLP_HOST = '127.0.0.1'
CLP_PORT = 65432

# --- Variáveis Globais para Log ---
running = threading.Event()
running.set()
log_lock = threading.Lock()
last_sent_target = {'tx': 0.0, 'ty': 0.0, 'tz': 0.0}

# --- Thread de Recebimento (e Log) ---
def receiver_thread(s, log_file):
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
                    
                    # *** MUDANÇA AQUI ***
                    # O timestamp agora é uma string
                    ts_drone_str = parts[0]
                    
                    dx, dy, dz = float(parts[1]), float(parts[2]), float(parts[3])
                    with log_lock:
                        target_copy = last_sent_target.copy()
                    tx, ty, tz = target_copy['tx'], target_copy['ty'], target_copy['tz']
                    
                    # *** MUDANÇA AQUI ***
                    # Salva a string direto no log
                    log_line = f"{ts_drone_str},{dx:.4f},{dy:.4f},{dz:.4f},{tx:.2f},{ty:.2f},{tz:.2f}\n"
                    log_file.write(log_line)
                    
                except (ValueError, IndexError):
                    pass
        except socket.timeout:
            continue 
        except (ConnectionResetError, OSError) as e:
            if running.is_set():
                print(f"\n[Receiver] Conexão perdida: {e}")
            break
            
    print("[Receiver] Parado.")
    running.clear() # AVISA AS OUTRAS THREADS PARA PARAREM

# --- Thread de Envio (Lógica Principal) ---
def sender_thread(s):
    print("\n--- 🎮 Painel de Controle TCP ---")
    print("Digite as coordenadas (tx, ty, tz) separadas por vírgula.")
    print("Exemplo: 10,20,5")
    print("Digite 'sair' para fechar.")
    print("---------------------------------")
    try:
        while running.is_set():
            user_input = input("Novo Alvo (tx,ty,tz): ")
            cmd = user_input.strip().lower()
            if cmd in ['sair', 'exit', 'quit', 'q']:
                break
            if not running.is_set():
                break
            try:
                parts = user_input.split(',')
                tx, ty, tz = float(parts[0]), float(parts[1]), float(parts[2])
                with log_lock:
                    last_sent_target['tx'] = tx
                    last_sent_target['ty'] = ty
                    last_sent_target['tz'] = tz
                
                # *** MUDANÇA AQUI ***
                # Gera timestamp em ISO 8601 (UTC)
                timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
                # *** MUDANÇA AQUI ***
                message = f"{timestamp_str},{tx},{ty},{tz}\n" 
                s.sendall(message.encode('utf-8'))
                print(f"✅ Alvo {tx,ty,tz} enviado.")
                
            except (ValueError, IndexError):
                print("❌ Formato inválido. Use vírgulas: ex: 10,20,5")
            except (BrokenPipeError, ConnectionResetError):
                print("❌ [Sender] Conexão perdida com o CLP.")
                break
    except EOFError: pass
    except KeyboardInterrupt: print("\n[Sender] Interrompido.")
    finally:
        print("[Sender] Parado.")
        running.clear() # AVISA AS OUTRAS THREADS PARA PARAREM

# --- Inicia o Cliente ---
if __name__ == "__main__":
    print("--- client_tcp.py (Painel de Controle + Historiador) ---")
    log_filename = "historiador.txt"
    s = None 
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Conectando ao CLP em {CLP_HOST}:{CLP_PORT}...")
        s.connect((CLP_HOST, CLP_PORT))
        s.settimeout(1.0)
        print("Conectado!")
        
        with open(log_filename, "w") as log_file:
            print(f"Salvando log em -> {log_filename}")
            
            # *** MUDANÇA AQUI ***
            # O cabeçalho do log agora tem um timestamp string
            log_file.write("timestamp_iso,drone_x,drone_y,drone_z,target_x,target_y,target_z\n")
            
            recv_thread = threading.Thread(target=receiver_thread, args=(s, log_file), daemon=True)
            send_thread = threading.Thread(target=sender_thread, args=(s,), daemon=True)
            
            recv_thread.start()
            send_thread.start()
            
            while running.is_set():
                if not recv_thread.is_alive() and not send_thread.is_alive():
                    running.clear()
                time.sleep(0.5)
        
        print(f"Arquivo '{log_filename}' salvo com sucesso.")

    except ConnectionRefusedError:
        print(f"\n❌ ERRO: Não foi possível conectar.")
        print(f"   Verifique se o 'CLP.py' está rodando na porta {CLP_PORT}.")
        print("[Main] Cliente desligado. Nenhum log foi salvo.")
    except KeyboardInterrupt:
        print("\n[Main] Desligamento solicitado (Ctrl+C).")
    except Exception as e:
        if running.is_set():
            print(f"Erro inesperado: {e}")
    finally:
        running.clear()
        if s: s.close()
        if 'recv_thread' in locals() and recv_thread.is_alive():
            recv_thread.join(timeout=1.0)
        if 'send_thread' in locals() and send_thread.is_alive():
            send_thread.join(timeout=1.0)
        
        print("[Main] Desligamento completo.")