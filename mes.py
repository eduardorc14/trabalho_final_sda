# /* Por fim, crie um segundo cliente OPCUA em outro programa, encapsulado dentro de outro
# servidor OPCUA, numa arquitetura que chamamos de chained server. O servidor fornecer´a as
# mesmas informa¸c˜oes do drone para outro cliente, chamado MES, que ir´a ler dados do processo
# para salvar em um arquivo chamado “mes.txt”. */

##########################################
thread 1:
    serverOPC2 = server(opc)

    recebe do clientOPC2            #client_mes.py
    envia para o clientOPC2         #client_mes.py

##########################################
thread 1:
    clientOPC1_2 = client(opc)

    recebe do serverOPC1        #clp.py