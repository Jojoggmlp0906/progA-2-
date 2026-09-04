saldo = 0

def cadastrarcliente(nome):
    cliente = nome
    return cliente
def consultar_saldo(saldo):
    print(saldo)
def fazerdeposito(saldo, deposito):
    total_deposito = saldo + deposito
    return total_deposito
def fazersaque(saldo, saque):
    total_saque = saldo - saque
    return total_saque

nome = input("Digite o nome do cliente: ")
print(f'o cadastro do cliente {cadastrarcliente(nome)} foi realizado')
conta = input("Crie uma conta ")
opcao = input("Digite o número correspondente a opção\n 0 - Para consultar saldo\n 1 - Para fazer um depósito\n 2 - Para fazer um saque\n 3 - Para fechar o programa\n\n ")
print()

while opcao != 3:
  if opcao == "0":
    print(consultar_saldo(saldo))
  if opcao == "1":
    valor_deposito = float(input("Digite o valor do depósito: "))
    novo_valor = fazerdeposito(saldo, valor_deposito)
    saldo = novo_valor
  if opcao == "2":
    valor_saque = float(input("Digite o valor do saque: "))
    novo_valor = fazersaque(saldo, valor_saque)
    saldo = novo_valor
  if opcao == "3":
    print("Obrigado por usar nosso sistema!")
    break
  opcao = input("Digite o número correspondente a opção\n 0 - Para consultar saldo\n 1 - Para fazer um depósito\n 2 - Para fazer um saque\n 3 - Para fechar o programa\n\n ")
  
  print()