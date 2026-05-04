import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from nba_api.stats.static import players as nba_players


st.set_page_config(page_title="NBA Shot Chart", layout="wide")
st.title("NBA Shot Charts 2024-2025")

@st.cache_data
def load_data():
    # chargement du dataset
    df = pd.read_csv('shotdetail_2024.csv')
    # transformation de coordonnées en feet pour l'affichage plus tard
    df['LOC_X'] = df['LOC_X'] / 10
    df['LOC_Y'] = df['LOC_Y'] / 10 + 5.25

    # on enleve les tirs de l'autre moitier de terain
    df = df[df['LOC_Y'] <= 47]
    return df

df = load_data()

# Sélecteur de joueur avec streamlit
players = sorted(df['PLAYER_NAME'].unique())
selected_player = st.selectbox("Pick a player", players)

player_shots = df[df['PLAYER_NAME'] == selected_player]

player_made = player_shots[player_shots['SHOT_MADE_FLAG'] == 1]

player_miss = player_shots[player_shots['SHOT_MADE_FLAG'] == 0]

# Récupération des infos joueur
player_id = player_shots['PLAYER_ID'].iloc[0]
photo_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
team_id = player_shots['TEAM_ID'].iloc[0]
logo_url = f"https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg"

# Chercher les infos du joueur avec nba_api
all_players = nba_players.get_players()
player_info = next((p for p in all_players if p['id'] == player_id), None)

if player_info:
    taille = player_info.get('height', 'N/A')
    poste = player_info.get('position', 'N/A')
    poids = player_info.get('weight', 'N/A')
else:
    taille = poste = poids = 'N/A'


_, col_main, _ = st.columns([1, 2, 1])

with col_main:
    col_photo, col_logo = st.columns([1, 1])
    
    with col_photo:
        st.image(photo_url, width=200)
    
    with col_logo:
        st.image(logo_url, width=150)
    
    st.markdown(f"<h2 style='text-align: center'>{selected_player}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center'>{taille}  |  {poste}  |  {poids}</p>", unsafe_allow_html=True)
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Total tirs", len(player_shots))
    with col_stat2:
        st.metric("Tirs réussis", len(player_made))
    with col_stat3:
        pct = len(player_made)/len(player_shots)*100 if len(player_shots) > 0 else 0
        st.metric("Pourcentage", f"{pct:.1f}%")



# on utilise plotly pour dessiner

def build_limite(fig) :
    fig.add_shape(
    type="rect",
    x0=-25, x1=25,
    y0=0, y1=42,
    line=dict(color="white", width=2)
)

def build_raquette(fig) :
    fig.add_shape(
    type="rect",
    x0=-8, x1=8,
    y0=0, y1=19,
    line=dict(color="white", width=2)
    )
    fig.add_shape(
    type="rect",
    x0=-6, x1=6,
    y0=0, y1=19,
    line=dict(color="white", width=2)
    )

def build_lf(fig) :
    fig.add_shape(
        type="circle",
        x0=-6, y0=19 - 6,
        x1=6,  y1=19 + 6,
        line=dict(color="white", width=2),
    )

def build_3Pline(fig) :
    basket_x, basket_y = 0, 5.25

    # on génère tous les angles possibles
    theta = np.linspace(0, np.pi, 560)
    arc_x = basket_x + 23.75 * np.cos(theta)
    arc_y = basket_y + 23.75 * np.sin(theta)

    # on garde uniquement les points où x est entre -22 et 22 (au-delà c'est le corner à 22ft)
    mask = (arc_x >= -22) & (arc_x <= 22)

    # segments droits corner 3 (à exactement 22ft du panier sur les côtés)
    fig.add_shape(type="line", x0=-22, x1=-22, y0=0, y1=basket_y + 23.75 * np.sin(np.arccos(22/23.75)), line=dict(color="white", width=2))
    fig.add_shape(type="line", x0=22,  x1=22,  y0=0, y1=basket_y + 23.75 * np.sin(np.arccos(22/23.75)), line=dict(color="white", width=2))

    # arc central
    fig.add_trace(go.Scatter(
        x=arc_x[mask], y=arc_y[mask],
        mode='lines',
        line=dict(color='white', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))

def build_player_shots(fig) : 
    fig.add_trace(go.Scatter(
        x = player_miss['LOC_X'],
        y = player_miss['LOC_Y'],
        mode='markers',
        name='Tirs Manqués',
        marker=dict(color='red', size=6, opacity = 0.8)
    ))

    fig.add_trace(go.Scatter(
        x = player_made['LOC_X'],
        y = player_made['LOC_Y'],
        mode='markers',
        name='Tirs Réussis',
        marker=dict(color='blue', size=6, opacity = 0.8)
    ))


def build_basket(fig) :
    # panier (cercle de rayon 0.75ft centré sur le panier)
    basket_x, basket_y = 0, 5.25
    theta_basket = np.linspace(0, 2 * np.pi, 100)
    fig.add_trace(go.Scatter(
        x=basket_x + 0.75 * np.cos(theta_basket),
        y=basket_y + 0.75 * np.sin(theta_basket),
        mode='lines',
        line=dict(color='orange', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))

def build_terrain() :
    fig = go.Figure() # type: go.Figure
    build_limite(fig)
    build_raquette(fig)
    build_lf(fig)
    build_3Pline(fig)
    build_player_shots(fig)
    build_basket(fig)
    return fig

# on s'occupe maintnant de créer un graphique dans lequel on divise le terrain par zone, cela permet de voir les pourcentages du joueurs dans chaque zones du terrain

def get_zone(row):
    x = row['LOC_X']
    y = row['LOC_Y']
    
    # Distance au panier (panier à x=0, y=5.25)
    dist = ((x**2 + (y - 5.25)**2) ** 0.5)
    
    # ── Raquette (dans la paint box : |x| <= 8, y <= 19) ──
    if abs(x) <= 8 and y <= 19:
        return "Raquette"
    
    # ── Corner 3 (|x| > 22 donc ligne droite du 3pts) ──
    if x <= -22:
        return "Corner 3 Gauche"
    if x >= 22:
        return "Corner 3 Droit"
    
    # ── Au-delà de l'arc 3pts (dist > 23.75 et pas corner) ──
    if dist > 23.75:
        if x < -4:
            return "3pts Côté Gauche"
        elif x > 4:
            return "3pts Côté Droit"
        else:
            return "3pts Centre"
    
    # ── Mi-distance (entre raquette et arc, y <= 19 mais hors raquette) ──
    if y <= 19:
        if x < 0:
            return "Mid-Range Gauche"
        else:
            return "Mid-Range Droit"
    
    # ── Mi-distance haute (y entre 19 et ~28, dans l'arc) ──
    if x < -4:
        return "Mid-Range Aile Gauche"
    elif x > 4:
        return "Mid-Range Aile Droit"
    else:
        return "Mid-Range Centre"


MIN_TENTATIVES = 5

def pct_to_color(pct, min_pct=20, max_pct=65):
    t = max(0, min(1, (pct - min_pct) / (max_pct - min_pct)))
    # Interpolation manuelle rouge → jaune → vert
    if t < 0.5:
        r, g, b = 220, int(t * 2 * 220), 0        # rouge → jaune
    else:
        r, g, b = int((1 - t) * 2 * 220), 200, 0  # jaune → vert
    return f'rgb({r},{g},{b})'

def build_zone_chart(player_shots):
    df_zones = player_shots.copy()
    df_zones['zone'] = df_zones.apply(get_zone, axis=1)
    
    stats = df_zones.groupby('zone').agg(
        tentatives=('SHOT_MADE_FLAG', 'count'),
        réussis=('SHOT_MADE_FLAG', 'sum')
    ).reset_index()
    stats['pct'] = stats['réussis'] / stats['tentatives'] * 100
    stats = stats.sort_values('pct', ascending=True)

    # Couleur grise si échantillon trop faible, sinon RdYlGn
    colors = [
        'lightgray' if t < MIN_TENTATIVES else pct_to_color(p)
        for p, t in zip(stats['pct'], stats['tentatives'])
    ]

    # Label différent pour les zones grises
    labels = [
        f"⚠ {t} tirs seulement" if t < MIN_TENTATIVES else f"{p:.1f}%  ({t} tirs)"
        for p, t in zip(stats['pct'], stats['tentatives'])
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=stats['zone'],
        x=stats['pct'],
        orientation='h',
        marker_color=colors,
        text=labels,
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>%{x:.1f}%<br>%{customdata} réussis',
        customdata=stats['réussis'],
    ))
    
    # Ligne de moyenne calculée uniquement sur les zones fiables
    stats_fiables = stats[stats['tentatives'] >= MIN_TENTATIVES]
    if len(stats_fiables) > 0:
        moy = stats_fiables['réussis'].sum() / stats_fiables['tentatives'].sum() * 100
        fig.add_vline(x=moy, line_dash="dash", line_color="gray", opacity=0.6,
                      annotation_text=f"Moy. {moy:.1f}%", annotation_position="top")

    fig.update_layout(
        xaxis=dict(title="% de réussite", range=[0, 85]),
        yaxis=dict(title=""),
        height=420,
        margin=dict(l=10, r=100, t=20, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig








# On affiche maintenant les graphes 

fig = build_terrain()

fig.update_yaxes(scaleanchor="x", scaleratio=1)
fig.update_xaxes(range=[-30, 30])
fig.update_yaxes(range=[-5, 50])
fig.update_layout(
    width=800,
    height=700,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

# css intégré grace à streamlit
st.markdown("""
<style>
    /* Titre principal */
    .stTitle {
        color: #1D428A;
        font-family: 'Impact', sans-serif;
    }
    /* Cartes des stats */
    .stMetric {
        background-color: blue;
        border-radius: 10px;
        padding: 10px;
    }
    /* Fond de page */
    .stApp {
        background-color: #black;
    }
</style>
""", unsafe_allow_html=True)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Efficacité par zone")
fig_zones = build_zone_chart(player_shots)
st.plotly_chart(fig_zones, use_container_width=True)