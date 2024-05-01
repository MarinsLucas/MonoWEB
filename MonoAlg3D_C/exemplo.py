import time

tempo_inicial = time.time()  # Captura o tempo inicial

while True:
    # Coloque aqui o código que deseja executar repetidamente

    tempo_atual = time.time()  # Captura o tempo atual
    tempo_passado = tempo_atual - tempo_inicial  # Calcula quanto tempo passou desde o início

    if tempo_passado >= 5:  # Verifica se passaram 10 segundos
        break  # Sai do loop

print("Tempo de execução de 10 segundos concluído.")