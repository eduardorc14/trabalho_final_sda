# Simulação e Controle de Drone

## Bibliotecas demandadas
pip install coppeliasim-zmqremoteapi-client
pip install opcua
pip install matplotlib

Para rodar o código, você deve rodar os seguintes códigos na seguinte ordem:

você deve abrir o Prosys OPC UA Simulation Server e abrir o arquivo "drone.uasim". Depois abra o Coppelia Sim e abra o arquivo "drone.ttt", depois basta seguir a ordem de compilaçãop dos códigos a seguir

1 - bridge.py
2 - clp.py
3 - client_tcp.py
4 - mes.py
5 - client_mes.py

Ou pode apenas rodar o script "run.py" que rodará todos na ordem já correta.

Simulação e Controle de Drone

Este projeto demonstra um sistema de controle de um drone simulado, integrando o CoppeliaSim, um servidor OPC UA e uma interface gráfica de controle em Python.

1. Requisitos

Antes de começar, instale as bibliotecas Python necessárias:

pip install coppeliasim-zmqremoteapi-client
pip install opcua
pip install matplotlib


2. Configuração do Ambiente

Você precisará de dois softwares de simulação. Siga estes passos:

Abra o Prosys OPC UA Simulation Server e carregue o arquivo de simulação drone.uasim.

Abra o CoppeliaSim e carregue a cena drone.ttt.

3. Execução do Projeto

Com os simuladores prontos, você pode iniciar os scripts de controle.

Método Recomendado (Automático)

Você pode executar o script run.py, que irá iniciar todos os componentes na ordem correta:

python run.py


Método Manual (Para Debug)

Se preferir, você pode rodar cada componente manualmente. É crucial abrir um terminal separado para cada script e executá-los na seguinte ordem:

python bridge.py

python clp.py

python client_tcp.py (Este é o script da interface gráfica)

python mes.py

python client_mes.py

4. Como Usar a Interface

Após a execução (manual ou automática), a interface gráfica "Sinótico Drone" será aberta.

Você pode controlar o drone de duas formas:

Clique no Gráfico: Clique diretamente em qualquer ponto nos gráficos "Controle dos eixos XY" ou "Controle do eixo Z (Altura)" para definir a nova posição do alvo.

Entrada Manual: Digite as coordenadas X, Y e Z desejadas nos campos da caixa "Definir Target" e clique no botão "Aplicar".

O drone (marcador X azul) se moverá automaticamente em direção ao alvo (marcador . vermelho) no gráfico.
