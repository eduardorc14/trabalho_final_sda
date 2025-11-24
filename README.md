# Simulação e Controle de Drone

Este projeto demonstra um sistema de controle de um drone simulado, integrando o CoppeliaSim, servidores e OPC UA e TCP/IP e um sinótico para controle.

## 1. Link do Vídeo apresentando o projeto

https://www.youtube.com/watch?v=NboQ0eCnko8

## 2. Requisitos

Instale as bibliotecas Python necessárias:
```
pip install coppeliasim-zmqremoteapi-client
pip install opcua
pip install matplotlib
```

## 3. Configuração do Ambiente

Além do Python instalado no computador, é necessário mais dois softwares, o Prosys OPC UA Simulation Server e o CoppeliaSim.

Abra o Prosys OPC UA Simulation Server e carregue o arquivo de simulação de server ```drone.uasim```.

Abra o CoppeliaSim e carregue o arquivo de cena ```drone.ttt```.

## 4. Execução do Projeto

Com os simuladores prontos, você pode iniciar os scripts de controle.

### Método Automático

Você pode executar o script run.py, que irá iniciar todos os códigos na ordem correta:
```
python run.py
```

### Método Manual 

Você pode rodar cada código manualmente. É preciso abrir um terminal separado para cada script e executá-los na seguinte ordem:
```python bridge.py```

```python clp.py```

```python client_tcp.py```

```python mes.py```

```python client_mes.py```

## 5. Como Usar a Interface

Após a execução escolhida, a interface gráfica "Sinótico Drone" será aberta.

<img width="1193" height="719" alt="image" src="https://github.com/user-attachments/assets/be9e5d57-7312-43a0-b66e-34b6cbc9b25c" />

Você pode controlar o drone de duas formas:

Clique no Gráfico: Clique diretamente em qualquer ponto nos gráficos "Controle dos eixos XY" ou "Controle do eixo Z (Altura)" para definir a nova posição do alvo.

Entrada Manual: Digite as coordenadas X, Y e Z desejadas nos campos da caixa "Definir Target" e clique no botão "Aplicar".

O drone se moverá automaticamente em direção ao target marcado no gráfico.
