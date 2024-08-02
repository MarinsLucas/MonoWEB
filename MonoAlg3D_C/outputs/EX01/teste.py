import matplotlib.pyplot as plt

# Função para ler o arquivo e extrair os dados
def ler_dados_arquivo(nome_arquivo):
    tempos = []
    vms = []
    
    with open(nome_arquivo, 'r') as arquivo:
        for linha in arquivo:
            # Divide a linha em tempo e vm
            partes = linha.split()
            if len(partes) == 2:
                tempo, vm = partes
                tempos.append(float(tempo))
                vms.append(float(vm))
    
    return tempos, vms

# Nome do arquivo
nome_arquivo = './Vm_matrix.txt'

# Ler os dados
tempos, vms = ler_dados_arquivo(nome_arquivo)

# Plotar os dados
plt.figure(figsize=(10, 6))
plt.plot(tempos, vms, linestyle='-', color='b')
plt.grid(True)
plt.show()