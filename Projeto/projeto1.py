#listas para guardar e acessar mais de um valor
clientes = []
contas = []
saldos = []
#funções para não repetir código
def cadastrarcliente(nome):
    clientes.append(nome) #coloca o cliente na lista clientes
def fazerdeposito(saldo, deposito):
    total_deposito = saldo + deposito #realiza a conta para depositar e agrega ao valor já existente
    return total_deposito
def fazersaque(saldo, saque):
    total_saque = saldo - saque #realiza o saque da conta, subtraindo do valor existente
    return total_saque
while True:
    conta = int(input("Crie uma conta (para finalizar digite -1): ")) #recebe o número da conta
    if conta == -1: #finaliza o código caso a conta seja -1
        print("Fim")
        break
    while conta in contas:
        conta = int(input("Digite outra conta, pois a digitada anteriormente já existe: ")) #se a conta já existe na lista contas, pede para que o usuário digite outro número que ainda não foi registrado
    contas.append(conta)
    nome = input("Digite o nome do cliente: ") #recebe o nome do cliente
    cadastrarcliente(nome) #adiciona o nome do cliente na função para adicioná-lo na lista clientes
    print(f'o cadastro do cliente {nome} foi realizado')
    saldo = 0 #inicia o saldo do cliente como zero
    saldos.append(saldo) #adiciona o saldo na lista saldos
    while True:
        opcao = input("Digite o número correspondente a opção\n0- Para consultar saldo\n1- Para fazer um depósito\n2- Para fazer um saque \n3- Para listar as contas cadastradas\n4- Para procurar uma conta \nDigite -1 para adicionar uma nova conta\n")
        if opcao == "-1": #volta para a adição de contas caso seja digitado a opção -1
            break
        if opcao == "0": #consulta o saldo
            print(saldo)
        if opcao == "1": #realiza o depósito
            valor_deposito = float(input("Digite o valor do depósito: "))
            novo_valor = fazerdeposito(saldo, valor_deposito)
            saldo = novo_valor
            print(f"Você depositou: {valor_deposito} e seu novo saldo é: {saldo}")
            saldos[-1] = saldo #procura o ultimo valor da lista (mais recente) e atualiza o saldo
        if opcao == "2" and saldo > 0: #opção que realiza o saque
            valor_saque = float(input("Digite o valor do saque: "))
            if valor_saque > saldo:
                print("Seu saldo é menor do que o valor de saque") #volta para o menu sem realizar alterações caso o valor do saque seja maior que o valor da conta
            else: #se o saldo for maior que o valor de saque, realiza o saque
                novo_valor = fazersaque(saldo, valor_saque)
                saldo = novo_valor
                saldos[-1] = saldo #procura o ultimo valor da lista e atualiza o valor do saldo
                print(f"Você sacou {valor_saque} e seu novo saldo é: {saldo}")
        if opcao == "2" and saldo == 0: #se o saldo for zero, volta para o menu, já que não é possível realizar saque
            print("Você está sem saldo e por isso não pode sacar!")
        if opcao == "3" and len(contas) > 0: #Se lista de contas tiver alguma conta cadastrada, retorna todas as contas já cadastradas 
            print(f" Essas são as contas cadastradas: \n{contas}")
        if opcao == "4" and len(contas) > 0: #se a lista de contas tiver alguma conta cadastrada, permite que seja realizada a busca de dados da conta
            proc_cont = int(input("Digite a conta que você quer procurar: "))
            posicao = contas.index(proc_cont) #já que a conta não pode ser repetida, retorna o índice da conta que está sendo procurada
            procurar_conta = list(zip(contas, clientes, saldos)) #junta os valores:conta, nome, saldo; em tuplas para pesquisa de dados
            print()
            print(f"conta | cliente |  saldo  \n{procurar_conta[posicao]}") #retorna a conta, nome e saldo pesquisados
