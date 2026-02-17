# File: src\frontend\app.py

"""
Tableau de bord interactif pour la satisfaction client avec prédiction de sentiment et intégration Kibana.
L'utilisateur se connecte via Streamlit pour accéder au modèle de prédiction sécurisé et aux visualisations Kibana.
"""

import os
import time
from typing import Dict
import requests
import streamlit as st
import streamlit.components.v1 as components

# --- Constantes et chemins des fichiers ---
LOGOS_FILES_PATHS: Dict[str, str] = {
    "airflow": os.path.join("src", "frontend", "base64_images", "airflow_logo.txt"),
    "datascientest": os.path.join("src", "frontend", "base64_images", "datascientest_logo.txt"),
    "fastapi": os.path.join("src", "frontend", "base64_images", "fastapi_logo.txt"),
    "github": os.path.join("src", "frontend", "base64_images", "github_logo.txt"),
    "grafana": os.path.join("src", "frontend", "base64_images", "grafana_logo.txt"),
    "kibana": os.path.join("src", "frontend", "base64_images", "kibana_logo.txt"),
}

API_URL: str = "http://fastapi-satisfaction:8000"
# API_URL: str = "http://localhost:8000" # Pour dev en local
AIRFLOW_URL: str = "http://localhost:8081/login"
FASTAPI_URL: str = "http://localhost:8000/docs"
GITHUB_URL: str = "https://github.com/roxfr/nov25_bde_satisfaction_client"
GRAFANA_URL: str = "http://localhost:3000"
KIBANA_BASE_URL: str = (
    "http://localhost:5601/app/dashboards#/view/4e52a31c-5cea-4429-b435-6d36728ad392"
    "?embed=true"
)

# --- Fonction pour lire les logos ---
def lire_base64(fichier_path: str) -> str:
    """Lit un fichier texte contenant du Base64 et retourne le contenu."""
    with open(fichier_path, "r", encoding="utf-8") as f:
        return f.read().strip()

# --- Fonction pour gérer la persistance du token ---
def save_token(token: str) -> None:
    """Sauvegarde le token dans un fichier."""
    with open("jwt_token.txt", "w") as f:
        f.write(token)

def load_token() -> str:
    """Charge le token depuis le fichier."""
    if os.path.exists("jwt_token.txt"):
        with open("jwt_token.txt", "r") as f:
            return f.read().strip()
    return ""

# Chargement de tous les logos en Base64
LOGOS_BASE64: Dict[str, str] = {key: lire_base64(path) for key, path in LOGOS_FILES_PATHS.items()}

# --- Connexion à l'API FastAPI pour obtenir un token JWT ---
def login_admin(username: str, password: str) -> str:
    """Authentifie l'utilisateur auprès de FastAPI pour obtenir un JWT."""
    login_resp = requests.post(
        f"{API_URL}/auth/token",
        data={"username": username, "password": password},
    )
    if login_resp.status_code == 200:
        return login_resp.json().get("access_token")
    return None

# --- Configuration de la page Streamlit ---
st.set_page_config(page_title="Dashboard de Sentiment et Kibana", layout="wide")

# --- Récupérer le token JWT de la session ou du fichier ---
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = load_token()

# Si l'utilisateur n'est pas connecté, on affiche la fenêtre de login
if not st.session_state.jwt_token:
    col1, col2, col3, col4, col5 = st.columns([1,1,2,1,1])
    with col3:
        st.markdown("#### 🛡️ Connexion à Satisfaction Client")

        with st.form(key="login_form"):
            username_input = st.text_input("Nom d'utilisateur :", "")
            password_input = st.text_input("Mot de passe :", type="password")
            login_button = st.form_submit_button("Se connecter")

            if login_button:
                token = login_admin(username_input, password_input)
                if token:
                    st.session_state.jwt_token = token
                    save_token(token)  # Sauvegarder le token dans le fichier
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect")
                
# --- Si l'utilisateur est connecté, afficher le tableau de bord ---
if st.session_state.jwt_token:
    # --- Header ---
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{LOGOS_BASE64['datascientest']}" width="50" />
            <h1 style="display: inline;">NOV25 BDE SATISFACTION CLIENT</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <table style="width: 100%; text-align: left; margin-bottom: 10px;">
            <tr>
                <td style="padding-right: 15px;">
                    <img src="data:image/png;base64,{LOGOS_BASE64['airflow']}" width="20" />
                    <a href="{AIRFLOW_URL}" style="text-decoration: none; color: black;">Apache Airflow — </a>
                    <img src="data:image/png;base64,{LOGOS_BASE64['fastapi']}" width="20" />
                    <a href="{FASTAPI_URL}" style="text-decoration: none; color: black;">FastAPI — </a>
                    <img src="data:image/png;base64,{LOGOS_BASE64['github']}" width="20" />
                    <a href="{GITHUB_URL}" style="text-decoration: none; color: black;">GitHub — </a>
                    <img src="data:image/png;base64,{LOGOS_BASE64['kibana']}" width="20" />
                    <a href="{KIBANA_BASE_URL}" style="text-decoration: none; color: black;">Kibana — </a>
                    <img src="data:image/png;base64,{LOGOS_BASE64['grafana']}" width="20" />
                    <a href="{GRAFANA_URL}" style="text-decoration: none; color: black;">Grafana</a>
                </td>
            </tr>
        </table>
        """,
        unsafe_allow_html=True
    )

    # --- Tableau de bord Kibana ---
    st.subheader("📊 Tableau de bord - Elasticsearch / Kibana")
    if "kibana_ts" not in st.session_state:
        st.session_state.kibana_ts = int(time.time())

    def on_periode_change() -> None:
        """Met à jour le timestamp pour forcer le reload de Kibana."""
        st.session_state.kibana_ts = int(time.time())

    col_select, _ = st.columns([1, 5])
    with col_select:
        periode = st.selectbox(
            "Sélectionner une période :",
            ["7 derniers jours", "14 derniers jours", "1 mois", "3 mois", "6 mois", "1 an"],
            on_change=on_periode_change
        )

    from_to_map: Dict[str, str] = {
        "7 derniers jours": "now-7d",
        "14 derniers jours": "now-14d",
        "1 mois": "now-1M",
        "3 mois": "now-3M",
        "6 mois": "now-6M",
        "1 an": "now-1y"
    }

    from_time = from_to_map[periode]
    kibana_url: str = f"{KIBANA_BASE_URL}&_g=(time:(from:{from_time},to:now))&_ts={st.session_state.kibana_ts}"

    components.iframe(src=kibana_url, height=600, scrolling=True)
    st.markdown("---")

    # --- Prédiction de sentiment sécurisée ---
    st.subheader("🔮 Outil de prédiction de sentiment - Modèle ML")
    col1, col2 = st.columns([1, 1])

    with col1:
        text_input: str = st.text_area("Entrer votre avis ci-dessous (4000 caractères max.) :", "", height=150)

    with col2:
        sentiment: str = ""
        sentiment_color: str = ""
        text_clean: str = text_input.strip()

        if text_clean:
            if len(text_clean) == 1 or (len(text_clean) == 2 and text_clean[0] == text_clean[1]):
                sentiment = "Texte trop court ou répétitif pour prédiction"
                sentiment_color = "gray"
            elif st.session_state.jwt_token:
                headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
                response = requests.post(f"{API_URL}/predict", json={"text": text_input}, headers=headers)
                if response.status_code == 200:
                    sentiment = response.json().get("sentiment", "Erreur lors de la prédiction")
                    sentiment_lower = sentiment.lower()
                    sentiment_color = (
                        "green" if sentiment_lower == "positif"
                        else "red" if sentiment_lower == "négatif"
                        else "gray"
                    )
                else:
                    st.error(f"Erreur {response.status_code}: Impossible de prédire le sentiment")
            else:
                st.warning("Veuillez vous connecter pour utiliser le modèle de prédiction.")

        st.markdown("<u><strong>Sentiment prédit :</strong></u>", unsafe_allow_html=True)
        if sentiment:
            st.markdown(f'<p style="color: {sentiment_color}; font-size: 16px;">{sentiment}</p>', unsafe_allow_html=True)

    if st.button("Envoyer l'avis pour prédiction") and not text_input:
        st.warning("Veuillez entrer un avis avant de soumettre.")

    # --- Footer ---
    st.markdown(
        """
        <footer style="text-align: center; font-size: 12px; color: gray; margin-top: 20px;">
            &copy; 2026 Liora (ex-DataScientest). Tous droits réservés.
        </footer>
        """,
        unsafe_allow_html=True
    )
