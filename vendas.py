import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid
import calendar
import hashlib
import hmac


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Controle de Vendas - Colina Bike Center",
    page_icon="🚲",
    layout="wide"
)


# ============================================================
# SISTEMA DE LOGIN
# ============================================================

# Credenciais padrão.
# Para alterar, basta modificar estas duas linhas.
USUARIO_LOGIN = "Colina"
SENHA_LOGIN = "Colina@2026"

def gerar_hash_senha(senha):
    """Gera um hash SHA-256 para comparar a senha com segurança."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def autenticar_usuario():
    """Exibe a tela de login e libera o sistema somente após autenticação."""

    # Se já estiver autenticado, não mostra novamente o formulário.
    if st.session_state.get("autenticado", False):
        return True

    st.markdown(
        """
        <style>
        .login-box {
            max-width: 480px;
            margin: 70px auto 0 auto;
            padding: 35px;
            border-radius: 15px;
            border: 1px solid rgba(128,128,128,0.25);
            box-shadow: 0 8px 30px rgba(0,0,0,0.10);
        }
        .login-title {
            text-align: center;
            font-size: 30px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .login-subtitle {
            text-align: center;
            color: #777;
            margin-bottom: 25px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown(
        '<div class="login-title">🚲 Colina Bike Center</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Controle de Vendas</div>',
        unsafe_allow_html=True
    )

    with st.form("form_login"):
        usuario = st.text_input(
            "👤 Usuário",
            placeholder="Digite seu usuário"
        )

        senha = st.text_input(
            "🔒 Senha",
            type="password",
            placeholder="Digite sua senha"
        )

        entrar = st.form_submit_button(
            "🔐 ENTRAR",
            use_container_width=True,
            type="primary"
        )

    if entrar:
        senha_hash_digitada = gerar_hash_senha(senha)
        senha_hash_correta = gerar_hash_senha(SENHA_LOGIN)

        usuario_ok = hmac.compare_digest(
            usuario.strip(),
            USUARIO_LOGIN
        )

        senha_ok = hmac.compare_digest(
            senha_hash_digitada,
            senha_hash_correta
        )

        if usuario_ok and senha_ok:
            st.session_state.autenticado = True
            st.session_state.usuario_logado = usuario.strip()
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")

    st.markdown(
        """
        <div style="text-align:center; margin-top:20px; color:#888;">
            🔒 Acesso restrito ao sistema interno
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    return False


# ============================================================
# BLOQUEIO DE ACESSO
# ============================================================

if not autenticar_usuario():
    st.stop()


# ============================================================
# CONTROLE DE SESSÃO
# ============================================================

# Mostra o usuário logado e botão para sair no menu lateral.
with st.sidebar:
    st.markdown("### 🔐 Sessão")
    st.success(
        f"Usuário: **{st.session_state.get('usuario_logado', USUARIO_LOGIN)}**"
    )

    if st.button(
        "🚪 SAIR DO SISTEMA",
        use_container_width=True
    ):
        st.session_state.autenticado = False
        st.session_state.pop("usuario_logado", None)
        st.rerun()


# ============================================================
# TÍTULO
# ============================================================

st.title("🚲 Controle de Vendas - Colina Bike Center")

st.caption(
    "Controle interno de vendas — Colina | J&M | Golembiewski"
)


# ============================================================
# ARQUIVO DE DADOS
# ============================================================

ARQUIVO_DADOS = "vendas.csv"


# ============================================================
# OPÇÕES
# ============================================================

VENDEDORES = [
    "Murilo",
    "Douglas",
    "Patricia",
    "Fran",
    "Wilson",
    "Reus",
    "Caio",
    "Jonathan"
]

EMPRESAS = [
    "Colina",
    "J&M",
    "Golembiewski"
]

FORMAS_PAGAMENTO = [
    "Dinheiro",
    "Cartão de Crédito",
    "Cartão de Débito",
    "PIX",
    "Boleto"
]

COLUNAS = [
    "ID",
    "Data",
    "Empresa",
    "Vendedor",
    "Produto",
    "Valor",
    "Forma de Pagamento"
]


# ============================================================
# FUNÇÃO: CARREGAR DADOS
# ============================================================

def carregar_dados():

    if not os.path.exists(ARQUIVO_DADOS):

        return pd.DataFrame(columns=COLUNAS)

    try:

        df = pd.read_csv(
            ARQUIVO_DADOS,
            encoding="utf-8-sig"
        )

        # ----------------------------------------------------
        # Compatibilidade com versão antiga
        # ----------------------------------------------------

        if "ID" not in df.columns:

            df.insert(
                0,
                "ID",
                [
                    str(uuid.uuid4())
                    for _ in range(len(df))
                ]
            )

        # ----------------------------------------------------
        # Garantir todas as colunas
        # ----------------------------------------------------

        for coluna in COLUNAS:

            if coluna not in df.columns:

                df[coluna] = ""

        # ----------------------------------------------------
        # Organizar colunas
        # ----------------------------------------------------

        df = df[COLUNAS]

        # ----------------------------------------------------
        # Valor numérico
        # ----------------------------------------------------

        df["Valor"] = pd.to_numeric(
            df["Valor"],
            errors="coerce"
        ).fillna(0.0)

        # ----------------------------------------------------
        # Data
        # ----------------------------------------------------

        df["Data"] = pd.to_datetime(
            df["Data"],
            errors="coerce"
        )

        # ----------------------------------------------------
        # Empresa
        # ----------------------------------------------------

        df["Empresa"] = df["Empresa"].astype(str)

        return df

    except Exception as erro:

        st.error(
            f"Erro ao carregar o histórico: {erro}"
        )

        return pd.DataFrame(columns=COLUNAS)


# ============================================================
# FUNÇÃO: SALVAR DATAFRAME
# ============================================================

def salvar_dataframe(df):

    # Garantir que a pasta exista
    pasta = os.path.dirname(ARQUIVO_DADOS)

    if pasta:

        os.makedirs(
            pasta,
            exist_ok=True
        )

    df.to_csv(
        ARQUIVO_DADOS,
        index=False,
        encoding="utf-8-sig"
    )


# ============================================================
# FUNÇÃO: SALVAR VENDA
# ============================================================

def salvar_registro(
    data,
    empresa,
    vendedor,
    produto,
    valor,
    forma_pagamento
):

    df = carregar_dados()

    novo_registro = {

        "ID": str(uuid.uuid4()),

        "Data": pd.Timestamp(data),

        "Empresa": empresa,

        "Vendedor": vendedor,

        "Produto": produto.strip(),

        "Valor": float(valor),

        "Forma de Pagamento": forma_pagamento
    }

    novo_df = pd.DataFrame(
        [novo_registro]
    )

    df = pd.concat(
        [
            df,
            novo_df
        ],
        ignore_index=True
    )

    salvar_dataframe(df)


# ============================================================
# FUNÇÃO: NOME DO MÊS
# ============================================================

def nome_mes(numero_mes):

    meses = {

        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    return meses[numero_mes]


# ============================================================
# FUNÇÃO: NOME DO MÊS/ANO
# ============================================================

def nome_mes_ano(data):

    return (
        f"{nome_mes(data.month)}/{data.year}"
    )


# ============================================================
# FUNÇÃO: CHAVE DO MÊS
# ============================================================

def chave_mes(data):

    return (
        f"{data.year:04d}-{data.month:02d}"
    )


# ============================================================
# CARREGAR HISTÓRICO
# ============================================================

df_vendas = carregar_dados()


# ============================================================
# AVISO DE FECHAMENTO MENSAL
# ============================================================

hoje = datetime.now()

if hoje.day == 1:

    if not df_vendas.empty:

        mes_anterior = hoje.month - 1
        ano_anterior = hoje.year

        if mes_anterior == 0:

            mes_anterior = 12
            ano_anterior -= 1

        chave_mes_anterior = (
            f"{ano_anterior:04d}-{mes_anterior:02d}"
        )

        df_mes_anterior = df_vendas[
            df_vendas["Data"].dt.strftime("%Y-%m")
            == chave_mes_anterior
        ].copy()

        if not df_mes_anterior.empty:

            st.warning(
                "🔔 FECHAMENTO MENSAL"
            )

            st.info(
                f"Hoje é dia 1º. "
                f"Não esqueça de baixar o relatório "
                f"de {nome_mes(mes_anterior)}/{ano_anterior}."
            )

            col1, col2, col3 = st.columns(3)

            for coluna, empresa in zip(
                [col1, col2, col3],
                EMPRESAS
            ):

                total = df_mes_anterior[
                    df_mes_anterior["Empresa"] == empresa
                ]["Valor"].sum()

                with coluna:

                    st.metric(
                        f"🏢 {empresa}",
                        f"R$ {total:,.2f}"
                    )

            # ------------------------------------------------
            # DOWNLOAD DO MÊS ANTERIOR
            # ------------------------------------------------

            relatorio_mes = (
                df_mes_anterior
                .drop(columns=["ID"], errors="ignore")
                .copy()
            )

            relatorio_mes["Data"] = (
                relatorio_mes["Data"]
                .dt.strftime("%d/%m/%Y")
            )

            csv_mes = (
                relatorio_mes
                .to_csv(index=False)
                .encode("utf-8-sig")
            )

            nome_arquivo = (
                f"vendas_"
                f"{ano_anterior}_"
                f"{mes_anterior:02d}.csv"
            )

            st.download_button(
                label=(
                    f"📥 BAIXAR RELATÓRIO "
                    f"{nome_mes(mes_anterior).upper()}/"
                    f"{ano_anterior}"
                ),
                data=csv_mes,
                file_name=nome_arquivo,
                mime="text/csv",
                use_container_width=True
            )


# ============================================================
# NOVA VENDA
# ============================================================

st.divider()

st.header("➕ Nova Venda")


with st.form(
    key="form_venda",
    clear_on_submit=True
):

    col1, col2 = st.columns(2)

    with col1:

        data_venda = st.date_input(
            "📅 Data",
            value=datetime.now()
        )

        empresa = st.selectbox(
            "🏢 Empresa",
            EMPRESAS
        )

        vendedor = st.selectbox(
            "👤 Vendedor",
            VENDEDORES
        )

    with col2:

        produto = st.text_input(
            "🛒 Descrição do Produto",
            placeholder=(
                "Ex: Bicicleta, capacete, revisão..."
            )
        )

        valor = st.number_input(
            "💰 Valor (R$)",
            min_value=0.0,
            step=0.01,
            format="%.2f"
        )

        forma_pagamento = st.selectbox(
            "💳 Forma de Pagamento",
            FORMAS_PAGAMENTO
        )

    salvar = st.form_submit_button(
        "💾 SALVAR VENDA",
        use_container_width=True
    )


# ============================================================
# SALVAR NOVA VENDA
# ============================================================

if salvar:

    if not produto.strip():

        st.error(
            "❌ Digite a descrição do produto."
        )

    elif valor <= 0:

        st.error(
            "❌ Digite um valor maior que R$ 0,00."
        )

    else:

        salvar_registro(
            data=data_venda,
            empresa=empresa,
            vendedor=vendedor,
            produto=produto,
            valor=valor,
            forma_pagamento=forma_pagamento
        )

        st.success(
            f"✅ Venda registrada para {empresa}!"
        )

        st.rerun()


# ============================================================
# ATUALIZAR DADOS
# ============================================================

df_vendas = carregar_dados()


# ============================================================
# HISTÓRICO
# ============================================================

st.divider()

st.header("📊 Histórico de Vendas")


if df_vendas.empty:

    st.info(
        "Nenhuma venda registrada até o momento."
    )

else:

    # ========================================================
    # RESUMO GERAL DAS EMPRESAS
    # ========================================================

    st.subheader("🏢 Resumo Geral")

    col1, col2, col3 = st.columns(3)

    for coluna, empresa in zip(
        [col1, col2, col3],
        EMPRESAS
    ):

        vendas_empresa = df_vendas[
            df_vendas["Empresa"] == empresa
        ]

        total = vendas_empresa["Valor"].sum()

        quantidade = len(vendas_empresa)

        with coluna:

            st.metric(
                f"🏢 {empresa}",
                f"R$ {total:,.2f}"
            )

            st.caption(
                f"{quantidade} venda(s)"
            )


    # ========================================================
    # CRIAR LISTA DE MESES EXISTENTES
    # ========================================================

    df_vendas["Mes"] = (
        df_vendas["Data"]
        .dt.strftime("%Y-%m")
    )

    meses_existentes = sorted(
        df_vendas["Mes"]
        .dropna()
        .unique(),
        reverse=True
    )


    # ========================================================
    # ABAS DOS MESES
    # ========================================================

    st.divider()

    st.subheader("📅 Histórico Mensal")

    nomes_abas = []

    for mes in meses_existentes:

        ano = int(mes[:4])
        numero_mes = int(mes[5:7])

        nomes_abas.append(
            f"{nome_mes(numero_mes)}/{ano}"
        )


    abas = st.tabs(nomes_abas)


    # ========================================================
    # PROCESSAR CADA MÊS
    # ========================================================

    for aba, mes, nome_aba in zip(
        abas,
        meses_existentes,
        nomes_abas
    ):

        with aba:

            ano = int(mes[:4])
            numero_mes = int(mes[5:7])

            df_mes = df_vendas[
                df_vendas["Mes"] == mes
            ].copy()


            # =================================================
            # TÍTULO DO MÊS
            # =================================================

            st.subheader(
                f"📅 {nome_aba}"
            )


            # =================================================
            # RESUMO DAS EMPRESAS NO MÊS
            # =================================================

            col1, col2, col3 = st.columns(3)

            for coluna, empresa in zip(
                [col1, col2, col3],
                EMPRESAS
            ):

                df_empresa = df_mes[
                    df_mes["Empresa"] == empresa
                ]

                total = df_empresa["Valor"].sum()

                quantidade = len(df_empresa)

                with coluna:

                    st.metric(
                        f"🏢 {empresa}",
                        f"R$ {total:,.2f}"
                    )

                    st.caption(
                        f"{quantidade} venda(s)"
                    )


            # =================================================
            # TOTAL DO MÊS
            # =================================================

            total_mes = df_mes["Valor"].sum()

            quantidade_mes = len(df_mes)

            ticket_medio = (
                total_mes / quantidade_mes
                if quantidade_mes > 0
                else 0
            )

            st.divider()

            m1, m2, m3 = st.columns(3)

            m1.metric(
                "💰 Total do Mês",
                f"R$ {total_mes:,.2f}"
            )

            m2.metric(
                "🧾 Vendas",
                quantidade_mes
            )

            m3.metric(
                "📈 Ticket Médio",
                f"R$ {ticket_medio:,.2f}"
            )


            # =================================================
            # FILTRO DE EMPRESA
            # =================================================

            filtro_empresa = st.selectbox(
                "🔎 Filtrar Empresa",
                ["Todas"] + EMPRESAS,
                key=f"empresa_{mes}"
            )


            if filtro_empresa == "Todas":

                df_exibicao = df_mes.copy()

            else:

                df_exibicao = df_mes[
                    df_mes["Empresa"] == filtro_empresa
                ].copy()


            # =================================================
            # HISTÓRICO DO MÊS
            # =================================================

            st.subheader(
                "📋 Registros"
            )


            if df_exibicao.empty:

                st.info(
                    "Nenhuma venda encontrada para "
                    "este filtro."
                )

            else:

                # ---------------------------------------------
                # Criar tabela de exibição
                # ---------------------------------------------

                df_tabela = df_exibicao.copy()

                df_tabela["Excluir"] = False

                df_tabela["Data"] = (
                    df_tabela["Data"]
                    .dt.strftime("%d/%m/%Y")
                )

                df_tabela = df_tabela[
                    [
                        "Excluir",
                        "Data",
                        "Empresa",
                        "Vendedor",
                        "Produto",
                        "Valor",
                        "Forma de Pagamento"
                    ]
                ]


                # ---------------------------------------------
                # Editor
                # ---------------------------------------------

                df_editado = st.data_editor(

                    df_tabela,

                    column_config={

                        "Excluir":
                            st.column_config.CheckboxColumn(
                                "🗑️ Excluir?",
                                help=(
                                    "Marque a venda que deseja "
                                    "excluir."
                                ),
                                default=False
                            ),

                        "Data":
                            st.column_config.TextColumn(
                                "Data"
                            ),

                        "Empresa":
                            st.column_config.TextColumn(
                                "Empresa"
                            ),

                        "Vendedor":
                            st.column_config.TextColumn(
                                "Vendedor"
                            ),

                        "Produto":
                            st.column_config.TextColumn(
                                "Produto"
                            ),

                        "Valor":
                            st.column_config.NumberColumn(
                                "Valor (R$)",
                                format="R$ %.2f"
                            ),

                        "Forma de Pagamento":
                            st.column_config.TextColumn(
                                "Pagamento"
                            )
                    },

                    disabled=[
                        "Data",
                        "Empresa",
                        "Vendedor",
                        "Produto",
                        "Valor",
                        "Forma de Pagamento"
                    ],

                    hide_index=True,

                    use_container_width=True
                )


                # =================================================
                # EXCLUSÃO
                # =================================================

                linhas_excluir = df_editado[
                    df_editado["Excluir"] == True
                ]


                if not linhas_excluir.empty:

                    st.warning(
                        f"⚠️ "
                        f"{len(linhas_excluir)} "
                        f"registro(s) selecionado(s)."
                    )


                    confirmar = st.checkbox(
                        "⚠️ Confirmo que desejo excluir os registros selecionados.",
                        key=f"confirmar_{mes}"
                    )


                    if confirmar:

                        if st.button(
                            "🗑️ EXCLUIR REGISTROS SELECIONADOS",
                            type="primary",
                            use_container_width=True,
                            key=f"excluir_{mes}"
                        ):

                            # ---------------------------------
                            # Recuperar índices
                            # ---------------------------------

                            indices = (
                                linhas_excluir.index
                            )


                            # ---------------------------------
                            # IDs reais
                            # ---------------------------------

                            ids_excluir = (
                                df_exibicao
                                .loc[
                                    indices,
                                    "ID"
                                ]
                                .tolist()
                            )


                            # ---------------------------------
                            # Remover pelo ID
                            # ---------------------------------

                            df_atualizado = df_vendas[
                                ~df_vendas["ID"].isin(
                                    ids_excluir
                                )
                            ].copy()


                            # ---------------------------------
                            # Remover coluna auxiliar
                            # ---------------------------------

                            df_atualizado = (
                                df_atualizado
                                .drop(
                                    columns=["Mes"],
                                    errors="ignore"
                                )
                            )


                            # ---------------------------------
                            # Salvar
                            # ---------------------------------

                            salvar_dataframe(
                                df_atualizado
                            )


                            st.success(
                                f"✅ "
                                f"{len(ids_excluir)} "
                                f"registro(s) excluído(s)."
                            )

                            st.rerun()


            # =================================================
            # DOWNLOAD DO MÊS
            # =================================================

            st.divider()

            st.subheader(
                "📥 Exportar este mês"
            )


            # ---------------------------------------------
            # Relatório completo
            # ---------------------------------------------

            relatorio_mes = (
                df_mes
                .drop(
                    columns=["ID", "Mes"],
                    errors="ignore"
                )
                .copy()
            )

            relatorio_mes["Data"] = (
                relatorio_mes["Data"]
                .dt.strftime("%d/%m/%Y")
            )

            csv_mes = (
                relatorio_mes
                .to_csv(index=False)
                .encode("utf-8-sig")
            )


            nome_arquivo_mes = (
                f"vendas_"
                f"{ano}_"
                f"{numero_mes:02d}.csv"
            )


            st.download_button(

                label=(
                    f"📥 Baixar "
                    f"{nome_aba} - Todas as Empresas"
                ),

                data=csv_mes,

                file_name=nome_arquivo_mes,

                mime="text/csv",

                use_container_width=True,

                key=f"download_todas_{mes}"
            )


            # =================================================
            # DOWNLOAD INDIVIDUAL POR EMPRESA
            # =================================================

            st.write(
                "**Relatórios individuais por empresa:**"
            )


            col1, col2, col3 = st.columns(3)


            for coluna, empresa in zip(
                [col1, col2, col3],
                EMPRESAS
            ):

                df_empresa_download = df_mes[
                    df_mes["Empresa"] == empresa
                ].copy()


                if not df_empresa_download.empty:

                    df_empresa_download = (
                        df_empresa_download
                        .drop(
                            columns=["ID", "Mes"],
                            errors="ignore"
                        )
                    )

                    df_empresa_download["Data"] = (
                        df_empresa_download["Data"]
                        .dt.strftime("%d/%m/%Y")
                    )


                    csv_empresa = (
                        df_empresa_download
                        .to_csv(index=False)
                        .encode("utf-8-sig")
                    )


                    nome_empresa_arquivo = (
                        empresa
                        .lower()
                        .replace("&", "e")
                        .replace(" ", "_")
                    )


                    with coluna:

                        st.download_button(

                            label=(
                                f"📥 {empresa}"
                            ),

                            data=csv_empresa,

                            file_name=(
                                f"vendas_"
                                f"{nome_empresa_arquivo}_"
                                f"{ano}_"
                                f"{numero_mes:02d}.csv"
                            ),

                            mime="text/csv",

                            use_container_width=True,

                            key=(
                                f"download_"
                                f"{empresa}_"
                                f"{mes}"
                            )
                        )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Controle de Vendas — Colina Bike Center"
)

st.caption(
    "Os dados são armazenados localmente no arquivo vendas.csv."
)