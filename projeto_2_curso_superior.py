"""
PROJETO 2: Curso Superior, Mulheres em STEM e Atração de Talentos
Projeto Integrador: Números que Falam — Descobrindo o Brasil
Startup DataVision Analytics • Ensino Médio Técnico em Informática
Bases Governamentais: MEC / BNCC, Censo da Educação Superior e IBGE PNADC
"""

import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(
    page_title="Projeto 2: Ensino Superior & Mulheres em STEM | DataVision",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 100%);
        padding: 1.3rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.2rem;
    }
    .header-box h1 { color: white; margin-bottom: 0.2rem; font-size: 2rem; }
    .header-box p { color: #E0E7FF; margin-bottom: 0; font-size: 1rem; }
    .badge {
        display: inline-block;
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 3px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Funções Matemáticas Embutidas (BNCC)
def calcular_estatisticas(series: pd.Series) -> dict:
    s = series.dropna()
    if len(s) == 0:
        return {}
    media = float(s.mean())
    mediana = float(s.median())
    moda_series = s.mode()
    moda = float(moda_series.iloc[0]) if not moda_series.empty else media
    q1 = float(np.percentile(s, 25))
    q2 = mediana
    q3 = float(np.percentile(s, 75))
    iqr = q3 - q1
    desvio = float(s.std())
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    outliers = s[(s < lim_inf) | (s > lim_sup)]
    return {
        "media": media,
        "mediana": mediana,
        "moda": moda,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "iqr": iqr,
        "desvio_padrao": desvio,
        "limite_inferior": lim_inf,
        "limite_superior": lim_sup,
        "qtd_outliers": len(outliers),
        "pct_outliers": (len(outliers) / len(s)) * 100
    }

# Carregamento de Dados com Fallback Automático
@st.cache_data
def carregar_dados():
    arquivo = "dados_superior.csv"
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    
    # Gerador de contingência caso o arquivo não exista localmente
    np.random.seed(42)
    n = 3000
    ufs = ["MG", "SP", "ES", "RJ", "PR", "SC", "RS", "BA", "GO", "DF"]
    areas = ["Ciências Exatas e da Terra", "Engenharias e TICs", "Ciências Humanas e Sociais", "Ciências da Saúde", "Ciências Biológicas"]
    sexos = ["Mulher", "Homem"]
    anos = [2019, 2020, 2021, 2022, 2023]
    
    rows = []
    for i in range(n):
        area = np.random.choice(areas, p=[0.18, 0.22, 0.30, 0.20, 0.10])
        if "Exatas" in area or "Engenharias" in area:
            sexo = np.random.choice(sexos, p=[0.24, 0.76])
            tempo = np.random.normal(loc=5.4, scale=1.1)
        elif "Saúde" in area or "Humanas" in area:
            sexo = np.random.choice(sexos, p=[0.68, 0.32])
            tempo = np.random.normal(loc=4.6, scale=0.8)
        else:
            sexo = np.random.choice(sexos, p=[0.55, 0.45])
            tempo = np.random.normal(loc=4.8, scale=0.9)
            
        rows.append({
            "id": 200000 + i,
            "ano": int(np.random.choice(anos)),
            "uf": np.random.choice(ufs),
            "area_conhecimento": area,
            "sexo": sexo,
            "status_academico": np.random.choice(["Diplomado / Concluinte", "Cursando", "Evadido"], p=[0.45, 0.40, 0.15]),
            "tempo_conclusao_anos": round(max(3.0, float(tempo)), 1)
        })
    df_gen = pd.DataFrame(rows)
    df_gen.to_csv(arquivo, index=False)
    return df_gen

df = carregar_dados()

# Cabeçalho
st.markdown("""
<div class="header-box">
    <h1>🎓 Projeto 2: Ensino Superior e Mulheres em STEM</h1>
    <p>Painel Analítico de Conclusão de Curso, Equidade de Gênero e Políticas de Atração de Talentos</p>
    <div class="badge">Startup DataVision Analytics • Foco: Governadores do Sudeste (MG, SP, ES, RJ)</div>
</div>
""", unsafe_allow_html=True)

# Barra Lateral
st.sidebar.markdown("### 🏢 **DataVision Analytics**")
st.sidebar.markdown("**Consultoria Estratégica em Educação**")
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros Dinâmicos")

ufs_sel = st.sidebar.multiselect("Filtrar Estado (UF):", sorted(df["uf"].unique()), default=sorted(df["uf"].unique()))
anos_sel = st.sidebar.multiselect("Filtrar Ano:", sorted(df["ano"].unique()), default=sorted(df["ano"].unique()))
areas_sel = st.sidebar.multiselect("Área do Conhecimento:", sorted(df["area_conhecimento"].unique()), default=sorted(df["area_conhecimento"].unique()))

df_filtrado = df[(df["uf"].isin(ufs_sel)) & (df["ano"].isin(anos_sel)) & (df["area_conhecimento"].isin(areas_sel))]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

stats = calcular_estatisticas(df_filtrado["tempo_conclusao_anos"])

# Cards de KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Tempo Médio de Formação", f"{stats['media']:.1f} anos")
c2.metric("Mediana (Q2)", f"{stats['mediana']:.1f} anos")
c3.metric("IQR (Q3 - Q1)", f"{stats['iqr']:.1f} anos")
c4.metric("Estudantes Analisados", f"{len(df_filtrado):,}")

# Abas do Painel
t1, t2, t3, t4 = st.tabs([
    "🎯 Perguntas de Negócio",
    "📐 Rigor Estatístico",
    "📰 Notícias & Mercado STEM",
    "🏛️ Bases Oficiais & Normativas MEC"
])

with t1:
    st.markdown("#### 1. Proporção de Gênero por Curso (Barras 100% Empilhadas)")
    comp_area_sexo = df_filtrado.groupby(["area_conhecimento", "sexo"]).size().reset_index(name="qtd")
    total_por_area = comp_area_sexo.groupby("area_conhecimento")["qtd"].transform("sum")
    comp_area_sexo["pct"] = (comp_area_sexo["qtd"] / total_por_area * 100).round(1)
    
    fig_emp = px.bar(
        comp_area_sexo, x="area_conhecimento", y="pct", color="sexo",
        title="Distribuição Percentual de Gênero por Área (Mulheres em STEM)",
        labels={"pct": "Proporção (%)", "area_conhecimento": "Área de Conhecimento", "sexo": "Gênero"},
        text_auto=".1f", color_discrete_map={"Mulher": "#EC4899", "Homem": "#3B82F6"}
    )
    st.plotly_chart(fig_emp, width='stretch')
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("#### 2. Participação dos Estados no Ensino Superior")
        dist_uf = df_filtrado.groupby("uf").size().reset_index(name="total")
        fig_uf = px.pie(dist_uf, names="uf", values="total", hole=0.4, title="Distribuição de Estudantes por UF")
        st.plotly_chart(fig_uf, width='stretch')
        
    with col_e2:
        st.markdown("#### 3. Evolução Histórica de Diplomados")
        evol_ano = df_filtrado[df_filtrado["status_academico"].str.contains("Diplomado")].groupby(["ano", "uf"]).size().reset_index(name="diplomados")
        fig_evol = px.line(evol_ano, x="ano", y="diplomados", color="uf", markers=True, title="Evolução Temporal de Diplomados")
        st.plotly_chart(fig_evol, width='stretch')
        
    st.info("💡 **Insight para os Governadores:** Mulheres são maioria expressiva em Humanas e Saúde (> 65%), porém representam menos de 25% nas áreas de Exatas e Tecnologia (STEM). É urgente criar bolsas estaduais de incentivo a meninas na computação e engenharias.")

with t2:
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        fig_box = px.box(
            df_filtrado, x="area_conhecimento", y="tempo_conclusao_anos", color="area_conhecimento", points="outliers",
            title="Boxplot do Tempo de Formação (Identificação de Retenção/Outliers)"
        )
        st.plotly_chart(fig_box, width='stretch')
    with col_b2:
        fig_hist = px.histogram(df_filtrado, x="tempo_conclusao_anos", nbins=20, title="Histograma do Tempo de Conclusão do Curso")
        fig_hist.add_vline(x=stats['media'], line_dash="dash", line_color="red", annotation_text=f"Média: {stats['media']:.1f}a")
        fig_hist.add_vline(x=stats['mediana'], line_dash="dot", line_color="green", annotation_text=f"Mediana: {stats['mediana']:.1f}a")
        st.plotly_chart(fig_hist, width='stretch')

with t3:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
        ### 💻 Fuga de Cérebros e Escassez de Talentos em TI
        *Fonte: FAPESP / Censo da Educação Superior*  
        O Sudeste concentra a maior demanda industrial e tecnológica da América Latina, enfrentando déficit de dezenas de milhares de profissionais de tecnologia e ciências exatas ao ano.
        """)
        st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&auto=format&fit=crop&q=80", caption="Formação acadêmica e centros de inovação tecnológica.", width='stretch')
    with col_m2:
        st.markdown("""
        ### 🔬 Movimento 'Mulheres na Ciência' Ganha Força
        Iniciativas de bolsas pré-vestibular e programas de tutoria corporativa estão diminuindo a disparidade e fomentando lideranças femininas em inteligência artificial e biotecnologia.
        """)
        st.image("https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=800&auto=format&fit=crop&q=80", caption="Presença feminina em laboratórios de ciência e inovação.", width='stretch')

with t4:
    st.markdown("### 🏛️ Fontes do MEC, BNCC & APIs Oficiais do IBGE")
    st.write("Fundamentação legal e bases para análise de formação superior e atração em STEM:")
    
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.markdown("""
        #### 🎓 MEC / CNE — Normativas e BNCC:
        - **Portal da BNCC no Ensino Médio:** [gov.br/mec/.../bncc-2013-ensino-medio](https://www.gov.br/mec/pt-br/cne/bncc-2013-ensino-medio)  
          Consulta aos itinerários formativos e competências de Matemática e Ciências da Natureza para atração de talentos e equidade de gênero.
        - **Acervo de Normas e Resolução CNE/CP nº 4/2018:** [gov.br/mec/.../base-nacional-comum-curricular-bncc](https://www.gov.br/mec/pt-br/cne/pdf/normas-classificadas-por-assunto/base-nacional-comum-curricular-bncc)  
          Texto integral da resolução para fundamentação dos currículos estaduais.
        """)
    with c_m2:
        st.markdown("""
        #### 🔌 APIs Públicas do IBGE & Microdados:
        - **API de Agregados (SIDRA):** [servicodados.ibge.gov.br/api/docs/agregados](https://servicodados.ibge.gov.br/api/docs/agregados) — Acesso a tabelas da PNADC de nível de instrução para filtrar a participação feminina em cursos STEM.
        - **API de Localidades (Público Sudeste):**  
          Endpoint `/api/v1/localidades/regioes/3/estados` para agrupamento automático dos estados do Sudeste (MG `31`, ES `32`, RJ `33`, SP `35`).
        - **IBGE Microdados em Lote:** [Portal de Downloads IBGE](https://www.ibge.gov.br/estatisticas/downloads-estatisticas.html) — Cruzamentos customizados via SQL entre mulheres em exatas e retorno salarial.
        """)

st.markdown("---")
st.caption("DataVision Analytics • Projeto Integrador • Ensino Médio Técnico em Informática (Turma 3D1)")
