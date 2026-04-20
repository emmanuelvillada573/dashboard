import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="‘Dashboard Estudiantil – Grupo 01", layout="wide")

# ── Carga y limpieza 
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv", decimal=",")

    df["Fecha_Nacimiento"] = pd.to_datetime(
        df["Fecha_Nacimiento"], format="%d/%m/%Y", errors="coerce"
    )
    hoy = pd.Timestamp.today()
    df["Edad"] = (
        hoy.year - df["Fecha_Nacimiento"].dt.year
        - (
            (hoy.month < df["Fecha_Nacimiento"].dt.month)
            | (
                (hoy.month == df["Fecha_Nacimiento"].dt.month)
                & (hoy.day < df["Fecha_Nacimiento"].dt.day)
            )
        )
    )

    df["Estatura"] = pd.to_numeric(df["Estatura"], errors="coerce")
    df["Peso"]     = pd.to_numeric(df["Peso"],     errors="coerce")

    # IMC con estatura en metros antes de convertir a cm
    df["IMC"] = df["Peso"] / (df["Estatura"] ** 2)

    def clasificar_imc(imc):
        if imc < 18.5:  return "Bajo peso"
        elif imc < 25:  return "Normal"
        elif imc < 30:  return "Sobrepeso"
        else:           return "Obesidad"

    df["Clasificacion_IMC"] = df["IMC"].apply(clasificar_imc)

    # Pasar estatura a cm para mostrar
    df["Estatura"] = (df["Estatura"] * 100).round(0)

    # Normalizar texto
    df["Color_Cabello"]    = df["Color_Cabello"].str.strip().str.title()
    df["Barrio_Residencia"] = df["Barrio_Residencia"].str.strip()
    df["Nombre_Completo"]  = (
        df["Nombre_Estudiante"].str.strip() + " " + df["Apellido_Estudiante"].str.strip()
    ).str.replace(r"\s+", " ", regex=True)
    df["Talla_Zapato"] = pd.to_numeric(df["Talla_Zapato"], errors="coerce")
    return df

df = load_data()

# ── Sidebar – Filtros y sliders ───────────────────────────────────────────────
st.sidebar.header(" Filtros")

# Filtro 1 – Tipo de Sangre
rh_opts = sorted(df["RH"].dropna().unique())
rh_sel  = st.sidebar.multiselect(" Tipo de Sangre (RH)", rh_opts, default=rh_opts)

# Filtro 2 – Color de Cabello
cab_opts = sorted(df["Color_Cabello"].dropna().unique())
cab_sel  = st.sidebar.multiselect(" Color de Cabello", cab_opts, default=cab_opts)

# Filtro 3 – Barrio de Residencia
barrio_opts = sorted(df["Barrio_Residencia"].dropna().unique())
barrio_sel  = st.sidebar.multiselect(" Barrio de Residencia", barrio_opts, default=barrio_opts)

# Filtro 4 – Integrantes del grupo (antes de los sliders)
integrantes_opts = sorted(df["Nombre_Completo"].dropna().unique())
MI_EQUIPO = ["EMMANUEL VILLADA SUÁREZ", "DAYANA GARCIA RODRIGUEZ", "SEBASTIAN ESTRADA CASTAÑEDA", "BRAYAN ANDRES VILLA ARANGO"]
default_integrantes = [i for i in MI_EQUIPO if i in integrantes_opts]
integrantes_sel  = st.sidebar.multiselect(
    " Integrantes del Grupo", integrantes_opts, default=default_integrantes
)

st.sidebar.markdown("---")

# Slider – Rango de Edad
edad_min, edad_max = int(df["Edad"].min()), int(df["Edad"].max())
edad_rango = st.sidebar.slider(
    " Rango de Edad", edad_min, edad_max, (edad_min, edad_max)
)

# Slider – Rango de Estatura (cm)
est_min = int(df["Estatura"].min())
est_max = int(df["Estatura"].max())
est_rango = st.sidebar.slider(
    "📏 Rango de Estatura (cm)", est_min, est_max, (est_min, est_max)
)

# ── Aplicar filtros ───────────────────────────────────────────────────────────
mask = (
    df["RH"].isin(rh_sel)
    & df["Color_Cabello"].isin(cab_sel)
    & df["Barrio_Residencia"].isin(barrio_sel)
    & df["Nombre_Completo"].isin(integrantes_sel)
    & df["Edad"].between(*edad_rango)
    & df["Estatura"].between(*est_rango)
)
filt = df[mask].copy()

# ── Mostrar archivo ───────────────────────────────────────────────────────────
st.subheader(" Datos del Grupo")
st.dataframe(filt.drop(columns=["Nombre_Completo"]), use_container_width=True)

# ── Título ────────────────────────────────────────────────────────────────────
st.title("Dashboard Estudiantil – Grupo 01")
st.markdown("---")

# ── Métricas ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(" Total Estudiantes",  len(filt))
c2.metric(" Edad Promedio",        f"{filt['Edad'].mean():.1f} años")
c3.metric(" Estatura Promedio",    f"{filt['Estatura'].mean():.1f} cm")
c4.metric(" Peso Promedio",        f"{filt['Peso'].mean():.1f} kg")
c5.metric(" IMC Promedio",         f"{filt['IMC'].mean():.2f}")

st.markdown("---")

# ── Fila 1: Distribución por edad · Distribución por tipo de sangre ───────────
r1c1, r1c2 = st.columns(2)

with r1c1:
    fig = px.histogram(
        filt, x="Edad", nbins=15,
        title=" Distribución por Edad",
        labels={"Edad": "Edad (años)", "count": "Cantidad"},
        color_discrete_sequence=["#4C78A8"],
    )
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    fig = px.pie(
        filt, names="RH",
        title=" Distribución por Tipo de Sangre",
        hole=0.35,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Fila 2: Estatura vs Peso · Distribución por color de cabello ──────────────
r2c1, r2c2 = st.columns(2)

with r2c1:
    fig = px.scatter(
        filt, x="Estatura", y="Peso", color="Clasificacion_IMC",
        title=" Relación Estatura vs Peso",
        labels={"Estatura": "Estatura (cm)", "Peso": "Peso (kg)"},
        hover_data=["Nombre_Completo"],
    )
    st.plotly_chart(fig, use_container_width=True)

with r2c2:
    cab_counts = filt["Color_Cabello"].value_counts().reset_index()
    cab_counts.columns = ["Color", "Cantidad"]
    fig = px.bar(
        cab_counts, x="Color", y="Cantidad",
        title=" Distribución por Color de Cabello",
        color_discrete_sequence=["#72B7B2"],
        labels={"Color": "Color de Cabello"},
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Fila 3: Tallas de zapatos · Top 10 barrios ────────────────────────────────
r3c1, r3c2 = st.columns(2)

with r3c1:
    talla_counts = (
        filt["Talla_Zapato"].value_counts().sort_index().reset_index()
    )
    talla_counts.columns = ["Talla", "Cantidad"]
    fig = px.line(
        talla_counts, x="Talla", y="Cantidad",
        title=" Distribución de Tallas de Zapatos",
        markers=True,
        labels={"Talla": "Talla de Zapato"},
        color_discrete_sequence=["#F58518"],
    )
    st.plotly_chart(fig, use_container_width=True)

with r3c2:
    top10 = filt["Barrio_Residencia"].value_counts().head(10).reset_index()
    top10.columns = ["Barrio", "Cantidad"]
    fig = px.bar(
        top10, x="Cantidad", y="Barrio", orientation="h",
        title=" Top 10 Barrios de Residencia",
        color_discrete_sequence=["#E45756"],
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Descargas Top 5 ───────────────────────────────────────────────────────────
st.subheader(" Top 5")

cols_show = ["Nombre_Completo", "Estatura", "Peso", "IMC", "Clasificacion_IMC"]
top5_est  = filt.nlargest(5, "Estatura")[cols_show].reset_index(drop=True)
top5_peso = filt.nlargest(5, "Peso")[cols_show].reset_index(drop=True)
top5_est.index  += 1
top5_peso.index += 1

dl1, dl2 = st.columns(2)

with dl1:
    st.markdown("** Mayor Estatura**")
    st.dataframe(top5_est, use_container_width=True)
    st.download_button(
        " Descargar CSV",
        top5_est.to_csv(index=True).encode("utf-8"),
        "top5_mayor_estatura.csv",
        "text/csv",
        key="dl_estatura",
    )

with dl2:
    st.markdown("** Mayor Peso**")
    st.dataframe(top5_peso, use_container_width=True)
    st.download_button(
        " Descargar CSV",
        top5_peso.to_csv(index=True).encode("utf-8"),
        "top5_mayor_peso.csv",
        "text/csv",
        key="dl_peso",
    )

st.markdown("---")

# ── Resumen Estadístico ───────────────────────────────────────────────────────
st.subheader(" Resumen Estadístico")

sc1, sc2, sc3 = st.columns(3)

with sc1:
    st.markdown("** Estatura (cm)**")
    st.dataframe(
        filt["Estatura"].describe().round(2).rename("Estatura (cm)").to_frame(),
        use_container_width=True,
    )

with sc2:
    st.markdown("** Peso (kg)**")
    st.dataframe(
        filt["Peso"].describe().round(2).rename("Peso (kg)").to_frame(),
        use_container_width=True,
    )

with sc3:
    st.markdown("** IMC**")
    st.dataframe(
        filt["IMC"].describe().round(2).rename("IMC").to_frame(),
        use_container_width=True,
    )
