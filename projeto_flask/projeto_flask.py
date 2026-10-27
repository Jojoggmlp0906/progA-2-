from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask(__name__)
app.secret_key = "090807"

class cliente:
    _contas = {}
    
    def __init__(self, conta: str, nome: str, saldo_inicial: float = 0):
        self.conta = conta
        self.nome = nome
        self._saldo = saldo_inicial
        
        # Se a conta não existe no dicionário da classe, então ela é adicionada
        if self.conta not in cliente._contas:
            cliente._contas[self.conta] = self

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, valor):
        if valor >= 0:
            self._saldo = valor

    def deposito(self, vdeposito):
        if vdeposito > 0:
            self._saldo += vdeposito

    def saque(self, vsaque):
        if 0 < vsaque <= self._saldo:
            self._saldo -= vsaque
            return True
        return False


@app.route("/")
def inicio():
    return render_template('index.html')

@app.route("/ir-para-dados", methods=["POST"])
def bancoDados():
    return render_template("banco_de_dados.html", banco_dados=cliente._contas)

@app.route("/user", methods=['POST'])
def usuario():
    conta = request.form.get("conta")
    nome = request.form.get("nome")
    if not conta or not nome:
        return "Erro: Conta e nome são obrigatórios", 400
    
    # Cria a conta apenas se ela não existir
    if conta not in cliente._contas:
        cliente(conta, nome, saldo_inicial=0)

    # Resgata a conta enviada no formulário
    c = cliente._contas[conta]
    return render_template('opcoes.html', conta_html=c.conta, nome_html=c.nome, saldo_atual=c.saldo)

@app.route("/ir-para-deposito", methods=['POST'])
def ir_para_deposito():
    conta = request.form.get("conta")
    c = cliente._contas[conta]
    return render_template('depositar.html', conta_html=c.conta, nome_html=c.nome, saldo_atual=c.saldo)

@app.route("/ir-procurar", methods=["POST"])
def ir_procurar():
    return render_template("procurar_conta.html")

@app.route("/buscar", methods=["POST"])
def buscarConta():
    contabuscada = request.form.get("buscador")
    if contabuscada in cliente._contas:
        c = cliente._contas[contabuscada]
        flash(f"Conta encontrada: Nº {contabuscada} | Titular: {c.nome} | Saldo: R$ {c.saldo:.2f}", "success")
    else:
        flash("Conta não encontrada", "danger")
    return render_template("procurar_conta.html")

@app.route("/ir-para-saque", methods=['POST'])
def ir_para_saque():
    conta = request.form.get("conta")
    c = cliente._contas[conta]
    return render_template('sacar.html', conta_html=c.conta, nome_html=c.nome, saldo_atual=c.saldo)

@app.route("/sacar", methods=['POST'])
def sacar():
    conta = request.form.get("conta")
    c = cliente._contas[conta]
    
    # Tratamento para aceitar vírgula/ponto e evitar crash ao digitar texto
    try:
        valor_str = request.form.get('valor_saque').replace(',', '.')
        valor = float(valor_str)
    except (ValueError, TypeError):
        flash("Por favor, digite um valor numérico válido.", "danger")
        return render_template('opcoes.html', conta_html=c.conta, nome_html=c.nome, saldo_atual=c.saldo)
    
    if valor <= c.saldo:
        c.saque(valor)
    else:
        flash("Saldo insuficiente!", "danger")
        
    return render_template('opcoes.html', conta_html=c.conta, nome_html=c.nome, saldo_atual=c.saldo)

@app.route("/depositar", methods=['POST'])
def depositar():
    conta = request.form.get("conta")
    c = cliente._contas[conta]
    
    # Tratamento para aceitar vírgula/ponto e evitar crash ao digitar texto
    try:
        valor_str = request.form.get('valor_deposito').replace(',', '.')
        valor = float(valor_str)
    except (ValueError, TypeError):
        flash("Por favor, digite um valor numérico válido.", "danger")
        return render_template('opcoes.html', conta_html=c.conta, nome_html=c.nome, saldo_atual=c.saldo)
    
    if valor > 0:
        c.deposito(valor)
    else:
        flash("O valor precisa ser maior que zero", "danger")
        
    return render_template('opcoes.html', conta_html=c.conta, nome_html=c.nome, saldo_atual=c.saldo)

if __name__ == '__main__':
    app.run(debug=True)