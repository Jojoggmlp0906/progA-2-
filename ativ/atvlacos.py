"""
1ª Questão

def triplicar(a):
    triplo = a*3
    return triplo
num = int(input("Digite um número: "))
while num != -999:
    print(triplicar(num))
    num = int(input("Digite um número: "))

#2ª Questão
num = int(input("Digite um número: "))
soma = 0
while num > 0:
    soma += 1
    print(soma)
    num = int(input("Digite um número: "))

    #3ª Questão
num = int(input("Digite um número: "))
soma = 0
total = 0
def calcularmedia(a,b):
    media = a/b
    return media
while num > 0 :
    soma += 1
    total += num
    num = int(input("Digite um número: "))
    if num <= 0:
        print(calcularmedia(total, soma))
        break
  
#4ª questão
num = int(input("Digite um número: "))
n_100_200 = 0
while num != 0:
    if num > 100 and num < 200:
        n_100_200 +=1
    num = int(input("Digite um número: "))
    if num == 0:
        print(n_100_200)
        break

#5ª Questão
nome = str(input("Digite um Nome: "))
while nome != "FIM":
    print(nome)
    nome = str(input("Digite um Nome: "))

#6ª Questão
profissao = str(input("Digite uma profissão:\n"))
def colocar_minusculo(a):
    minusculo = a.lower()
    return minusculo
contagem = 0
while profissao != "FIM":
    novaprofissao = colocar_minusculo(profissao)
    if novaprofissao == "dentista":
        contagem +=1
    profissao = str(input("Digite uma profissão:\n"))
    if profissao == "FIM":
        print(f"{contagem} são dentistas")
Explicar o pequeno uso de IA e procurar entender com o professor também!!!

#7ª Questão
num = int(input("Digite um número: "))
def quadrado(a):
    quadrado_num = a**2
    return quadrado_num
while True:
    if quadrado(num) % 6 != 0:
        print(quadrado(num))
    else:
        print(quadrado(num))
        break
    num = int(input("Digite um número: "))
True == loop infinito

#8ª Questão
num = int(input("Digite um Número: "))
while True:
    if num == -999:
        break
    for n in range(1, num+1):
        if num % n == 0:
            print(f"é divisível por: {n}")
    num = int(input("Digite um Número: "))

#9ª Questão
paisA = 5000000
paisB = 7000000
taxaA = 0.3
taxaB = 0.2
def calcular_nat(pais, taxa_n):
    natalidade = pais * (1+taxa_n)
    return natalidade
ano = 0
while paisA < paisB:
        ano += 1
        paisA = calcular_nat(paisA, taxaA)
        paisB = calcular_nat(paisB, taxaB)
print(f"Serão necessários {ano} anos, para ultrapassar.")
Lembrar: o while guarda as informações mesmo depois de acabar!!!

#10ª Questão
def det_total(quant, tipo):
    if tipo == "residencial":
        kw_total = quant * 0.82
    if tipo == "comercial":
        kw_total = quant * 1.2
    if tipo == "industrial":
        kw_total = quant * 1.6
    return kw_total
def calcular_media(kwh, contador):
    media = kwh/contador
    return media
def icms(total):
    valor_icms = total*1.17
    return valor_icms
contador_res = 0
contador_com = 0
contador_ind = 0
total_res = 0
total_com = 0
total_ind = 0
while True:
    cod = input("Digite o código do consumidor: ")
    if cod == "0":
        break
    quant_kwh = float(input("Digite o consumo do consumidor em kwh: "))
    tipo_con = str(input("Digite o tipo de consumidor: ")).lower()
    print(f"O consumidor {cod} utilizou {quant_kwh} e o valor da sua conta foi {icms(det_total(quant_kwh, tipo_con))}")
    if tipo_con == "residencial":
        contador_res +=1
        total_res += quant_kwh
    if tipo_con == "comercial":
        contador_com +=1
        total_com += quant_kwh
    if tipo_con == "industrial":
        contador_ind +=1
        total_ind += quant_kwh

print(f"O total consumido por cada consumidor foi:\n residencial: {total_res}\n comercial: {total_com}\n industrial: {total_ind}")
if contador_res > 0:
    print(f"A média de consumo residencial foi: {calcular_media(total_res, contador_res)}")
if contador_com > 0:
    print(f"A média de consumo comercial foi: {calcular_media(total_com, contador_com)}")

#Questão 11
for num in range(10):
    num = float(input("Digite um número positivo: "))
    while num < 0:
        num = float(input("Digite um número novamente, pois o anterior é negativo: "))
    print(f"A raiz quadrada é: {num**0.5:.2f}")

#Questão 12
contador_me21 = 0
contador_ma50 = 0
while True:
    idade=int(input("Digite a idade: "))
    if idade < 0:
        break   
    if idade < 21:
        contador_me21 += 1
    if idade > 50:
        contador_ma50 +=1
print(f"O total de pessoas menores de 21 anos é: {contador_me21}")
print(f"O total de pessoas maiores de 50 anos é: {contador_ma50}")

#Questão14
while True:
    num = float(input("Verifique se o número é um quadrado perfeito: "))
    raiz = num**0.5
    while num < 0 :
        num = float(input("Digite novamente pois o número anterior é menor que zero: "))
        raiz = num**0.5
    if raiz == int(raiz):
        print(f"{num} É um quadrado perfeito")
        break
    else:
        print(f"{num} Não é um quadrado perfeito")
        break

#Questão 15
while True:
    num = int(input("Verifique se um número é primo: "))
    resultado = True
    for i in range(2, num):
        if num % i == 0:
            resultado = False
            break
    if resultado == True:
        print(f"{num} é um número primo")
        break
    if resultado == False:
        print(f"{num} não é um número primo")
        break
            

#Questão 16
maior = 0
while True:
    num = float(input("Digite um número:\n (Digite -9999 para finalizar)\n"))
    if num == -9999:
        break
    if num > maior:
        maior = num
if maior > 0:
    print(f"{maior} é o maior número digitado")

#Questão 17
total_contas = 0
contas_negativas = 0
contas_positivas = 0
while True:
    n_conta = int(input("Digite o número da conta: "))
    if n_conta < 0:
        break
    saldo = float(input("Digite o saldo da conta: "))
    total_contas +=1
    if saldo >= 0:
        contas_positivas += 1
        print(f"A conta {n_conta} tem saldo {saldo}")
        print("Positivo")
    if saldo < 0:
        contas_negativas += 1
        print(f"A conta {n_conta} tem saldo {saldo}")
        print("Negativo")
    
if total_contas > 0:
    percentual_neg = (contas_negativas / total_contas)*100
    print(f"O percentual de contas negativas é: {percentual_neg:.2f}%")

#Questão 18
num = []
multiplos = []
while True:
    valor = int(input("Digite um valor: "))
    if valor == 0:
        break
    if valor != 0:
        num.append(valor)
for posicao, i in enumerate(num, start =1):
    if i % posicao == 0:
        multiplos.append(i)
print(multiplos)

#Questão 19
while True:
    num, num1 = int(input("Digite um número:")), int(input("Digite um número para  subtrair do anterior: "))
    if num1 == 0:
        break
    while num >= num1:
        num = num - num1
    print(num)
    break

#Questão 20
while True:
    contador_mmc = 1
    num, num1 = int(input("Digite o primeiro número: ")), int(input("Digite o segundo número: "))

    i = 2
    while  num > 1 or num1 > 1:
        if num % i == 0 or num1 % i == 0:
            contador_mmc*= i
        if num % i == 0:
            num = num / i
        if num1 % i == 0:
            num1 = num1 / i
        if num % i != 0 and num1 % i != 0:
            i += 1
        if num == 1 and num1 == 1:
            break
    print(contador_mmc)

#Questão 21
while True:
    num, num1 = int(input("Digite o primeiro número: ")), int(input("Digite o segundo número: "))
    num = abs(num)
    num1 = abs(num1)
    n_original = num
    n1_original = num1
    i = 2
    contador_mdc = 1
    while num > 1 and num1 > 1:
        if num % i == 0 and num1 % i == 0:
            contador_mdc *= i
            num = num//i
            num1 = num1//i
        if num % i != 0 or num1 % i != 0:
            i+=1
        if num == 1 and num1 == 1:
            break
        if i > min(num, num1):
            break
    print(f"O mdc de {n_original} e {n1_original} é: {contador_mdc}")
    break
#Questão 22
while True:
    num = str(input("Digite um número entre 1000 e 9999: "))
    if len(num) < 4 or len(num) > 4:
        break
    numn = int(num)
    dois_primeiros = int(num[0:2])
    dois_ultimos = int(num[2:4])
    juncao = (dois_primeiros + dois_ultimos)
    juncao_2 = juncao ** 2
    if juncao_2 == numn and numn//100 == dois_primeiros and numn % 100 == dois_ultimos:
        print(f"{numn} possui a mesma característica que 3025")
    else: 
        print(f"{numn} não possui a mesma característica que 3025")
#23 Questão
total = 0
while True:
    cod_prod = int(input("Digite o código do produto: "))
    if cod_prod == 0:
        break
    preco_uni = float(input("Digite o valor unitário: "))
    quant = int(input("Digite a quantidade: "))
    total += preco_uni*quant
print(f"O valor total da compra: {total}")
#24 Questão
def calcularmedia(a, b):
    media = a/b
    return media
contagem = 0
total = 0
numeros = []
num = int(input("Digite um número: "))
while num != 0:
    numeros.append(num)
    num = int(input("Digite um número: "))
for i in numeros:
    total += i
    contagem += 1

print(f"Maior: {max(numeros)}   Menor:{min(numeros)}    Média: {calcularmedia(total, contagem)}")
#Questão 25
lista = []
entre_100_1000 = []
num = 0

while True:
    num = int(input("Digite um número: "))
    if num != -1:
        lista.append(num)
    else:
        break
for x in lista:
    if x > 100 and x < 1000:
      entre_100_1000.append(x)
if len(entre_100_1000) > 0:
    print(f" O menor valor entre 100 e 1000 é: {min(entre_100_1000)}")
    print(f"A média dos valores entre 100 e 1000 é: {(sum(entre_100_1000)/len(entre_100_1000)):.2f}")
    print(f"A soma de todos os valores entre 100 e 1000 é: {sum(entre_100_1000)}")
print(f"A soma de todos os valores é: {sum(lista)}") 
#Questão 26
lista = []
multiplosde8 = []

while True:
    num = int(input("Digite um número: "))
    if num == -1:
        break
    lista.append(num)
    print(lista)
for n in lista:
    if n % 8 == 0:
        multiplosde8.append(n)
print(len(multiplosde8))
if len(lista) > 0:
    print(f"{sum(lista)/len(lista):.2f}")
#Questão27:

primos = []
while True:
    num = int(input("Verifique se um número é primo: "))
    if num <= 0 :
        break
    resultado = True
    if num == 1:
        resultado = False
    for i in range(2, num):
        if num % i == 0:
            resultado = False
            break
    if resultado == True:
        primos.append(num)
        print(primos)
    
"""
#Questão 28
