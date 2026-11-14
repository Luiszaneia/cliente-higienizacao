import os
import base64
import urllib.parse
import streamlit as st

# Configuração da página otimizada para celular
st.set_page_config(
    page_title="LR Higienização - Simulador de Orçamento",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CONFIGURAÇÕES DA EMPRESA
# ==========================================
WHATSAPP_EMPRESA = "5516992218198"  # Número atualizado conforme a logo
ARQUIVO_LOGO = "logo_lr.png"        # Arquivo PNG com fundo branco

TABELA_SERVICOS = {
    "Sofá 2 Lugares (Padrão)": 140.00,
    "Sofá 3 Lugares (Padrão)": 180.00,
    "Sofá Retrátil / Reclinável (2 a 3 lugares)": 230.00,
    "Sofá de Canto / em L (até 5 lugares)": 280.00,
    "Colchão de Solteiro": 110.00,
    "Colchão de Casal Padrão": 150.00,
    "Colchão Queen / King": 190.00,
    "Poltrona Simples / Amamentação": 80.00,
    "Cadeira de Jantar (Assento + Encosto)": 35.00,
    "Higienização Interna de Veículo (Bancos)": 200.00,
}

NIVEL_SUJIDADE = {
    "🟢 Manutenção / Uso Normal (poeira e suor do dia a dia)": 1.10,
    "🟡 Sujidade Moderada (manchas leves de líquidos ou alimentos)": 1.20,
    "🔴 Sujidade Pesada (manchas antigas, mofo, odor ou urina pet)": 1.40,
}

TIPOS_TECIDO = [
    "Suede", 
    "Linho", 
    "Veludo", 
    "Bouclé", 
    "Colchão", 
    "Sarja / Algodão", 
    "Couro / Sintético", 
    "Outro / Não sei"
]

TIPOS_MANCHAS = [
    "Nenhuma / Apenas sujeira normal",
    "Café ou Refrigerante",
    "Vinho",
    "Gorduras / Molhos / Comida",
    "Tinta de Caneta / Canetinha",
    "Odores / Urina / Fluidos corporais",
    "Mofo / Umidade"
]

# EDITE AQUI AS CIDADES QUE VOCÊ ATENDE:
CIDADES_ATENDIDAS = [
    "Luiz Antônio - SP",
    "Guatapará - SP",
    "Santa Rita do Passa Quatro - SP",
    "São Simão - SP",
    "Ribeirão Preto - SP",
    "Outra cidade da região"
]

if "carrinho_cliente" not in st.session_state:
    st.session_state.carrinho_cliente = []

def carregar_imagem_base64(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# ==========================================
# ESTILIZAÇÃO MODERNA (FUNDO BRANCO E LIMPO)
# ==========================================
st.markdown("""
    <style>
    .logo-container {
        text-align: center;
        padding: 10px 0 15px 0;
    }
    .logo-container img {
        max-width: 340px;
        width: 90%;
        height: auto;
    }
    div.stButton > button[kind="primary"], a[kind="primary"] {
        background-color: #165B99 !important;
        border-color: #165B99 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
    }
    div.stButton > button[kind="primary"]:hover, a[kind="primary"]:hover {
        background-color: #0F4373 !important;
        border-color: #0F4373 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CABEÇALHO COM A LOGO EM PNG (FUNDO BRANCO)
# ==========================================
logo_b64 = carregar_imagem_base64(ARQUIVO_LOGO)

if logo_b64:
    st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_b64}" alt="LR Higienização">
        </div>
    """, unsafe_allow_html=True)
else:
    st.title("🛋️ LR Higienização")

st.info("✨ **Atendimento profissional a domicílio** com extração profunda e produtos bactericidas seguros para sua família e pets.")

st.markdown("---")

# ==========================================
# PASSO 1: DETALHES DA PEÇA
# ==========================================
st.subheader("1. Detalhes da Peça")

item_escolhido = st.selectbox("Escolha a peça:", list(TABELA_SERVICOS.keys()))

col_qtd, col_estado = st.columns([1, 2])
with col_qtd:
    qtd = st.number_input("Quantidade / m²:", min_value=1, max_value=30, value=1)
with col_estado:
    estado_peca = st.selectbox("Nível geral de sujidade:", list(NIVEL_SUJIDADE.keys()))

col_tec, col_man = st.columns(2)
with col_tec:
    tecido_escolhido = st.selectbox("Tipo de Tecido:", TIPOS_TECIDO)
with col_man:
    mancha_especifica = st.selectbox("Mancha ou odor específico?", TIPOS_MANCHAS)

historico_limpeza = st.radio("Já foi feita higienização anteriormente?", ["Não", "Sim"], horizontal=True)

valor_base = TABELA_SERVICOS[item_escolhido]
fator = NIVEL_SUJIDADE[estado_peca]
valor_unitario = valor_base * fator
subtotal = valor_unitario * qtd

st.markdown("")
st.caption(f"Valor estimado para este item: **R$ {subtotal:.2f}** *(R$ {valor_unitario:.2f} cada)*")

if st.button("➕ Adicionar Item à Simulação", use_container_width=True, type="primary"):
    st.session_state.carrinho_cliente.append({
        "peca": item_escolhido,
        "qtd": qtd,
        "estado": estado_peca.split(" (")[0],
        "tecido": tecido_escolhido,
        "mancha": mancha_especifica,
        "historico": historico_limpeza,
        "subtotal": subtotal
    })
    st.success(f"{qtd}x {item_escolhido} adicionado!")

# ==========================================
# PASSO 2: RESUMO DA SIMULAÇÃO
# ==========================================
if st.session_state.carrinho_cliente:
    st.markdown("---")
    st.subheader("2. Resumo da Simulação")

    valor_total_estimado = 0
    for idx, item in enumerate(st.session_state.carrinho_cliente):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{item['qtd']}x {item['peca']}**")
                st.caption(f"Tecido: {item['tecido']} | Mancha: {item['mancha']} | Limpo antes: {item['historico']}")
                st.markdown(f"Subtotal: **R$ {item['subtotal']:.2f}**")
            with c2:
                if st.button("🗑️", key=f"rem_{idx}", help="Remover item"):
                    st.session_state.carrinho_cliente.pop(idx)
                    st.rerun()
        valor_total_estimado += item["subtotal"]

    st.markdown("---")
    
    st.metric(label="💰 VALOR TOTAL ESTIMADO", value=f"R$ {valor_total_estimado:.2f}")
    
    st.warning("⚠️ **Atenção:** Este valor é uma **estimativa inicial** baseada nas informações fornecidas. O orçamento exato e definitivo será confirmado após o envio das fotos do estofado no WhatsApp.")

    st.markdown("---")

    # ==========================================
    # PASSO 3: LOCALIZAÇÃO E ENVIO NO WHATSAPP
    # ==========================================
    st.subheader("3. Local do Atendimento")
    
    cidade = st.selectbox("Selecione sua Cidade:", CIDADES_ATENDIDAS)

    lista_itens_msg = ""
    for item in st.session_state.carrinho_cliente:
        lista_itens_msg += f"▪ {item['qtd']}x {item['peca']}\n  - Tecido: {item['tecido']} | Mancha: {item['mancha']} | Já lavado antes: {item['historico']}\n  - Subtotal: R$ {item['subtotal']:.2f}\n\n"

    mensagem_pronta = f"""Olá! Fiz uma simulação no site da *LR Higienização*:

*Cidade:* {cidade}

*ITENS SELECIONADOS:*
{lista_itens_msg}*VALOR ESTIMADO:* R$ {valor_total_estimado:.2f}

*(Vou enviar as fotos do estofado aqui no chat para a análise e a confirmação do orçamento)*"""

    texto_codificado = urllib.parse.quote(mensagem_pronta)
    link_whatsapp = f"https://wa.me/{WHATSAPP_EMPRESA}?text={texto_codificado}"

    st.markdown("---")
    
    st.link_button(
        label="📲 Enviar Simulação para o WhatsApp",
        url=link_whatsapp,
        type="primary",
        use_container_width=True
    )

    st.info("💡 **Dica:** Ao clicar no botão acima, o WhatsApp abrirá com o texto pronto. **Basta anexar a foto do estofado na conversa** para agilizarmos a confirmação!")

    if st.button("🧹 Limpar Tudo / Nova Simulação", use_container_width=True):
        st.session_state.carrinho_cliente = []
        st.rerun()

else:
    st.markdown("---")
    st.caption("👆 Selecione as opções acima e clique em **Adicionar Item à Simulação** para começar.")
    
# --- RODAPÉ DISCRETO ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 0.8rem;'>© 2026 LR Higienização • Todos os direitos reservados</p>", 
    unsafe_allow_html=True
)
