from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from datetime import datetime
from abc import ABC, abstractmethod
import plotly.express as px
import pandas as pd
import json
import os
import io

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
        self.transacoes: list[Transacao] = []
        self.historico_transacoes: list[str] = []
        # Dados simulados iniciais + saldo atual para o gráfico de evolução
        self.evolucao_mensal = [
            {"mes": "Set", "valor": 1000.0},
            {"mes": "Out", "valor": 1150.0},
            {"mes": "Nov", "valor": self._saldo}
        ]

    @property
    def saldo(self):
        return self._saldo

    def registrar_transacao(self, tipo: str, valor: float, mes: str = "Nov", descricao: str = "") -> Transacao:
        transacao = Transacao(tipo=tipo, valor=valor, descricao=descricao)
        self.transacoes.append(transacao)
        self.historico_transacoes.append(transacao.formatar_texto())
        self.evolucao_mensal.append({"mes": mes, "valor": self._saldo})
        return transacao

    def depositar(self, valor: float, mes: str = "Nov", tipo: str = "DEPOSITO", descricao: str = ""):
        if valor <= 0:
            return False, "O valor do depósito precisa ser maior que 0."
        self._saldo += valor
        self.registrar_transacao(tipo=tipo, valor=valor, mes=mes, descricao=descricao)
        return True, "Depósito realizado com sucesso!"

    def sacar(self, valor: float, mes: str = "Nov", tipo: str = "SAQUE", descricao: str = ""):
        if valor <= 0:
            return False, "O valor do saque precisa ser maior que 0."
        if valor > self._saldo:
            return False, "Saldo insuficiente para realizar o saque."
        self._saldo -= valor
        self.registrar_transacao(tipo=tipo, valor=valor, mes=mes, descricao=descricao)
        return True, "Saque realizado com sucesso!"

    def transferir(self, valor: float, conta_destino, mes: str = "Nov"):
        if self.numero == conta_destino.numero:
            return False, "Falha na transferência: não é possível transferir para a mesma conta."

        sucesso, mensagem = self.sacar(
            valor,
            mes=mes,
            tipo="TRANSFERENCIA",
            descricao=f"enviada para conta {conta_destino.numero}",
        )
        if not sucesso:
            return False, f"Falha na transferência: {mensagem}"

        sucesso_dest, msg_dest = conta_destino.depositar(
            valor,
            mes=mes,
            tipo="TRANSFERENCIA",
            descricao=f"recebida da conta {self.numero}",
        )
        if not sucesso_dest:
            # Estorna o saldo e desfaz os registros da origem se o depósito falhar
            self._saldo += valor
            self.transacoes.pop()
            self.historico_transacoes.pop()
            self.evolucao_mensal.pop()
            return False, f"Falha na transferência: {msg_dest}"

        return True, "Transferência realizada com sucesso!"

    def exibir_historico_saldo(self):
        return {
            "saldo": self._saldo,
            "historico": self.historico_transacoes,
            "transacoes": [t.to_dict() for t in self.transacoes]
        }
class Transacao:
    """Representa uma transação financeira associada a uma conta."""
    TIPOS_VALIDOS = {"SAQUE", "DEPOSITO", "TRANSFERENCIA", "PIX", "TAXA", "RENDIMENTO"}

    def __init__(self, tipo: str, valor: float, data: datetime | None = None, descricao: str = ""):
        tipo_normalizado = tipo.strip().upper()
        if tipo_normalizado not in self.TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido: {tipo}. Use um dos tipos válidos: {self.TIPOS_VALIDOS}")
        if float(valor) <= 0:
            raise ValueError("O valor digitado precisa ser maior que zero.")

        self.tipo = tipo_normalizado
        self.valor = float(valor)
        self.data = data if data is not None else datetime.now()
        self.descricao = descricao

    def formatar_texto(self) -> str:
        data_fmt = self.data.strftime("%d/%m/%Y %H:%M")
        extra = f" ({self.descricao})" if self.descricao else ""
        return f"{self.tipo.capitalize()}: R$ {self.valor:.2f}{extra} em {data_fmt}"

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo,
            "valor": self.valor,
            "data": self.data.isoformat(),
            "descricao": self.descricao,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Transacao":
        data_raw = dados.get("data")
        if isinstance(data_raw, datetime):
            data_obj = data_raw
        elif isinstance(data_raw, str) and data_raw:
            try:
                data_obj = datetime.fromisoformat(data_raw)
            except ValueError:
                data_obj = datetime.strptime(data_raw, "%d/%m/%Y %H:%M")
        else:
            data_obj = datetime.now()

        return cls(
            tipo=dados["tipo"],
            valor=float(dados["valor"]),
            data=data_obj,
            descricao=dados.get("descricao", ""),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __repr__(self) -> str:
        return (
            f"Transacao(tipo={self.tipo!r}, valor={self.valor:.2f}, "
            f"data={self.data.strftime('%Y-%m-%d %H:%M:%S')!r})"
        )
        
            

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
        self.evolucao_mensal.append({"mes": "Nov", "valor": self._saldo})
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
        self.evolucao_mensal.append({"mes": "Nov", "valor": self._saldo})
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
        return fig_pizza.to_html()

    
    def GraficoMediaSalarial(self): #Gera o gráfico de média salarial a partir dos salarios dos usuários
        """Gera um gráfico de barras com a média salarial dos titulares por tipo de conta."""
        if not self.lista_contas:
            return ""

        registros = [
            {
                "Tipo de Conta": conta.tipo,
                "Conta": str(conta.numero),
                "Titular": conta.titular.nome,
                "Salario": float(conta.titular.salario),
            }
            for conta in self.lista_contas.values()
        ]

        df = pd.DataFrame(registros)
        df_media = df.groupby("Tipo de Conta", as_index=False)["Salario"].mean()

        fig = px.bar(
            df_media,
            x="Tipo de Conta",
            y="Salario",
            text_auto=".2f",
            labels={"Tipo de Conta": "Tipo de Conta", "Salario": "Média Salarial (R$)"},
            title="Média Salarial por Tipo de Conta",
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
            # Em salvar_dados(), dentro do loop `for num, conta in self.lista_contas.items():`
            estrutura["contas"][str(num)] = {
                "numero": conta.numero,
                "tipo": conta.tipo,
                "cpf_titular": conta.titular.cpf,
                "saldo": conta._saldo,
                "historico_transacoes": conta.historico_transacoes,
                "transacoes": [t.to_dict() for t in conta.transacoes],
                "evolucao_mensal": conta.evolucao_mensal
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

                conta.transacoes = [
                    Transacao.from_dict(item) for item in info.get("transacoes", [])
                ]
                conta.historico_transacoes = info.get(
                    "historico_transacoes",
                    [t.formatar_texto() for t in conta.transacoes]
                )
                conta.evolucao_mensal = info.get("evolucao_mensal", conta.evolucao_mensal)

                self.lista_contas[num] = conta
                titular.adicionar_conta(conta)
    def GraficoPatrimonioCliente(self, cpf_cliente: str) -> str:
        """1. Gráfico de Pizza: Distribuição do patrimônio entre as contas de um cliente."""
        cliente = self.lista_clientes.get(cpf_cliente)
        if not cliente or not cliente.contas:
            return "<p>Nenhuma conta encontrada para este cliente.</p>"

        dados = [
            {
                "Conta": f"Conta {c.numero} ({c.tipo})",
                "Saldo": max(0.0, float(c.saldo))
            }
            for c in cliente.contas
        ]
        df = pd.DataFrame(dados)

        if df["Saldo"].sum() == 0:
            return "<p>O cliente ainda não possui saldo positivo distribuído nas contas.</p>"

        fig = px.pie(
            df,
            values="Saldo",
            names="Conta",
            title=f"Distribuição de Patrimônio - {cliente.nome}",
            hole=0.35
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def GraficoSaquesDepositosMensais(self, numero_conta: int) -> str:
        """2. Gráfico de Barras: Comparação de saques e depósitos ao longo dos meses."""
        conta = self.buscar_conta(int(numero_conta))
        if not conta or not conta.transacoes:
            return "<p>Sem transações registradas para comparar saques e depósitos.</p>"

        meses_pt = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
        }

        registros = []
        for t in conta.transacoes:
            if t.tipo in {"SAQUE", "DEPOSITO"}:
                rotulo_mes = f"{meses_pt[t.data.month]}/{t.data.year}"
                registros.append({
                    "Mes": rotulo_mes,
                    "DataOrdenacao": t.data.strftime("%Y-%m"),
                    "Operacao": "Depósitos" if t.tipo == "DEPOSITO" else "Saques",
                    "Valor": float(t.valor)
                })

        if not registros:
            return "<p>Nenhum saque ou depósito registrado ainda nesta conta.</p>"

        df = pd.DataFrame(registros)
        df_agrupado = (
            df.groupby(["DataOrdenacao", "Mes", "Operacao"], as_index=False)["Valor"]
            .sum()
            .sort_values("DataOrdenacao")
        )

        fig = px.bar(
            df_agrupado,
            x="Mes",
            y="Valor",
            color="Operacao",
            barmode="group",
            text_auto=".2f",
            color_discrete_map={"Depósitos": "#2ecc71", "Saques": "#e74c3c"},
            labels={"Mes": "Mês", "Valor": "Total Movimentado (R$)", "Operacao": "Tipo"},
            title=f"Saques vs. Depósitos por Mês - Conta {conta.numero}"
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def GraficoEvolucaoSaldoTransacoes(self, numero_conta: int) -> str:
        """3. Gráfico de Linhas: Evolução do saldo e transações ao longo do tempo."""
        conta = self.buscar_conta(int(numero_conta))
        if not conta:
            return ""

        # Se houver transações estruturadas, reconstrói a linha do tempo exata
        if conta.transacoes:
            transacoes_ordenadas = sorted(conta.transacoes, key=lambda x: x.data)
            
            # Calcula o saldo inicial antes da primeira transação registrada
            variacao_total = sum(
                t.valor if t.tipo in {"DEPOSITO", "RENDIMENTO"} or (t.tipo == "TRANSFERENCIA" and "recebida" in t.descricao)
                else -t.valor
                for t in transacoes_ordenadas
            )
            saldo_corrente = conta.saldo - variacao_total

            pontos = []
            for t in transacoes_ordenadas:
                if t.tipo in {"DEPOSITO", "RENDIMENTO"} or (t.tipo == "TRANSFERENCIA" and "recebida" in t.descricao):
                    saldo_corrente += t.valor
                else:
                    saldo_corrente -= t.valor

                pontos.append({
                    "Data": t.data.strftime("%d/%m/%Y %H:%M"),
                    "Saldo": round(saldo_corrente, 2),
                    "ValorTransacao": round(t.valor, 2),
                    "Detalhe": f"{t.tipo} (R$ {t.valor:.2f})"
                })

            df = pd.DataFrame(pontos)
            fig = px.line(
                df,
                x="Data",
                y="Saldo",
                markers=True,
                hover_data={"Detalhe": True, "ValorTransacao": ":.2f"},
                labels={"Data": "Data / Hora", "Saldo": "Saldo (R$)"},
                title=f"Evolução do Saldo e Transações - Conta {conta.numero}"
            )
            return fig.to_html(full_html=False, include_plotlyjs="cdn")

        # Fallback caso a conta só tenha os dados iniciais de evolucao_mensal
        df_fallback = pd.DataFrame(conta.evolucao_mensal)
        fig = px.line(
            df_fallback,
            x="mes",
            y="valor",
            markers=True,
            labels={"mes": "Mês", "valor": "Saldo (R$)"},
            title=f"Evolução do Saldo - Conta {conta.numero}"
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
    def exportar_json_texto(self) -> str:
        """Retorna todo o banco de dados formatado como string JSON."""
        self.salvar_dados()
        with open(self.arquivo_json, "r", encoding="utf-8") as f:
            return f.read()

    def exportar_csv_texto(self) -> str:
        """Exporta as contas e titulares em formato CSV usando pandas."""
        linhas = []
        for num, conta in self.lista_contas.items():
            linhas.append({
                "numero": conta.numero,
                "tipo": conta.tipo,
                "saldo": conta.saldo,
                "cpf": conta.titular.cpf,
                "nome": conta.titular.nome,
                "salario": conta.titular.salario,
                "telefone": conta.titular.telefone,
            })

        colunas = ["numero", "tipo", "saldo", "cpf", "nome", "salario", "telefone"]
        df = pd.DataFrame(linhas, columns=colunas)
        return df.to_csv(index=False, encoding="utf-8")

    def importar_arquivo(self, arquivo_storage):
        """Importa dados de um arquivo .json ou .csv enviado pelo formulário."""
        if not arquivo_storage or arquivo_storage.filename == "":
            return False, "Nenhum arquivo selecionado."

        nome_arquivo = arquivo_storage.filename.lower()

        try:
            if nome_arquivo.endswith(".json"):
                conteudo = arquivo_storage.read().decode("utf-8")
                dados = json.loads(conteudo)

                if "clientes" not in dados or "contas" not in dados:
                    return False, "Arquivo JSON inválido: chaves 'clientes' ou 'contas' ausentes."

                with open(self.arquivo_json, "w", encoding="utf-8") as f:
                    json.dump(dados, f, indent=4, ensure_ascii=False)

                # Limpa a memória atual e recarrega a partir do JSON importado
                self.lista_clientes.clear()
                self.lista_contas.clear()
                self.carregar_dados()
                return True, "Dados importados do JSON com sucesso!"

            elif nome_arquivo.endswith(".csv"):
                df = pd.read_csv(arquivo_storage, dtype={"cpf": str, "telefone": str})
                colunas_necessarias = {"numero", "tipo", "saldo", "cpf", "nome", "salario", "telefone"}
                if not colunas_necessarias.issubset(set(df.columns)):
                    return False, f"CSV inválido. Colunas esperadas: {', '.join(sorted(colunas_necessarias))}"

                for _, row in df.iterrows():
                    cpf = str(row["cpf"]).strip()
                    cliente = self.cadastrar_cliente(
                        nome=str(row["nome"]).strip(),
                        cpf=cpf,
                        salario=float(row["salario"]),
                        telefone=str(row["telefone"]).strip(),
                    )
                    num_conta = int(row["numero"])
                    saldo = float(row["saldo"])
                    tipo = str(row["tipo"]).strip()

                    if num_conta not in self.lista_contas:
                        self.criar_conta(num_conta, tipo, cliente.cpf, saldo)
                    else:
                        self.lista_contas[num_conta]._saldo = saldo

                self.salvar_dados()
                return True, "Dados importados do CSV com sucesso!"

            else:
                return False, "Formato não suportado. Envie um arquivo .json ou .csv."

        except Exception as e:
            return False, f"Erro ao importar arquivo: {e}"

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
    
    # Gera os gráficos da conta e do cliente titular
    grafico_evolucao = agencia_central.GraficoEvolucaoSaldoTransacoes(conta)
    grafico_barras = agencia_central.GraficoSaquesDepositosMensais(conta)
    grafico_pizza_cliente = agencia_central.GraficoPatrimonioCliente(objeto_conta.titular.cpf)

    return render_template(
        'historico.html',
        conta_html=conta,
        nome_html=objeto_conta.titular.nome,
        saldo_atual=dados_historico["saldo"],
        historico=dados_historico["historico"],
        grafico_evolucao_html=grafico_evolucao,
        grafico_barras_html=grafico_barras,
        grafico_pizza_html=grafico_pizza_cliente
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
    grafico_pizza = agencia_central.GraficoPizza()
    grafico_barras = agencia_central.GraficoMediaSalarial()
    return render_template("painel_contas.html", grafico_pizza_html=grafico_pizza, grafico_barras_html=grafico_barras)


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

@app.route("/exportar-dados", methods=["POST"])
def exportar_dados():
    formato = request.form.get("formato", "json").lower()

    if formato == "csv":
        csv_conteudo = agencia_central.exportar_csv_texto()
        return Response(
            csv_conteudo,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=dados_banco.csv"},
        )

    json_conteudo = agencia_central.exportar_json_texto()
    return Response(
        json_conteudo,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=dados_banco.json"},
    )


@app.route("/importar-dados", methods=["POST"])
def importar_dados():
    conta = request.form.get("conta")
    arquivo = request.files.get("arquivo_dados")

    sucesso, mensagem = agencia_central.importar_arquivo(arquivo)
    flash(mensagem, "success" if sucesso else "danger")

    return render_template(
        "banco_de_dados.html",
        contas=agencia_central.lista_contas,
        patrimonio=agencia_central.calcular_patrimonio_total(),
        conta_html=conta,
    )

if __name__ == '__main__':
    app.run(debug=True)