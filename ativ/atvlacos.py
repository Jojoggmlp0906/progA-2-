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
"""
#Questão14
