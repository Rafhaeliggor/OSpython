![Comandos](comandos.png)
Esta imagem mostra todos os comandos que o simulador reconhece dentro do terminal do sistema operacional simulado.
Entre eles estão: create, list, run, block, unblock, kill e exit.
Cada comando representa uma ação típica de um sistema operacional, como criar processos, listar o estado atual ou executar o escalonador.


![importacao](importacao.png)
Aqui vemos os módulos importados e a estrutura inicial do código.
São utilizadas bibliotecas padrão do Python, como random, collections e dataclasses, responsáveis por gerar valores aleatórios, gerenciar filas e armazenar informações dos processos de forma organizada.


![lista](lista.png)
Este trecho mostra o laço principal (while True) que mantém o simulador em execução.
Dentro dele, o programa verifica qual comando o usuário digitou e executa a ação correspondente por meio de várias condições if/elif.
É o coração do simulador — ele interpreta e responde aos comandos como se fosse um terminal real de um sistema operacional.


![uso1](uso1.png)
Nesta etapa, foi criado três processos: spotify, chrome e vscode.
Cada processo recebe atributos gerados aleatoriamente, como tempo de CPU, uso de memória e prioridade.
Esses processos são adicionados à fila de prontos e podem ser visualizados com o comando list.


![uso2](uso2.png)
Aqui é mostrado o momento em que o comando run prio é utilizado.
Ele ativa o algoritmo de escalonamento por prioridade, onde os processos com menor valor de prioridade (mais alta prioridade) são executados primeiro.
O simulador então passa a mostrar, ciclo a ciclo, qual processo está sendo executado e o consumo da CPU.