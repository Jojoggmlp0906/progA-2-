from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask(__name__)
app.secret_key = "090807"

class Conta: # a classe Conta só vai ser responsável pelas operações dos objetos
    def __init__(self, conta:int, nome:str, saldo:float=0): 
        self._nome = nome
        self.__saldo = saldo
        self.__conta = conta

    @property #mostra o saldo
    def saldo(self):
        return self.__saldo
    @property #mostra a conta
    def conta(self):
        return self.__conta
    @property #mostra o nome
    def nome(self):
        return self._nome
    def deposito(self, valor:float): #Função de depósito
        if valor <= 0:
            print("O valor não pode ser menor ou igual a 0")
            return
        self.__saldo += valor
    def saque(self, valor:float): #Função de saque
        if valor <= 0:
          return "O Valor precisa ser maior que 0"
        if valor > self.__saldo:
            return "O valor precisa ser menor ou igual ao valor atual"
        self.__saldo -= valor
class Banco:# Classe responsável por gerar e trabalhar com o banco de dados
    def __init__(self): 
        self.__BancodeDados = {}
    def criarcontas(self, conta:int, nome:str): #Checa se a conta existe e se não, cria o objeto conta
        if conta in self.__BancodeDados:
            return False
        nova_conta = Conta(conta, nome)
        self.__BancodeDados[conta] = { #dicionário usado como banco de dados
            "informacoes_conta": nova_conta,
            "nome": nome
        }
    def mostrarobjeto(self, conta): #mostra o objeto dentro do dicionário, permitindo operações
        return self.__BancodeDados[conta]["informacoes_conta"]
    @property
    def mostrarBanco(self): #mostra o banco de dados
        return self.__BancodeDados
BancoDados = Banco() #cria o banco de dados universal

@app.route("/")
def inicio():
    return render_template('index.html')


@app.route("/ir-para-dados", methods=["POST"])
def bancoDados():
    return render_template("banco_de_dados.html", banco_dados=BancoDados.mostrarBanco)


@app.route("/user", methods=['POST'])
def usuario():
    conta = request.form.get("conta")
    nome = request.form.get("nome")
    if not conta or not nome:
        return "Erro: Conta e nome são obrigatórios", 400
    conta = int(conta)

    # Cria a conta apenas se ela não existir
    novo_cliente = BancoDados.criarcontas(conta, nome)
    objeto_cliente = BancoDados.mostrarobjeto(conta)
    # Resgata a conta enviada no formulário
    return render_template('opcoes.html', conta_html=conta, nome_html=nome, saldo_atual=objeto_cliente.saldo)


@app.route("/ir-procurar", methods=["POST"])
def ir_procurar():
    return render_template("procurar_conta.html")


@app.route("/buscar", methods=["POST"])
def buscarConta():
    contabuscada = request.form.get("buscador")
    if not contabuscada:
        return "Erro: Conta é Obrigatório", 400
    contabuscada = int(contabuscada)
    if contabuscada in BancoDados.mostrarBanco:
        objeto_cliente = BancoDados.mostrarobjeto(contabuscada)
        flash(f"Conta encontrada: Nº {contabuscada} | Titular: {objeto_cliente.nome} | Saldo: R$ {objeto_cliente.saldo:.2f}", "success")
    else:
        flash("Conta não encontrada", "danger")
    return render_template("procurar_conta.html")

@app.route("/ir-para-deposito", methods=['POST'])
def ir_para_deposito():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é Obrigatório", 400
    conta = int(conta)
    objeto_cliente = BancoDados.mostrarobjeto(conta)
    return render_template('depositar.html', conta_html=conta, nome_html=objeto_cliente.nome, saldo_atual=objeto_cliente.saldo)

@app.route("/ir-para-saque", methods=['POST'])
def ir_para_saque():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatório", 400
    conta = int(conta)
    objeto_cliente = BancoDados.mostrarobjeto(conta)
    return render_template('sacar.html', conta_html=conta, nome_html=objeto_cliente.nome, saldo_atual=objeto_cliente.saldo)


@app.route("/sacar", methods=['POST'])
def sacar():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatório"
    conta = int(conta)
    objeto_cliente = BancoDados.mostrarobjeto(conta)

    # Tratamento para aceitar vírgula/ponto e evitar crash ao digitar texto
    try:
        valor_str = request.form.get('valor_saque').replace(',', '.')
        valor = float(valor_str)
    except (ValueError, TypeError):
        flash("Por favor, digite um valor numérico válido.", "danger")
        return render_template('opcoes.html', conta_html=conta, nome_html=objeto_cliente.nome, saldo_atual=objeto_cliente.saldo)

    if valor <= objeto_cliente.saldo:
        objeto_cliente.saque(valor)
    else:
        flash("Saldo insuficiente!", "danger")

    return render_template('opcoes.html', conta_html=objeto_cliente.conta, nome_html=objeto_cliente.nome, saldo_atual=objeto_cliente.saldo)


@app.route("/depositar", methods=['POST'])
def depositar():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatório", 400
    conta = int(conta)
    objeto_cliente = BancoDados.mostrarobjeto(conta)

    # Tratamento para aceitar vírgula/ponto e evitar crash ao digitar texto
    try:
        valor_str = request.form.get('valor_deposito').replace(',', '.')
        valor = float(valor_str)
    except (ValueError, TypeError):
        flash("Por favor, digite um valor numérico válido.", "danger")
        return render_template('opcoes.html', conta_html=objeto_cliente.conta, nome_html=objeto_cliente.nome, saldo_atual=objeto_cliente.saldo)

    if valor > 0:
        objeto_cliente.deposito(valor)
    else:
        flash("O valor precisa ser maior que zero", "danger")

    return render_template('opcoes.html', conta_html=objeto_cliente.conta, nome_html=objeto_cliente.nome, saldo_atual=objeto_cliente.saldo)


if __name__ == '__main__':
    app.run(debug=True)

