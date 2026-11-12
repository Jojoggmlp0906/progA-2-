from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "090807"

class Cliente:
    def __init__(self, nome: str, cpf: str, salario: float, telefone: str):
        self.nome = nome
        self.cpf = cpf
        self.salario = salario
        self.telefone = telefone
        self.contas = [] # 1 cliente pode ter N contas
    @property
    def mostrar_cpf(self):
        return self.cpf
    @property
    def mostrar_nome(self):
        return self.nome
    @property
    def mostrar_contas(self):
        return self.contas
    def adicionar_conta(self, conta):
        self.contas.append(conta)


class Conta:
    def __init__(self, numero: int, tipo: str, titular: Cliente, saldo: float = 0.0):
        self.numero = numero
        self.tipo = tipo  # "Corrente" ou "Poupança"
        self.titular = titular  # Objeto Cliente
        self.__saldo = saldo
        self.historico_transacoes = []

    @property
    def saldo(self):
        return self.__saldo
    def depositar(self, valor: float):
        if valor <= 0:
            return False, "O valor do depósito precisa ser maior que 0."
        self.__saldo += valor
        self.historico_transacoes.append(f"Depósito de R$ {valor:.2f} em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        return True, "Depósito realizado com sucesso!"

    def sacar(self, valor: float):
        if valor <= 0:
            return False, "O valor do saque precisa ser maior que 0."
        if valor > self.__saldo:
            return False, "Saldo insuficiente para realizar o saque."
        self.__saldo -= valor
        self.historico_transacoes.append(f"Saque de R$ {valor:.2f} em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        return True, "Saque realizado com sucesso!"

    def transferir(self, valor: float, conta_destino):
        sucesso, mensagem = self.sacar(valor)
        if not sucesso:
            return False, f"Falha na transferência: {mensagem}"
        
        conta_destino.depositar(valor)
        self.historico_transacoes[-1] = f"Transferência enviada: R$ {valor:.2f} para conta {conta_destino.numero} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        conta_destino.historico_transacoes[-1] = f"Transferência recebida: R$ {valor:.2f} da conta {self.numero} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        return True, "Transferência realizada com sucesso!"


class Agencia():
    def __init__(self, nome: str, numero: int):
        self.nome = nome
        self.numero = numero
        self.lista_contas = {}    # {numero_conta: objeto_conta}
        self.lista_clientes = {}  # {cpf: objeto_cliente}

    def cadastrar_cliente(self, nome: str, cpf: str, salario: float, telefone: str):
        if cpf in self.lista_clientes:
            return self.lista_clientes[cpf]
        novo_cliente = Cliente(nome, cpf, salario, telefone)
        self.lista_clientes[cpf] = novo_cliente
        return novo_cliente

    def criar_conta(self, numero: int, tipo: str, cpf_titular: str, saldo_inicial: float = 0.0):
        numero = int(numero) # Garante que o número seja inteiro
        if numero in self.lista_contas:
            return False, "Essa conta já existe na agência."
    
        cliente = self.lista_clientes.get(cpf_titular)
        if not cliente:
            return False, "Cliente não encontrado pelo CPF informado."

        nova_conta = Conta(numero, tipo, cliente, saldo_inicial)
        self.lista_contas[numero] = nova_conta # Salva direto pelo número da conta
        cliente.adicionar_conta(nova_conta)
        return True, "Conta criada com sucesso!"

    def buscar_conta(self, numero: int):
        return self.lista_contas.get(numero, None)

    def calcular_patrimonio_total(self):
        return sum(conta.saldo for conta in self.lista_contas.values())


# Instância única da agência do banco
agencia_central = Agencia("Agência Central", 1)


# --- ROTAS DO FLASK ---

@app.route("/")
def inicio():
    return render_template("login.html")
@app.route("/login", methods=["POST"])
def fazerlogin(): #Primeira tela de login, busca se o cpf já existe no banco de dados
    cpf = request.form.get("cpf")
    if not cpf:
        flash("Digite o CPF (obrigatório)", "danger")
        return render_template("login.html")
    
    if cpf in agencia_central.lista_clientes:
        session["cpf_pendente"] = cpf
        cliente = agencia_central.lista_clientes[cpf]
        return render_template("selecao_contas.html", cpf_html=cpf, nome_html=cliente.mostrar_nome, contas_html=cliente.contas)
    else:
        session["cpf_pendente"] = cpf
        return redirect(url_for("irparacadastro"))
"""
A segunda rota é para pedir outras informações e criar os objetos cliente e conta

"""
@app.route("/ir-para-cadastro", methods=["GET", "POST"])
def irparacadastro():
    cpf_guardado = session.get("cpf_pendente", "")
    return render_template("cadastro.html", cpf_guardado=cpf_guardado)
@app.route("/fazercadastro", methods=["POST"]) #realiza o cadastro
def fazercadastro():
    cpf = session.get("cpf_pendente", "")
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    salario = request.form.get("salario")
    
    if not nome or not cpf or not telefone or not salario:
        flash("Preencha todas as informações (obrigatório)", "danger") # Chamado separado
        return render_template("cadastro.html")
        
    agencia_central.cadastrar_cliente(nome, cpf, salario, telefone)
    return redirect(url_for("ircriarconta"))

@app.route("/ir-para-criar-conta", methods=["GET", "POST"]) #cria o objeto conta e puxa outras informações
def ircriarconta():
    return render_template("criacao_conta.html")
@app.route("/criandoconta", methods=["POST"])
def CriandoConta():
    numero = request.form.get("numero")
    cpf = session.get("cpf_pendente")
    tipo = request.form.get("tipo")
    
    if not numero or not tipo:
        flash("É necessário preencher todas as informações", "danger") # Chamado separado
        return render_template("criacao_conta.html")
        
    sucesso, msg = agencia_central.criar_conta(numero, tipo, cpf)
    if not sucesso:
        flash(msg, "danger")
        return render_template("criacao_conta.html")
        
    conta_cliente = agencia_central.lista_contas[int(numero)]
    cliente = agencia_central.lista_clientes[cpf]
    return render_template("opcoes.html", nome_html=cliente.mostrar_nome, tipo_html=conta_cliente.tipo, conta_html=conta_cliente.numero, saldo_atual=conta_cliente.saldo)

@app.route("/ir-para-dados", methods=["POST"]) #mostrar o banco de dados
def bancoDados():
    return render_template("banco_de_dados.html", contas=agencia_central.lista_contas, patrimonio=agencia_central.calcular_patrimonio_total())

@app.route("/selecao", methods=["POST"]) #trabalha com a parte de seleção caso o cpf já exista
def selecionarconta():
    numero_conta = request.form.get("contaselecionada")
    if not numero_conta:
        flash("Selecione uma conta.", "danger")
        return redirect(url_for("inicio"))
        
    conta_cliente = agencia_central.buscar_conta(int(numero_conta))
    return render_template(
        "opcoes.html",
        nome_html=conta_cliente.titular.nome,
        tipo_html=conta_cliente.tipo,
        conta_html=conta_cliente.numero,
        saldo_atual=conta_cliente.saldo
    )

@app.route("/ir-procurar", methods=["POST"]) #procura se a conta existe no Banco de Dados
def ir_procurar():
    return render_template("procurar_conta.html")


@app.route("/buscar", methods=["POST"])
def buscarConta():
    contabuscada = request.form.get("buscador")
    if not contabuscada:
        return "Erro: Conta é obrigatória", 400
    
    contabuscada = int(contabuscada)
    objeto_conta = agencia_central.buscar_conta(contabuscada)

    if objeto_conta:
        flash(f"Conta encontrada: Nº {contabuscada} ({objeto_conta.tipo}) | Titular: {objeto_conta.titular.nome} | Saldo: R$ {objeto_conta.saldo:.2f}", "success")
    else:
        flash("Conta não encontrada", "danger")
        
    return render_template("procurar_conta.html")


@app.route("/ir-para-deposito", methods=['POST'])
def ir_para_deposito():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatória", 400
    conta = int(conta)
    objeto_conta = agencia_central.buscar_conta(conta)
    
    return render_template('depositar.html', conta_html=conta, nome_html=objeto_conta.titular.nome, saldo_atual=objeto_conta.saldo)


@app.route("/ir-para-saque", methods=['POST'])
def ir_para_saque():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatória", 400
    conta = int(conta)
    objeto_conta = agencia_central.buscar_conta(conta)
    
    return render_template('sacar.html', conta_html=conta, nome_html=objeto_conta.titular.nome, saldo_atual=objeto_conta.saldo)


@app.route("/sacar", methods=['POST'])
def sacar():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatória", 400
    conta = int(conta)
    objeto_conta = agencia_central.buscar_conta(conta)

    try:
        valor_str = request.form.get('valor_saque').replace(',', '.')
        valor = float(valor_str)
    except (ValueError, TypeError):
        flash("Por favor, digite um valor numérico válido.", "danger")
        return render_template('opcoes.html', conta_html=conta, tipo_html=objeto_conta.tipo, nome_html=objeto_conta.titular.nome, saldo_atual=objeto_conta.saldo)

    sucesso, mensagem = objeto_conta.sacar(valor)
    if not sucesso:
        flash(mensagem, "danger")
    else:
        flash(mensagem, "success")

    return render_template('opcoes.html', conta_html=objeto_conta.numero, tipo_html=objeto_conta.tipo, nome_html=objeto_conta.titular.nome, saldo_atual=objeto_conta.saldo)


@app.route("/depositar", methods=['POST'])
def depositar():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatória", 400
    conta = int(conta)
    objeto_conta = agencia_central.buscar_conta(conta)

    try:
        valor_str = request.form.get('valor_deposito').replace(',', '.')
        valor = float(valor_str)
    except (ValueError, TypeError):
        flash("Por favor, digite um valor numérico válido.", "danger")
        return render_template('opcoes.html', conta_html=conta, tipo_html=objeto_conta.tipo, nome_html=objeto_conta.titular.nome, saldo_atual=objeto_conta.saldo)

    sucesso, mensagem = objeto_conta.depositar(valor)
    if not sucesso:
        flash(mensagem, "danger")
    else:
        flash(mensagem, "success")

    return render_template('opcoes.html', conta_html=objeto_conta.numero, tipo_html=objeto_conta.tipo, nome_html=objeto_conta.titular.nome, saldo_atual=objeto_conta.saldo)


if __name__ == '__main__':
    app.run(debug=True)