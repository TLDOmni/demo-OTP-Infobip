import streamlit as st
import requests

# Configuração da página
st.set_page_config(page_title="Validação 2FA Infobip", page_icon="📱")

# Buscando as chaves de acesso (Secrets)
BASE_URL = st.secrets["INFOBIP_BASE_URL"]
API_KEY = st.secrets["INFOBIP_API_KEY"]
APP_ID = st.secrets["INFOBIP_APP_ID"]
MSG_ID = st.secrets["INFOBIP_MSG_ID"]

headers = {
    "Authorization": f"App {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

st.title("📱 Envio e Validação de OTP via SMS")
st.markdown("Desenvolvido com Infobip e Streamlit")

# Controle de estado para salvar o ID do PIN gerado
if "pin_id" not in st.session_state:
    st.session_state.pin_id = None

st.divider()

# --- ETAPA 1: ENVIO DO CÓDIGO ---
st.subheader("1. Enviar Código")
phone_number = st.text_input("Digite o número do celular com DDI e DDD (Ex: 5511999999999):")

if st.button("Enviar OTP", type="primary"):
    if phone_number:
        url = f"{BASE_URL}/2fa/2/pin"
        payload = {
            "applicationId": APP_ID,
            "messageId": MSG_ID,
            "from": "InfoApp",
            "to": phone_number
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            # Salva o pinId para usar na validação
            st.session_state.pin_id = response.json().get("pinId")
            st.success("✅ Código enviado com sucesso! Verifique seu celular.")
        else:
            st.error(f"❌ Erro ao enviar: {response.text}")
    else:
        st.warning("Por favor, insira um número de telefone.")

# --- ETAPA 2: VALIDAÇÃO DO CÓDIGO ---
if st.session_state.pin_id:
    st.divider()
    st.subheader("2. Validar Código")
    pin_code = st.text_input("Digite o código PIN recebido via SMS:")
    
    if st.button("Validar OTP", type="secondary"):
        if pin_code:
            url_verify = f"{BASE_URL}/2fa/2/pin/{st.session_state.pin_id}/verify"
            payload_verify = {"pin": pin_code}
            
            response_verify = requests.post(url_verify, json=payload_verify, headers=headers)
            
            if response_verify.status_code == 200:
                result = response_verify.json()
                if result.get("verified"):
                    st.success("🎉 Código validado com sucesso! Autenticação concluída.")
                    # Limpa o estado após o sucesso
                    st.session_state.pin_id = None
                else:
                    st.error("❌ Código incorreto.")
            else:
                st.error(f"❌ Erro na validação: {response_verify.text}")
        else:
            st.warning("Por favor, insira o código PIN.")
