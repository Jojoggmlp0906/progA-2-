def cadastrarcliente(nome):
    cliente = nome
    return cliente
def consultar_saldo(saldo):
    return saldo
def fazerdeposito(saldo, deposito):
    total_deposito = saldo + deposito
    return total_deposito
def fazersaque(saldo, saque):
    total_saque = saldo - saque
    return total_saque
clientes = []
contas = []
saldos = []
while True:
    nome = input("Digite o nome do cliente")
    clientes.append(nome)
    print(f'o cadastro do cliente {cadastrarcliente(nome)} foi realizado')
    conta = int(input("Crie uma conta"))
    contas.append(conta)
    saldo = 0.0
    saldos.append(saldo)
    opcao = input("Digite o número correspondente a opção\n 0 - Para consultar saldo\n 1 - Para fazer um depósito\n 2- Para fazer um saque\n 3- Para procurar uma conta pelo número \n4- Para listar contas ")
    if opcao == "0":
        print(consultar_saldo(saldo))
    if opcao == "1":
        valor_deposito = float(input("Digite o valor do depósito: "))
        novo_valor = fazerdeposito(saldo, valor_deposito)
        saldo = novo_valor
        break
    if opcao == "2":
        valor_saque = float(input("Digite o valor do saque"))
        novo_valor = fazersaque(saldo, valor_saque)
        saldo = novo_valor
        break
    if opcao == "3":
        procurar = int(input("Digite a conta que você quer procurar: "))
        juncao = list(zip(contas, clientes, saldos))
        for tupla in juncao:
            if procurar in tupla:
                print(f"conta: {tupla}")
        break
    if opcao == "4":
        print(contas)