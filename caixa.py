import streamlit as st
import pandas as pd
import plotly.express as px

import openai
from dotenv import load_dotenv
import os

# Carregar variables d'entorn
load_dotenv()

# Configuració de l'API
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    resposta = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-1106:mcd-personal::AkGFKNCH",  # Model personalitzat
        messages=[
            {"role": "system", "content": "Ets un assistent catalàen finances personals que ajuda amb l'anàlisi de dades dels meus fons d'inversió proporcionant respostes àmplies i detallades."},
            {"role": "user", "content": "Quin és l'equilibri global de la meva cartera'?"}
        ]
    )
    print(resposta["choices"][0]["message"]["content"])
except Exception as e:
    print(f"Error amb l'API d'OpenAI: {str(e)}")
# Dades dels fons
data = {
    "ISIN": [
        "LU0034353002", "LU0113257694", "LU0599946893", "LU0218171717",
        "IE00B4468526", "LU1769942233", "LU0203975437", "LU0171307068",
        "LU0232524495", "LU1295551144"
    ],
    "Nom del Fons": [
        "DWS FLOAT RATE NOTES", "SISF EUR CORPORATE BOND", "DWS CONCEPT KALDEMORGEN",
        "JPM US SELECT EQ A EUR", "POLAR CAPITAL GLOBAL TECHNOLOGY R EUR",
        "DWS INVEST CROCI JAPAN", "ROBECO GLOBAL PREMIUM", "BGF WORLD HEALTHSCIENCE FUND A2 EUR",
        "AB AMERICAN GROWTH PORTFOLIO", "CAPITAL GROUP NEW PERSPECTIVE"
    ],
    "Pes Cartera (%)": [
        5.83, 4.11, 22.62, 3.97, 2.64, 2.63, 3.40, 5.09, 5.66, 11.42
    ],
    "Gestora": [
        "Deutsche Bank", "Schroders", "DWS", "JPMorgan",
        "Polar Capital", "DWS", "Robeco", "BlackRock",
        "Alliance Bernstein", "Capital Group"
    ],
    "Rendibilitat (%)": [
        2.56, 1.42, 7.0, 11.5, 18.42, 17.54, 6.19, 7.84, 14.8, 10.5
    ],
    "Nivell de Risc": [
        2, 2, 5, 4, 6, 5, 4, 5, 5, 4
    ],
    "Distribució Geogràfica": [
        "Europa: 50%, EUA: 35%, Altres: 15%",
        "Europa: 80%, EUA: 20%", "Global: 100%",
        "EUA: 90%, Altres: 10%", "EUA: 70%, Àsia: 20%, Altres: 10%",
        "Japó: 100%", "Global: 100%", "EUA: 85%, Europa: 15%",
        "EUA: 100%", "Global: 100%"
    ],
    "Comissions (%)": [
        0.26, 1.04, 1.56, 1.50, 1.62, 1.30, 0.95, 1.77, 1.0, 1.3
    ],
    "Empreses Principals": [
        "Swedbank, BNP Paribas, Rabobank",
        "BMW, MSD Netherlands, Wintershall DEA",
        "Alphabet, Microsoft, Allianz",
        "Apple, Microsoft, Amazon",
        "NVIDIA, Meta, TSMC",
        "Sony, Toyota, Daikin",
        "Roche, Microsoft, ExxonMobil",
        "UnitedHealth, Eli Lilly, AbbVie",
        "Apple, Microsoft, Tesla",
        "Tesla, Alphabet, Roche"
    ]
}

# Crear DataFrame
df = pd.DataFrame(data)

# Sidebar per filtres
st.sidebar.title("Filtres")
selected_gestores = st.sidebar.multiselect(
    "Selecciona Gestora:", df["Gestora"].unique(), default=df["Gestora"].unique()
)

# Aplicar filtres només per Gestora
filtered_df = df[df["Gestora"].isin(selected_gestores)]
# Caixa de preguntes interactives amb OpenAI
st.subheader("Xat amb el teu Assessor")

# Entrada de la pregunta
pregunta = st.text_input("Fes una pregunta sobre els fons, distribució de la cartera, etc.:")
if st.button("Consulta"):
    # Comprovar si s'ha introduït una pregunta
    if not pregunta.strip():
        st.warning("Si us plau, introdueix una pregunta abans d'enviar.")
    elif filtered_df.empty:
        st.warning("No hi ha dades disponibles amb els filtres aplicats.")
    else:
        try:
            # Preparar les dades filtrades per al prompt
            data_text = filtered_df.to_string(index=False)
            complet_prompt = f"""
            Tens accés a les següents dades sobre fons d'inversió:

            {data_text}

            Respon aquesta consulta:
            {pregunta}
            """

            # Crida a l'API d'OpenAI
            resposta = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ets un assistent que ajuda amb l'anàlisi de dades."},
                    {"role": "user", "content": complet_prompt}
                ],
                stop=[" ->"]
            )

            # Processar la resposta
            resposta_text = resposta.choices[0].message.content.strip()
            st.write("### Resposta:")
            st.write(resposta_text)
        except Exception as e:
            st.error(f"Hi ha hagut un error processant la resposta: {str(e)}")

# Funció per calcular la valoració de la cartera
def calcular_valoracio(data):
    try:
        # Rendibilitat mitjana ponderada
        rendibilitat_mitjana = sum(data["Pes Cartera (%)"] * data["Rendibilitat (%)"]) / sum(data["Pes Cartera (%)"])
        # Nivell de risc mitjà ponderat
        risc_mitja = sum(data["Pes Cartera (%)"] * data["Nivell de Risc"]) / sum(data["Pes Cartera (%)"])
        # Comissions mitjanes
        comissions_mitjanes = data["Comissions (%)"].mean()

        valoracio = f"""
        ### Valoració de la cartera actual:
        - **Rendibilitat mitjana ponderada:** {rendibilitat_mitjana:.2f}%
        - **Nivell de risc mitjà ponderat:** {risc_mitja:.2f} (1-7)
        - **Comissions mitjanes:** {comissions_mitjanes:.2f}%
        - **Fons seleccionats:** {len(data)}
        """
        return valoracio, rendibilitat_mitjana, risc_mitja, comissions_mitjanes
    except Exception as e:
        st.error(f"Error calculant la valoració: {str(e)}")
        return None, 0, 0, 0

# Funció per generar un comentari qualitatiu amb IA
def generar_comentari_qualitatiu(data, rendibilitat_mitjana, risc_mitja, comissions_mitjanes):
    try:
        data_text = data.to_string(index=False)
        prompt = f"""
        Analitza aquesta cartera d'inversió basada en les dades següents:
        {data_text}

        - La rendibilitat mitjana ponderada és del {rendibilitat_mitjana:.2f}%.
        - El nivell de risc mitjà ponderat és del {risc_mitja:.2f} en una escala de 1 a 7.
        - Les comissions mitjanes són del {comissions_mitjanes:.2f}%.

        Proporciona un comentari qualitatiu sobre la diversificació, el risc, les comissions i l'adequació global.
        """
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ets un analista d'inversions que proporciona comentaris qualitatius."},
                {"role": "user", "content": prompt}
            ]
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        return f"Error amb l'API d'OpenAI: {str(e)}"

# Aplicació Streamlit
st.title("Anàlisi de la Cartera d'Inversió")

# Valoració de la cartera
st.subheader("Valoració de la Cartera")
if filtered_df.empty:
    st.write("### Cap fons seleccionat. Aplica filtres per veure la valoració.")
else:
    valoracio, rendibilitat_mitjana, risc_mitja, comissions_mitjanes = calcular_valoracio(filtered_df)
    if valoracio:
        st.markdown(valoracio)

        # Botó per generar el comentari qualitatiu
        if st.button("Genera el Comentari Qualitatiu"):
            st.subheader("Comentari Qualitatiu")
            comentari = generar_comentari_qualitatiu(filtered_df, rendibilitat_mitjana, risc_mitja, comissions_mitjanes)
            st.markdown(comentari)