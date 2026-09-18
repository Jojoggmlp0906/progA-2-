clientes = []
contas = []
saldos = []
def cadastrarcliente(nome):
    clientes.append(nome)
def consultar_saldo(saldo):
    print(saldo)
def fazerdeposito(saldo, deposito):
    total_deposito = saldo + deposito
    return total_deposito
def fazersaque(saldo, saque):
    total_saque = saldo - saque
    return total_saque
while True:
    conta = int(input("Crie uma conta (para finalizar digite -1): "))
    if conta == -1:
        print("Fim")
        break
    nome = input("Digite o nome do cliente: ")
    print(f'o cadastro do cliente {nome} foi realizado')
    while conta in contas:
        conta = int(input("Digite outra conta, pois a digitada anteriormente já existe: "))
    contas.append(conta)
    saldo = 0
    saldos.append(saldo)
    posicao = saldos.index(saldo)
    cadastrarcliente(nome)
    while True:
        opcao = input("Digite o número correspondente a opção\n0- Para consultar saldo\n1- Para fazer um depósito\n2- Para fazer um saque \n3- Para listar as contas cadastradas\n4- Para procurar uma conta \nDigite -1 para finalizar\n")
        if opcao == "-1":
            break
        if opcao == "0":
            print(consultar_saldo(saldo))
        if opcao == "1":
            valor_deposito = float(input("Digite o valor do depósito: "))
            novo_valor = fazerdeposito(saldo, valor_deposito)
            saldo = novo_valor
            saldos[-1] = saldo
        if opcao == "2" and saldo > 0:
            valor_saque = float(input("Digite o valor do saque: "))
            if valor_saque > saldo:
                print("Seu saldo é menor do que o valor de saque")
            else:
                novo_valor = fazersaque(saldo, valor_saque)
                saldo = novo_valor
                saldos[-1] = saldo
                print(f"Você sacou {valor_saque} e seu novo saldo é: {saldo}")
        if opcao == "2" and saldo == 0:
            print("Você está sem saldo e por isso não pode sacar!")
        if opcao == "3" and len(contas) > 0:
            print(f" Essas são as contas cadastradas: \n{contas}")
        if opcao == "4" and len(contas) > 0:
            proc_cont = int(input("Digite a conta que você quer procurar: "))
            posicao = contas.index(proc_cont)
            procurar_conta = list(zip(contas, clientes, saldos))
            print()
            print(f"conta | cliente |  saldo  \n{procurar_conta[posicao]}")
