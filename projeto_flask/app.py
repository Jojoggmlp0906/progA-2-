from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask(__name__)
app.secret_key = "090807"
clientes = {} #atualizei para dicionário, já que precisaríamos de muitas funções pra operar com listas

def fazerdeposito(saldo, deposito):
    total_deposito = saldo + deposito #realiza a conta para depositar e agrega ao valor já existente
    return total_deposito
def fazersaque(saldo, saque):
    total_saque = saldo - saque #realiza o saque da conta, subtraindo do valor existente
    return total_saque

#funções para operações matemáticas

@app.route("/")
def inicio():
    return render_template('index.html')

#Leva para a página inicial index.html

@app.route("/user", methods=['POST'])
def usuario():
    global clientes
    conta = request.form.get("conta")
    nome = request.form.get("nome")
    if not conta or not nome:
        return "Erro: Conta e nome são obrigatórios", 400
    if conta not in clientes:
        saldo_inicial = 0
        clientes[conta]={
            "nome": nome,
            "saldo": saldo_inicial
        }
    return render_template('opcoes.html', conta_html=conta, nome_html=clientes[conta]["nome"], saldo_atual=clientes[conta]["saldo"])

#criação de conta de usuário, não deixa a conta ser repetida, já que ela é única

@app.route("/ir-para-deposito", methods=['POST'])
def ir_para_deposito():
    global clientes
    conta = request.form.get("conta")
    return render_template('depositar.html', conta_html=conta, nome_html=clientes[conta]["nome"], saldo_atual=clientes[conta]["saldo"])

#leva para a página de depósito

@app.route("/ir-procurar", methods=["POST"])
def ir_procurar():
    return render_template("procurar_conta.html")
@app.route("/buscar", methods=["POST"])
def buscarConta():
    global clientes
    contabuscada = request.form.get("buscador")
    if contabuscada in clientes:
        nome = clientes[contabuscada]["nome"]
        saldo = clientes[contabuscada]["saldo"]
        # Mudamos de "danger" para "success" para ficar visualmente correto se achou
        flash(f"Conta encontrada: Nº {contabuscada} | Titular: {nome} | Saldo: R$ {saldo:.2f}", "success")
    else:
        flash("Conta não encontrada", "danger")
    return render_template("procurar_conta.html")
#Leva para a página de procurar contas

@app.route("/ir-para-saque", methods=['POST'])
def ir_para_saque():
    global clientes
    conta = request.form.get("conta")
    return render_template('sacar.html', conta_html=conta, nome_html=clientes[conta]["nome"], saldo_atual=clientes[conta]["saldo"])

#Leva para a página de saque

@app.route("/sacar", methods=['POST'])
def sacar():
    global clientes
    conta = request.form.get("conta")
    valor = float(request.form.get('valor_saque'))
    if valor <= clientes[conta]["saldo"]:
        clientes[conta]["saldo"] = fazersaque(clientes[conta]["saldo"], valor)
    return render_template('opcoes.html', nome_html=clientes[conta]["nome"] , saldo_atual=clientes[conta]["saldo"], conta_html=conta)

#Função executada na ação de saque

@app.route("/depositar", methods=['POST'])
def depositar():
    global clientes
    conta = request.form.get("conta")
    valor = float(request.form.get('valor_deposito'))
    if valor > 0:
        clientes[conta]["saldo"] = fazerdeposito(clientes[conta]["saldo"], valor)
    else:
        return "O valor precisa ser maior que zero"
    return render_template('opcoes.html', nome_html=clientes[conta]["nome"] ,saldo_atual=clientes[conta]["saldo"], conta_html=conta)

#Função para executar a ação de depósito

if __name__ == '__main__':
    app.run(debug=True)
#Faz o projeto rodar
