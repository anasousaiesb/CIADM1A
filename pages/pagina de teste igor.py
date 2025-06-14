import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap
import matplotlib.ticker as mticker # Import for more refined tick formatting

# --- CONFIGURAÇÕES DA PÁGINA ---
# THIS IS THE CORRECT AND ONLY st.set_page_config CALL
st.set_page_config(
    layout="wide",
    page_title="Clima Brasil: Análise Interativa (2020-2025) 🇧🇷", # Keep 2020-2025 as it's the data range
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.streamlit.io/help', # Replace with actual help link
        'Report a bug': "https://www.streamlit.io/bug-report", # Replace with actual bug report link
        'About': "# Este é um aplicativo interativo de análise climática do Brasil."
    }
)

# --- CUSTOM CSS (Melhorias Visuais) ---
st.markdown("""
<style>
    /* Fundo da Sidebar e Main Content */
    .stApp {
        background-color: #f0f2f6; /* Light gray background for the entire app */
    }
    .stSidebar {
        background-color: #e0f7fa; /* Light cyan for sidebar */
        border-right: 1px solid #b2ebf2;
    }

    /* Títulos e Textos */
    /* NEW STYLE FOR MAIN TITLE (h1) to match image */
    h1 {
        color: #212121; /* Very dark gray, almost black */
        text-align: center;
        font-size: 3.2em; /* Slightly smaller than before but still very large */
        font-weight: 800; /* Extra bold */
        margin-bottom: 5px; /* Reduce space after main title to bring emojis closer */
        line-height: 1.2; /* Adjust line height for multi-line titles */
    }

    /* Emojis style below h1 */
    .emoji-title {
        font-size: 2.5em; /* Large emoji size */
        text-align: center;
        margin-top: 5px; /* Space above emojis */
        margin-bottom: 20px; /* Space below emojis before intro text */
    }


    .big-font {
        font-size:24px !important;
        font-weight: bold;
        color: #00796b; /* Dark Teal */
        text-align: center;
        margin-bottom: 15px;
    }
    .medium-font {
        font-size:18px !important;
        color: #004d40; /* Even darker Teal */
        text-align: center;
        margin-bottom: 25px;
    }

    h2 {
        color: #37474f; /* Slightly lighter dark title */
        font-size: 2.2em;
        border-bottom: 2px solid #b0bec5;
        padding-bottom: 10px;
        margin-top: 40px;
        margin-bottom: 25px;
    }
    h3 {
        color: #455a64;
        font-size: 1.8em;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    /* Mensagens de Alerta e Info */
    .st.Alert {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .st.Alert p {
        font-size: 1.1em;
    }

    /* Blocos de Insights (melhora nos estilos já existentes) */
    div[data-testid="stMarkdownContainer"] div {
        line-height: 1.6;
    }
    ul {
        list-style-type: '👉 '; /* Custom bullet point */
        padding-left: 20px;
    }
    li {
        margin-bottom: 8px;
    }

    /* Botões e Selectboxes na Sidebar */
    .stSelectbox>label, .stMultiSelect>label {
        font-size: 1.1em;
        font-weight: bold;
        color: #004d40;
    }
    .stSelectbox div, .stMultiSelect div {
        border-radius: 8px;
        border: 1px solid #00796b;
    }
    .stSelectbox div:hover, .stMultiSelect div:hover {
        border-color: #004d40;
    }

    /* Rodapé */
    .footer {
        font-size: 0.9em;
        color: #78909c;
        text-align: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #cfd8dc;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES INICIAIS ---
# REMOVE THIS LINE: st.set_page_config(layout="wide", page_title="Análise Climática Interativa por Região ☀️")

# CSS para estilização aprimorada do título
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fa; /* Fundo suave para o aplicativo */
}
.main-title {
    font-size: 3.5em;
    font-weight: 700;
    color: #2E8B57; /* Um verde mais escuro e atraente */
    text-align: center;
    margin-bottom: 0.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle {
    font-size: 1.8em;
    color: #3CB371; /* Um verde um pouco mais claro */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 1.5em;
}
.header-section {
    background-color: #e6f7ee; /* Fundo levemente verde para a seção de cabeçalho */
    padding: 1.5em;
    border-radius: 10px;
    margin-bottom: 2em;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)
