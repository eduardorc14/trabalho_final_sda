# /*Crie um programa chamado CLP que contenha um cliente OPC UA (para ler e atuar no drone
# via servidor) e um servidor TCP/IP (responsável por receber conex˜oes de clientes TCP/IP
# que desejem controlar o processo). Sugest˜ao: crie duas threads, uma para cada finalidade. O
# cliente OPC ir´a ler a posi¸c˜ao do drone (DroneX,Y,Z ) e enviar comandos de referˆencia de posi¸c˜ao
# (T argetX,Y,Z ), conforme ilustrado na figura 4*/

var globais:
    DroneX.read
    DroneY.read
    DroneZ.read

    TargetX.write
    TargetY.write
    TargetZ.write

#lembrar de usar semaforo ou lock na hora de ler e escrever

#############################################

thread 1:
    clientOPC1_1 = client(opc)

    envia para o serverOPC1     #bridge.py
    recebe do serverOPC1        #bridge.py

#############################################

thread 2:
    serverTCP1 = server(tcp)

    manda para o clientTCP1     #client_tcp.py
    recebe do clientTCP1        #cliebt_tcp.py

#############################################