import streamlit as st
import pandas as pd
import plotly.express as px
import openai
from dotenv import load_dotenv
import os

# Carregar variables d'entorn
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

# Mostrar el DataFrame filtrat
st.subheader("Dades Filtrades")
st.dataframe(filtered_df)

# La resta del codi no ha de fer referència a 'selected_fons'

# Funció per calcular la valoració
def calcular_valoracio(data):
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

# Funció per generar comentari qualitatiu amb IA
def generar_comentari_qualitatiu(data, rendibilitat_mitjana, risc_mitja, comissions_mitjanes):
    data_text = data.to_string(index=False)
    prompt = f"""
    Analitza aquesta cartera d'inversió basada en les dades següents:
    {data_text}
    
    - La rendibilitat mitjana ponderada és del {rendibilitat_mitjana:.2f}%.
    - El nivell de risc mitjà ponderat és del {risc_mitja:.2f} en una escala de 1 a 7.
    - Les comissions mitjanes són del {comissions_mitjanes:.2f}%.

    Proporciona un comentari qualitatiu sobre la diversificació, el risc, les comissions i l'adequació global.
    """
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ets un analista d'inversions que proporciona comentaris qualitatius."},
                {"role": "user", "content": prompt}
            ]
        )
        return resposta["choices"][0]["message"]["content"]
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
    st.markdown(valoracio)
    
    # Botó per generar el comentari qualitatiu
    if st.button("Genera el Comentari Qualitatiu"):
        st.subheader("Comentari Qualitatiu")
        comentari = generar_comentari_qualitatiu(filtered_df, rendibilitat_mitjana, risc_mitja, comissions_mitjanes)
        st.markdown(comentari)

# Taula de dades filtrades
st.subheader("Dades Filtrades")
st.dataframe(filtered_df)

# Visualitzacions
st.subheader("Distribució per Pesos")
fig_pesos = px.pie(
    filtered_df,
    values="Pes Cartera (%)",
    names="Nom del Fons",
    title="Distribució dels Fons en la Cartera"
)
st.plotly_chart(fig_pesos)

st.subheader("Comparativa de Rendibilitats (%)")
fig_rendibilitat = px.bar(
    filtered_df,
    x="Nom del Fons",
    y="Rendibilitat (%)",
    color="Gestora",
    title="Rendibilitat per Fons"
)
st.plotly_chart(fig_rendibilitat)

# Gràfic de dispersió per visualitzar empreses principals
st.subheader("Empreses Principals per Fons")

# Comprovar si la columna 'Empreses Principals' existeix
if "Empreses Principals" in filtered_df.columns:
    empreses_df = filtered_df.copy()

    # Dividir les empreses principals en llistes i explotar-les
    empreses_df["Empreses Principals"] = empreses_df["Empreses Principals"].str.split(", ")
    empreses_df = empreses_df.explode("Empreses Principals")

    # Crear un gràfic de dispersió per visualitzar les empreses principals per fons
    fig_empreses = px.scatter(
        empreses_df,
        x="Empreses Principals",
        y="Nom del Fons",
        color="Gestora",
        title="Empreses Principals per Fons",
        labels={"Empreses Principals": "Empreses", "Nom del Fons": "Fons"},
        size_max=10,
        height=600,
        width=1000
    )

    # Mostrar el gràfic a Streamlit
    st.plotly_chart(fig_empreses)
else:
    st.warning("La columna 'Empreses Principals' no existeix al DataFrame filtrat.")

# Dividir les distribucions geogràfiques en categories
geo_df = filtered_df.copy()

# Convertir la columna 'Distribució Geogràfica' en un format processable
geo_df["Distribució Geogràfica"] = geo_df["Distribució Geogràfica"].str.replace("%", "").str.split(", ")

# Crear un nou DataFrame amb les categories separades
geo_expanded = geo_df.explode("Distribució Geogràfica").reset_index()
geo_expanded[["Categoria", "Percentatge"]] = geo_expanded["Distribució Geogràfica"].str.split(": ", expand=True)
geo_expanded["Percentatge"] = geo_expanded["Percentatge"].astype(float)

# Crear un gràfic de barres apilades
st.subheader("Distribució Geogràfica dels Fons")
fig_geo = px.bar(
    geo_expanded,
    x="Nom del Fons",
    y="Percentatge",
    color="Categoria",
    title="Distribució Geogràfica dels Fons",
    labels={"Percentatge": "Percentatge (%)", "Nom del Fons": "Fons"},
    text="Percentatge"
)

# Ajustar el disseny
fig_geo.update_layout(barmode="stack", xaxis_tickangle=-45)

# Mostrar el gràfic a Streamlit
st.plotly_chart(fig_geo)
