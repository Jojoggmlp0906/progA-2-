from flask import Flask, render_template, request, redirect, url_for, flash
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


class Agencia:
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
        if numero in self.lista_contas:
            return False, "Essa conta já existe na agência."
        
        cliente = self.lista_clientes.get(cpf_titular)
        if not cliente:
            return False, "Cliente não encontrado pelo CPF informado."

        nova_conta = Conta(numero, tipo, cliente, saldo_inicial)
        self.lista_contas[numero] = nova_conta
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
    return render_template('index.html')


@app.route("/ir-para-dados", methods=["POST"])
def bancoDados():
    return render_template("banco_de_dados.html", contas=agencia_central.lista_contas, patrimonio=agencia_central.calcular_patrimonio_total())


@app.route("/user", methods=['POST'])
def usuario():
    # Coleta dados do cliente
    nome = request.form.get("nome")
    cpf = request.form.get("cpf")
    salario = float(request.form.get("salario", 0))
    telefone = request.form.get("telefone")

    # Coleta dados da conta
    conta_num = request.form.get("conta")
    tipo_conta = request.form.get("tipo_conta", "Corrente")

    if not conta_num or not nome or not cpf:
        return "Erro: Preencha todos os campos obrigatórios", 400
    
    conta_num = int(conta_num)

    # 1. Cadastra ou recupera o cliente
    cliente = agencia_central.cadastrar_cliente(nome, cpf, salario, telefone)

    # 2. Verifica se a conta já existe para permitir o login direto
    objeto_conta = agencia_central.buscar_conta(conta_num)

    if objeto_conta:
        # Conta já existe: apenas segue para as opções
        pass
    else:
        # Conta não existe: cria uma nova
        sucesso, mensagem = agencia_central.criar_conta(conta_num, tipo_conta, cpf)
        if not sucesso:
            flash(mensagem, "danger")
            return redirect(url_for('inicio'))
        objeto_conta = agencia_central.buscar_conta(conta_num)
    
    return render_template('opcoes.html', 
                           conta_html=objeto_conta.numero, 
                           tipo_html=objeto_conta.tipo,
                           nome_html=cliente.nome, 
                           saldo_atual=objeto_conta.saldo)


@app.route("/ir-procurar", methods=["POST"])
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