import subprocess
import sys
import time

# Ordem de inicialização
list_scripts = [
    "bridge.py",
    "clp.py",
    "client_tcp.py",
    "mes.py",
    "client_mes.py"
]

processos = []

try:
    for script in list_scripts:
        print(f"Iniciando script {script}...")
        
        processo = subprocess.Popen([sys.executable, script])
        processos.append(processo)

        time.sleep(1)   # delay entre scripts

    print("\nScripts iniciados.")

    # Para Ctrl+C funcionar
    while True:
        time.sleep(5)

# Ctrl+C
except KeyboardInterrupt:
    print("Encerrando scripts...")
    
    for p in processos:
        p.terminate()
        print(f"Script {p.args[1]} encerrando...")
            
    print("\Scripts encerrados.")