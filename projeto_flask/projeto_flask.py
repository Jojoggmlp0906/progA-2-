from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask(__name__)
app.secret_key = "090807"
class cliente:
    _contas = {}
    def __init__(self, conta:int, nome:str, saldo_inicial:float = 0):
        self.__conta = conta
        self._nome = nome
        self._saldo = saldo_inicial
        if self.__conta not in cliente._contas:
            cliente._contas[self.__conta]= self
    def deposito(self, vdeposito):
        if vdeposito > 0:
            self._saldo += vdeposito
    def saque(self, vsaque):
        if vsaque>0 and vsaque <= self._saldo:
            self._saldo -= vsaque
    def para_dict(self):
        return{
            "conta" : self.__conta,
            "nome" : self.__nome,
            "saldo" : self.__saldo
        }

#classes 

@app.route("/")
def inicio():
    return render_template('index.html')

#Leva para a página inicial index.html
@app.route("/ir-para-dados", methods=["POST"])
def bancoDados():
    return render_template("banco_de_dados.html", banco_dados=cliente._contas)

@app.route("/user", methods=['POST'])
def usuario():
    global nova_conta
    conta = request.form.get("conta")
    nome = request.form.get("nome")
    if not conta or not nome:
        return "Erro: Conta e nome são obrigatórios", 400
    if conta not in cliente._contas:
        nova_conta = cliente(conta, nome, saldo_inicial=0)
        
    return render_template('opcoes.html', conta_html=conta, nome_html=nova_conta._nome, saldo_atual=nova_conta._saldo)

#criação de conta de usuário, não deixa a conta ser repetida, já que ela é única

@app.route("/ir-para-deposito", methods=['POST'])
def ir_para_deposito():
    conta = request.form.get("conta")
    return render_template('depositar.html', conta_html=conta, nome_html=nova_conta._nome, saldo_atual=nova_conta._saldo)

#leva para a página de depósito

@app.route("/ir-procurar", methods=["POST"])
def ir_procurar():
    return render_template("procurar_conta.html")
@app.route("/buscar", methods=["POST"])
def buscarConta():
    contabuscada = request.form.get("buscador")
    if contabuscada in cliente._contas:
        # Mudamos de "danger" para "success" para ficar visualmente correto se achou
        conta_encontrada = cliente._contas[contabuscada]
        nome = conta_encontrada._nome
        saldo = conta_encontrada._saldo
        flash(f"Conta encontrada: Nº {contabuscada} | Titular: {nome} | Saldo: R$ {saldo:.2f}", "success")
    else:
        flash("Conta não encontrada", "danger")
    return render_template("procurar_conta.html")
#Leva para a página de procurar contas

@app.route("/ir-para-saque", methods=['POST'])
def ir_para_saque():
    conta = request.form.get("conta")
    return render_template('sacar.html', conta_html=conta, nome_html=nova_conta._nome, saldo_atual=nova_conta._saldo)

#Leva para a página de saque

@app.route("/sacar", methods=['POST'])
def sacar():
    global nova_conta
    conta = request.form.get("conta")
    valor = float(request.form.get('valor_saque'))
    if valor <= nova_conta._saldo:
        nova_conta.saque(valor)
    return render_template('opcoes.html', conta_html=conta, nome_html=nova_conta._nome, saldo_atual=nova_conta._saldo)

#Função executada na ação de saque

@app.route("/depositar", methods=['POST'])
def depositar():
    global nova_conta
    conta = request.form.get("conta")
    valor = float(request.form.get('valor_deposito'))
    if valor > 0:
        nova_conta.deposito(valor)
    else:
        return "O valor precisa ser maior que zero"
    return render_template('opcoes.html', conta_html=conta, nome_html=nova_conta._nome, saldo_atual=nova_conta._saldo)

#Função para executar a ação de depósito

if __name__ == '__main__':
    app.run(debug=True)
#Faz o projeto rodar