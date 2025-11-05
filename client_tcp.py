# /* Crie um programa que opere como cliente TCP/IP para ler e enviar dados remotamente ao
# processo (para fins pr´aticos, esse cliente pode rodar na mesmo m´aquina do servidor). Dados
# de controle e supervis˜ao devem ser exibidos ao operador via um sin´otipo gr´afico ou exibidas
# na pr´opria tela do terminal (a parte gr´afica ´e meramente opcional, mas vale pontos-extra).
# Todas essas informa¸c˜oes devem ser registradas em um arquivo denominado “historiador.txt”. O
# operador dever´a, via supervis´orio, escolher pontos de referˆencia para inspe¸c˜ao visual do drone,
# recebendo de volta os valores de posi¸c˜ao da robˆo e o timestamp associado. */

clientTCP1 = client(tcp)

manda para o serverTCP1     #clp.py
recebe do serverTCP1        #clp.py

## cria um sinotipo que terá o controle e o retorno.
- Uma tela com os valores de X, Y, Z atualizados. Pode ser um gráfico de coordenadas X, Y, e outro gráfico apenas para o Z, que varia verticalmente (com timestamp).
- Terá um campo que digita os novos valores de X, Y, Z. (Se não quiser no campo, pode colocar um grafico igual acima)
- Tela com a câmera do drone se possível.

criar um arquivo "historiador.txt" com todas essas posições recebidas.
