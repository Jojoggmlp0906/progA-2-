from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from abc import ABC, abstractmethod
import plotly.express as px
import pandas as pd
import json
import os

app = Flask(__name__)
app.secret_key = "090807"


class Cliente:
    def __init__(self, nome: str, cpf: str, salario: float, telefone: str):
        self.nome = nome
        self.cpf = cpf
        self.salario = float(salario)
        self.telefone = telefone
        self.contas = []  # 1 cliente pode ter N contas

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


class Conta(ABC):
    def __init__(self, numero: int, tipo: str, titular: Cliente, saldo: float = 0.0):
        self.numero = numero
        self.tipo = tipo  # "Corrente" ou "Poupança"
        self.titular = titular  # Objeto Cliente
        self._saldo = float(saldo)  # Protegido para acesso nas subclasses
        self.historico_transacoes = []
        # Dados simulados iniciais + saldo atual para o gráfico de evolução
        self.evolucao_anual = [
            {"mes": "Set", "valor": 1000.0},
            {"mes": "Out", "valor": 1150.0},
            {"mes": "Nov", "valor": self._saldo}
        ]

    @property
    def saldo(self):
        return self._saldo

    def depositar(self, valor: float, mes: str = "Nov"):
        if valor <= 0:
            return False, "O valor do depósito precisa ser maior que 0."
        self._saldo += valor
        self.historico_transacoes.append(
            f"Depósito de R$ {valor:.2f} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        # Registra o novo saldo na evolução anual
        self.evolucao_anual.append({"mes": mes, "valor": self._saldo})
        return True, "Depósito realizado com sucesso!"

    def sacar(self, valor: float, mes: str = "Nov"):
        if valor <= 0:
            return False, "O valor do saque precisa ser maior que 0."
        if valor > self._saldo:
            return False, "Saldo insuficiente para realizar o saque."
        self._saldo -= valor
        self.historico_transacoes.append(
            f"Saque de R$ {valor:.2f} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        # Registra o novo saldo na evolução anual
        self.evolucao_anual.append({"mes": mes, "valor": self._saldo})
        return True, "Saque realizado com sucesso!"

    def transferir(self, valor: float, conta_destino):
        sucesso, mensagem = self.sacar(valor)
        if not sucesso:
            return False, f"Falha na transferência: {mensagem}"

        conta_destino.depositar(valor)
        self.historico_transacoes[-1] = (
            f"Transferência enviada: R$ {valor:.2f} para conta {conta_destino.numero} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        conta_destino.historico_transacoes[-1] = (
            f"Transferência recebida: R$ {valor:.2f} da conta {self.numero} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        return True, "Transferência realizada com sucesso!"

    def exibir_historico_saldo(self):
        return {
            "saldo": self._saldo,
            "historico": self.historico_transacoes
        }


class ContaCorrente(Conta):
    def __init__(self, numero: int, titular: Cliente, saldo: float = 0.0, taxa_manutencao: float = 15.0):
        super().__init__(numero, "Corrente", titular, saldo)
        self.taxa_manutencao = taxa_manutencao

    def descontar_taxa(self):
        if self._saldo < self.taxa_manutencao:
            return False, "Saldo insuficiente para descontar a taxa de manutenção."
        self._saldo -= self.taxa_manutencao
        self.historico_transacoes.append(
            f"Desconto de taxa de manutenção: R$ {self.taxa_manutencao:.2f} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        self.evolucao_anual.append({"mes": "Nov", "valor": self._saldo})
        return True, "Taxa de manutenção descontada com sucesso!"


class ContaPoupanca(Conta):
    def __init__(self, numero: int, titular: Cliente, saldo: float = 0.0, taxa_rendimento: float = 0.005):
        super().__init__(numero, "Poupança", titular, saldo)
        self.taxa_rendimento = taxa_rendimento  # 0.5% padrão

    def aplicar_rendimento(self):
        rendimento = self._saldo * self.taxa_rendimento
        self._saldo += rendimento
        self.historico_transacoes.append(
            f"Rendimento aplicado: R$ {rendimento:.2f} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        self.evolucao_anual.append({"mes": "Nov", "valor": self._saldo})
        return True, f"Rendimento de R$ {rendimento:.2f} aplicado com sucesso!"


class Agencia:
    def __init__(self, nome: str, numero: str, arquivo_json: str = "dados_banco.json"):
        self.nome = nome
        self.numero = numero
        self.arquivo_json = arquivo_json
        self.lista_contas = {}    # {numero_conta: objeto_conta}
        self.lista_clientes = {}  # {cpf: objeto_cliente}
        self.correntes_criadas = 0
        self.poupancas_criadas = 0
        
        # Recupera os dados salvos assim que o servidor inicia
        self.carregar_dados()

    def cadastrar_cliente(self, nome: str, cpf: str, salario: float, telefone: str):
        if cpf in self.lista_clientes:
            return self.lista_clientes[cpf]
        novo_cliente = Cliente(nome, cpf, salario, telefone)
        self.lista_clientes[cpf] = novo_cliente
        self.salvar_dados()  # Persiste o novo cliente
        return novo_cliente

    def criar_conta(self, numero: int, tipo: str, cpf_titular: str, saldo_inicial: float = 0.0):
        numero = int(numero)
        if numero in self.lista_contas:
            return False, "Essa conta já existe na agência."

        cliente = self.lista_clientes.get(cpf_titular)
        if not cliente:
            return False, "Cliente não encontrado pelo CPF informado."

        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado in ["corrente", "cc", "conta corrente"]:
            nova_conta = ContaCorrente(numero, cliente, saldo_inicial)
            self.correntes_criadas += 1
        elif tipo_normalizado in ["poupança", "poupanca", "cp", "conta poupança", "conta poupanca"]:
            nova_conta = ContaPoupanca(numero, cliente, saldo_inicial)
            self.poupancas_criadas += 1
        else:
            return False, "Tipo de conta inválido. Escolha Corrente ou Poupança."

        self.lista_contas[numero] = nova_conta
        cliente.adicionar_conta(nova_conta)
        self.salvar_dados()  # Persiste a nova conta
        return True, "Conta criada com sucesso!"

    def buscar_conta(self, numero: int):
        return self.lista_contas.get(numero, None)

    def calcular_patrimonio_total(self):
        return sum(conta.saldo for conta in self.lista_contas.values())

    def GraficoPizza(self):
        dados_grafico = {
            "Tipos": ["Corrente", "Poupança"],
            "Quantidade": [self.correntes_criadas, self.poupancas_criadas]
        }
        df_tipos = pd.DataFrame(dados_grafico)
        fig_pizza = px.pie(df_tipos, values="Quantidade", names="Tipos", title="Distribuição de Contas - Agência 001")
        return fig_pizza.to_html(full_html=False, include_plotlyjs="cdn")

    def GraficoEvolucao(self, numero_conta: int):
        """Gera o gráfico de linha do crescimento do saldo ao longo do ano para uma conta."""
        conta = self.buscar_conta(int(numero_conta))
        if not conta:
            return ""
        df = pd.DataFrame(conta.evolucao_anual)
        fig = px.line(
            df,
            x="mes",
            y="valor",
            markers=True,
            title=f"Evolução do Saldo - Conta {conta.numero}"
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def salvar_dados(self):
        """Converte clientes e contas em dicionários simples e grava no arquivo JSON."""
        estrutura = {
            "correntes_criadas": self.correntes_criadas,
            "poupancas_criadas": self.poupancas_criadas,
            "clientes": {},
            "contas": {}
        }

        for cpf, cliente in self.lista_clientes.items():
            estrutura["clientes"][cpf] = {
                "nome": cliente.nome,
                "cpf": cliente.cpf,
                "salario": cliente.salario,
                "telefone": cliente.telefone
            }

        for num, conta in self.lista_contas.items():
            estrutura["contas"][str(num)] = {
                "numero": conta.numero,
                "tipo": conta.tipo,
                "cpf_titular": conta.titular.cpf,
                "saldo": conta._saldo,
                "historico_transacoes": conta.historico_transacoes,
                "evolucao_anual": conta.evolucao_anual
            }

        with open(self.arquivo_json, "w", encoding="utf-8") as f:
            json.dump(estrutura, f, indent=4, ensure_ascii=False)

    def carregar_dados(self):
        """Lê o arquivo JSON (se existir) e reconstrói os objetos na memória."""
        if not os.path.exists(self.arquivo_json):
            return

        with open(self.arquivo_json, "r", encoding="utf-8") as f:
            dados = json.load(f)

        self.correntes_criadas = dados.get("correntes_criadas", 0)
        self.poupancas_criadas = dados.get("poupancas_criadas", 0)

        # 1. Recria os clientes
        for cpf, info in dados.get("clientes", {}).items():
            self.lista_clientes[cpf] = Cliente(
                info["nome"], info["cpf"], info["salario"], info["telefone"]
            )

        # 2. Recria as contas e reconecta aos respectivos titulares
        for num_str, info in dados.get("contas", {}).items():
            titular = self.lista_clientes.get(info["cpf_titular"])
            if titular:
                num = int(info["numero"])
                if info["tipo"] == "Corrente":
                    conta = ContaCorrente(num, titular, info["saldo"])
                else:
                    conta = ContaPoupanca(num, titular, info["saldo"])

                conta.historico_transacoes = info.get("historico_transacoes", [])
                conta.evolucao_anual = info.get("evolucao_anual", conta.evolucao_anual)

                self.lista_contas[num] = conta
                titular.adicionar_conta(conta)


# Instância única da agência do banco
agencia_central = Agencia("Agência Central", "001")

# --- ROTAS DO FLASK ---

@app.route("/")
def inicio():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def fazerlogin():
    cpf = request.form.get("cpf")
    agencia = agencia_central.numero
    session["agencia"] = agencia
    if not cpf:
        flash("Digite o CPF (obrigatório)", "danger")
        return render_template("login.html")

    if cpf in agencia_central.lista_clientes:
        session["cpf_pendente"] = cpf
        cliente = agencia_central.lista_clientes[cpf]
        return render_template(
            "selecao_contas.html",
            cpf_html=cpf,
            nome_html=cliente.mostrar_nome,
            contas_html=cliente.contas,
            agencia_html=agencia
        )
    else:
        session["cpf_pendente"] = cpf
        return redirect(url_for("irparacadastro"))


@app.route("/ir-para-cadastro", methods=["GET", "POST"])
def irparacadastro():
    cpf_guardado = session.get("cpf_pendente", "")
    return render_template("cadastro.html", cpf_guardado=cpf_guardado, agencia_html=session.get("agencia"))


@app.route("/fazercadastro", methods=["POST"])
def fazercadastro():
    cpf = session.get("cpf_pendente", "")
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    salario = request.form.get("salario")

    if not nome or not cpf or not telefone or not salario:
        flash("Preencha todas as informações (obrigatório)", "danger")
        return render_template("cadastro.html", cpf_guardado=cpf)

    try:
        salario_float = float(salario.replace(',', '.'))
    except ValueError:
        flash("Digite um valor numérico válido para o salário.", "danger")
        return render_template("cadastro.html", cpf_guardado=cpf)

    agencia_central.cadastrar_cliente(nome, cpf, salario_float, telefone)
    return redirect(url_for("ircriarconta"))


@app.route("/ir-para-criar-conta", methods=["GET", "POST"])
def ircriarconta():
    return render_template("criacao_conta.html", agencia_html=session.get("agencia"))


@app.route("/criandoconta", methods=["POST"])
def CriandoConta():
    numero = request.form.get("numero")
    cpf = session.get("cpf_pendente")
    tipo = request.form.get("tipo")

    if not numero or not tipo:
        flash("É necessário preencher todas as informações", "danger")
        return render_template("criacao_conta.html")

    sucesso, msg = agencia_central.criar_conta(numero, tipo, cpf)
    if not sucesso:
        flash(msg, "danger")
        return render_template("criacao_conta.html")

    conta_cliente = agencia_central.lista_contas[int(numero)]
    cliente = agencia_central.lista_clientes[cpf]
    return render_template(
        "opcoes.html",
        nome_html=cliente.mostrar_nome,
        tipo_html=conta_cliente.tipo,
        conta_html=conta_cliente.numero,
        saldo_atual=conta_cliente.saldo
    )


@app.route("/ir-para-dados", methods=["POST"])
def bancoDados():
    conta = request.form.get("conta")
    return render_template(
        "banco_de_dados.html",
        contas=agencia_central.lista_contas,
        patrimonio=agencia_central.calcular_patrimonio_total(),
        conta_html=conta
    )


@app.route("/selecao", methods=["POST"])
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


@app.route("/ir-procurar", methods=["POST"])
def ir_procurar():
    conta = request.form.get("conta")
    return render_template("procurar_conta.html", conta_html=conta, agencia_html=session.get("agencia"))


@app.route("/buscar", methods=["POST"])
def buscarConta():
    contabuscada = request.form.get("buscador")
    conta_atual = request.form.get("conta")
    agencia = session.get("agencia")
    
    if not contabuscada:
        return "Erro: Conta é obrigatória", 400

    contabuscada = int(contabuscada)
    objeto_conta = agencia_central.buscar_conta(contabuscada)

    if objeto_conta:
        flash(
            f"Conta encontrada: Nº {contabuscada} ({objeto_conta.tipo}) | Ag: {agencia}| Titular: {objeto_conta.titular.nome} | Saldo: R$ {objeto_conta.saldo:.2f}",
            "success"
        )
    else:
        flash("Conta não encontrada", "danger")

    return render_template("procurar_conta.html", conta_html=conta_atual)


@app.route("/ir-para-deposito", methods=['POST'])
def ir_para_deposito():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatória", 400
    conta = int(conta)
    objeto_conta = agencia_central.buscar_conta(conta)

    return render_template(
        'depositar.html',
        conta_html=conta,
        nome_html=objeto_conta.titular.nome,
        saldo_atual=objeto_conta.saldo
    )


@app.route("/ir-para-saque", methods=['POST'])
def ir_para_saque():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatória", 400
    conta = int(conta)
    objeto_conta = agencia_central.buscar_conta(conta)

    return render_template(
        'sacar.html',
        conta_html=conta,
        nome_html=objeto_conta.titular.nome,
        saldo_atual=objeto_conta.saldo
    )


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
        return render_template(
            'opcoes.html',
            conta_html=conta,
            tipo_html=objeto_conta.tipo,
            nome_html=objeto_conta.titular.nome,
            saldo_atual=objeto_conta.saldo
        )

    sucesso, mensagem = objeto_conta.sacar(valor)
    if not sucesso:
        flash(mensagem, "danger")
    else:
        agencia_central.salvar_dados()  # Atualiza o JSON após o saque
        flash(mensagem, "success")

    return render_template(
        'opcoes.html',
        conta_html=objeto_conta.numero,
        tipo_html=objeto_conta.tipo,
        nome_html=objeto_conta.titular.nome,
        saldo_atual=objeto_conta.saldo
    )


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
        return render_template(
            'opcoes.html',
            conta_html=conta,
            tipo_html=objeto_conta.tipo,
            nome_html=objeto_conta.titular.nome,
            saldo_atual=objeto_conta.saldo
        )

    sucesso, mensagem = objeto_conta.depositar(valor)
    if not sucesso:
        flash(mensagem, "danger")
    else:
        agencia_central.salvar_dados()  # Atualiza o JSON após o depósito
        flash(mensagem, "success")

    return render_template(
        'opcoes.html',
        conta_html=objeto_conta.numero,
        tipo_html=objeto_conta.tipo,
        nome_html=objeto_conta.titular.nome,
        saldo_atual=objeto_conta.saldo
    )


@app.route("/ir-para-historico", methods=['POST'])
def ir_para_historico():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatória", 400
    conta = int(conta)
    objeto_conta = agencia_central.buscar_conta(conta)
    
    dados_historico = objeto_conta.exibir_historico_saldo()
    grafico_evolucao = agencia_central.GraficoEvolucao(conta)
    return render_template(
        'historico.html',
        conta_html=conta,
        nome_html=objeto_conta.titular.nome,
        saldo_atual=dados_historico["saldo"],
        historico=dados_historico["historico"],
        grafico_evolucao_html=grafico_evolucao  # Já disponível para usar no historico.html
    )


@app.route("/ir-para-transferencia", methods=['POST'])
def ir_para_transferencia():
    conta = request.form.get("conta")
    if not conta:
        return "Erro: Conta é obrigatória", 400
    
    try:
        conta = int(conta)
    except ValueError:
        return "Erro: Número de conta inválido", 400

    objeto_conta = agencia_central.buscar_conta(conta)

    if not objeto_conta:
        flash("Conta não encontrada.", "danger")
        return redirect(url_for("inicio"))

    return render_template(
        'transferir.html',
        conta_html=conta,
        nome_html=objeto_conta.titular.nome,
        saldo_atual=objeto_conta.saldo
    )


@app.route("/transferir", methods=['POST'])
def transferir():
    conta_origem_num = request.form.get("conta_origem")
    conta_destino_num = request.form.get("conta_destino")
    
    if not conta_origem_num or not conta_destino_num:
        flash("Conta de origem e de destino são obrigatórias.", "danger")
        return redirect(url_for("inicio"))

    conta_origem = agencia_central.buscar_conta(int(conta_origem_num))
    
    try:
        conta_destino_num = int(conta_destino_num)
        valor_str = request.form.get('valor_transferencia').replace(',', '.')
        valor = float(valor_str)
    except (ValueError, TypeError):
        flash("Por favor, digite um valor numérico e uma conta de destino válidos.", "danger")
        return render_template(
            'transferir.html',
            conta_html=conta_origem.numero,
            nome_html=conta_origem.titular.nome,
            saldo_atual=conta_origem.saldo
        )

    conta_destino = agencia_central.buscar_conta(conta_destino_num)
    if not conta_destino:
        flash("Conta de destino não encontrada na agência.", "danger")
        return render_template(
            'transferir.html',
            conta_html=conta_origem.numero,
            nome_html=conta_origem.titular.nome,
            saldo_atual=conta_origem.saldo
        )

    sucesso, mensagem = conta_origem.transferir(valor, conta_destino)
    
    if not sucesso:
        flash(mensagem, "danger")
    else:
        agencia_central.salvar_dados()  # Atualiza o JSON após a transferência
        flash(mensagem, "success")

    return render_template(
        'opcoes.html',
        conta_html=conta_origem.numero,
        tipo_html=conta_origem.tipo,
        nome_html=conta_origem.titular.nome,
        saldo_atual=conta_origem.saldo
    )


@app.route("/ir-painel", methods=["POST"])
def irpainel():
    grafico = agencia_central.GraficoPizza()
    return render_template("painel_contas.html", grafico_html=grafico)


@app.route("/voltar-opcoes", methods=['POST'])
def voltar_opcoes():
    conta = request.form.get("conta")
    if not conta:
        return redirect(url_for("inicio"))
    
    try:
        conta = int(conta)
    except ValueError:
        return redirect(url_for("inicio"))

    objeto_conta = agencia_central.buscar_conta(conta)
    if not objeto_conta:
        return redirect(url_for("inicio"))
    
    return render_template(
        'opcoes.html',
        conta_html=objeto_conta.numero,
        tipo_html=objeto_conta.tipo,
        nome_html=objeto_conta.titular.nome,
        saldo_atual=objeto_conta.saldo
    )


if __name__ == '__main__':
    app.run(debug=True)