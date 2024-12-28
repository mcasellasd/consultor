import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import openai
from dotenv import load_dotenv
import os

# Carregar variables d'entorn i la clau API
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Dades dels fons
data = {
    "ISIN": [
        "LU0034353002", "LU0113257694", "LU0599946893", "LU0218171717", "IE00B4468526", 
        "LU1769942233", "LU0203975437", "LU0171307068", "LU0232524495", "LU1295551144",
        "ES0174013021", "IE00B3K83P04", "IE00B03HCZ61", "IE0031786142", "LU0072462426", 
        "LU0599946893", "S/N"
    ],
    "Nom del Fons": [
        "DWS FLOAT RATE NOTES", "SISF EUR CORPORATE BOND", "DWS CONCEPT KALDEMORGEN",
        "JPM US SELECT EQ A EUR", "POLAR CAPITAL GLOBAL TECHNOLOGY R EUR", 
        "DWS INVEST CROCI JAPAN", "ROBECO GLOBAL PREMIUM", "BGF WORLD HEALTHSCIENCE FUND A2 EUR",
        "AB - AMERICAN GROWTH PORTFOLIO A EUR ACC", "CAPITAL GROUP NEW PERSPECTIVE FUND (LUX) B EUR",
        "CREAND RTA. FIXA MIXTA", "POLAR CAP-HEALTH", "VANG, GLOB, STK", 
        "VANG-EMRG IND", "BLACKROCK GLOBAL FUND", "DWS CONCEPT KALDEMORGEN", "S/N"
    ],
    "pes cartera": [
        5.83, 4.11, 22.62, 3.97, 2.64, 2.63, 3.40, 5.09, 5.66, 11.42, 
        4.06, 3.80, 3.98, 3.39, 2.37, 2.37, 12.65
    ],
    "Gestora": [
        "Deutsche Bank", "Deutsche Bank", "Deutsche Bank", "Deutsche Bank", 
        "Crèdit Andorrà", "Deutsche Bank", "Crèdit Andorrà", "Crèdit Andorrà", 
        "CaixaBank", "CaixaBank", "CaixaBank", "Crèdit Andorrà", "Crèdit Andorrà",
        "Crèdit Andorrà", "Deutsche Bank", "Deutsche Bank", "CaixaBank"
    ],
    "Rendibilitat (%)": [
        2.5, 1.8, 4.2, 6.3, 8.1, 5.5, 7.3, 6.8, 9.4, 10.5, 
        0.7, 16.1, 22.2, 16.5, 9.8, 4.2, 0
    ],
    "Nivell de Risc": [
        3, 3, 5, 6, 6, 6, 5, 6, 5, 4, 3, 6, 6, 6, 5, 5, 0,
    ],
    "Empreses Principals": [
        "DWS ESG Money Market, Swedbank AB, BNP Paribas Cardif",
        "Germany Federal Bonds, JPMorgan, MSD Netherlands",
        "Flexible Allocation (sense posicions fixes)",
        "Apple, Microsoft, Amazon",
        "Apple, NVIDIA, Samsung",
        "Toyota, Sony, Nintendo",
        "Alphabet, Roche, Microsoft",
        "UnitedHealth, Eli Lilly, AbbVie",
        "Apple, Microsoft, Amazon",
        "Tesla, Alphabet, Roche",
        "No disponible",
        "UnitedHealth, Johnson & Johnson, Pfizer",
        "Apple, Microsoft, Alphabet",
        "Tencent, Samsung, Alibaba",
        "Amazon, Tesla, Roche",
        "Flexible Allocation (sense posicions fixes)",
        "N/D"
    ],
    "Distribució Geogràfica": [
        "Eurozona: 81.31%, Efectiu: 17.01%",
        "Eurozona: 87.83%, Efectiu: 9.85%",
        "Global: 100%",
        "Estats Units: 100%",
        "Global: 100%",
        "Japó: 100%",
        "Global: 100%",
        "Estats Units: 76.86%, Eurozona: 17.44%",
        "Estats Units: 100%",
        "Global: 100%",
        "Eurozona: 100%",
        "Estats Units: 100%",
        "Global: 100%",
        "Mercats Emergents: 100%",
        "Global: 100%",
        "Global: 100%",
        "Pla de pensions: 100%"
    ],
    "Distribució Actius": [
        "Renda Fixa: 70%, Efectiu: 30%",
        "Renda Fixa: 87.83%, Efectiu: 9.85%",
        "Multiactiu (Flexible)",
        "Renda Variable: 100%",
        "Tecnologia: 60%, Comunicacions: 30%",
        "Renda Variable (Japó): 100%",
        "Tecnologia: 40%, Salut: 35%, Energia: 25%",
        "Salut: 100%",
        "Renda Variable: 100%",
        "Tecnologia: 50%, Salut: 30%, Consum: 20%",
        "Renda Fixa: 70%, Altres: 30%",
        "Salut: 100%",
        "Renda Variable Global: 100%",
        "Mercats Emergents: 100%",
        "Renda Variable Global: 100%",
        "Renda Variable Global: 100%",
        "Pla de pensions: 100%"
    ],
    "Comissions (%)": [
        0.75, 0.85, 1.5, 1.0, 1.2, 0.9, 1.1, 1.4, 1.0, 1.3, 0.7, 1.5, 0.9, 1.2, 0.95, 1.0, 0
    ]
}

# Crear DataFrame
df = pd.DataFrame(data)

# Funció per calcular la distribució
def calcular_distribucio(data):
    total_pes = data["pes cartera"].sum()
    data["Percentatge"] = data["pes cartera"] / total_pes * 100
    return data

# Funció per interactuar amb OpenAI
def consultar_openai(prompt, data):
    data_text = data.to_string(index=False)
    complet_prompt = f"Tens accés a les següents dades sobre fons d'inversió:\n\n{data_text}\n\nRespon aquesta consulta:\n{prompt}"
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ets un assistent que ajuda amb l'anàlisi de dades."},
            {"role": "user", "content": complet_prompt}
        ]
    )
    return resposta["choices"][0]["message"]["content"]

# Filtres de la barra lateral
st.sidebar.subheader("Filtres")
selected_gestores = st.sidebar.multiselect("Selecciona Gestores:", options=df["Gestora"].unique(), default=df["Gestora"].unique())
selected_fons = st.sidebar.multiselect("Selecciona Fons:", options=df["Nom del Fons"].unique(), default=df["Nom del Fons"].unique())

# Aplicar filtres
filtered_df = df[df["Gestora"].isin(selected_gestores)]
filtered_df = filtered_df[filtered_df["Nom del Fons"].isin(selected_fons)]

# Títol de l'aplicació
st.title("Distribució dels Fons d'Inversió")

# Mostrar xat amb OpenAI
st.subheader("Xat amb el teu Assessor")
pregunta = st.text_input("Fes una pregunta sobre els fons:")

if st.button("Envia"):
    if pregunta:
        if not filtered_df.empty:
            resposta = consultar_openai(pregunta, filtered_df)
            st.write("### Resposta:")
            st.write(resposta)
        else:
            st.warning("No hi ha dades disponibles amb els filtres aplicats.")
    else:
        st.warning("Introdueix una pregunta primer.")

# Mostrar dades filtrades
if not filtered_df.empty:
    st.subheader("Fons Filtrats")
    st.dataframe(filtered_df)

    # Calcular distribució
    filtered_df = calcular_distribucio(filtered_df)

    # Gràfic circular de distribució
    st.subheader("Distribució dels Fons")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(filtered_df["Percentatge"], labels=filtered_df["Nom del Fons"], autopct="%1.1f%%", startangle=140)
    ax.set_title("Distribució dels Fons en la Cartera")
    st.pyplot(fig)

    # Gràfic de barres del nivell de risc
    st.subheader("Comparativa de Nivell de Risc")
    fig_risc = px.bar(filtered_df, x="Nom del Fons", y="Nivell de Risc", color="Gestora", title="Nivell de Risc per Fons")
    st.plotly_chart(fig_risc)

    # Gràfic de barres de rendibilitat
    st.subheader("Comparativa de Rendibilitat (%)")
    fig_rendibilitat = px.bar(filtered_df, x="Nom del Fons", y="Rendibilitat (%)", color="Gestora", title="Rendibilitat per Fons")
    st.plotly_chart(fig_rendibilitat)
else:
    st.warning("No hi ha dades disponibles amb els filtres aplicats.")