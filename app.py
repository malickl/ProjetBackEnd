import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_lottie import st_lottie
import json
import datetime

##################################
#     CONFIGURATION DE LA PAGE   #
##################################
st.set_page_config(
    page_title="Tableau de Bord E-commerce",
    page_icon="🛍️",
    layout="wide"
)

##################################
#     CHARGEMENT ANIMATION       #
##################################
def charger_animation_lottie(nom_fichier: str):
    with open(nom_fichier, "r") as f:
        return json.load(f)

try:
    anim_lottie = charger_animation_lottie("animation.json")
except:
    anim_lottie = {}

##################################
#  STYLE CSS PERSONNALISE (HTML) #
##################################
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap');

body {
  font-family: 'Quicksand', sans-serif;
  background: #f2f2f2;
}
.entete {
  background: linear-gradient(135deg, #6B93D6, #68B5D6, #73BA9B);
  padding: 2.5rem;
  border-radius: 12px;
  text-align: center;
  color: white;
  margin-bottom: 2rem;
  animation: fadeDown 1.5s ease-in-out;
}
.entete h1 {
  margin: 0;
  font-weight: 700;
  letter-spacing: 1px;
  font-size: 2.2rem;
}
@keyframes fadeDown {
  0% {opacity: 0; transform: translateY(-30px);}
  100% {opacity: 1; transform: translateY(0);}
}
.conteneur-kpi {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  margin-bottom: 1.5rem;
}
.conteneur-kpi h3 {
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
}
</style>
""", unsafe_allow_html=True)

##################################
#        FONCTIONS UTILES        #
##################################
def requete_api(url: str, date_debut=None, date_fin=None) -> pd.DataFrame:
    """
    Envoie une requête GET à l'endpoint spécifié, en passant date_debut et date_fin
    comme paramètres de requête (pour filtrer côté API).
    """
    try:
        params = {}
        if date_debut and date_fin:
            params["date_debut"] = date_debut.isoformat()
            params["date_fin"] = date_fin.isoformat()

        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            return pd.DataFrame(data)
        else:
            st.error(f"Erreur {resp.status_code} en récupérant : {url}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Problème de connexion: {e}")
        return pd.DataFrame()

##################################
#           URLs DE L'API        #
##################################
BASE_URL = "http://localhost:8000/kpi"

URL_CLIENTS = {
    "ventes_client": f"{BASE_URL}/ventes-par-client",
    "commandes_client": f"{BASE_URL}/commandes-par-client",  # nouveau KPI
    "panier_moyen": f"{BASE_URL}/panier-moyen-par-client",
    "profit_client": f"{BASE_URL}/clients-par-profit",
    "quantite_client": f"{BASE_URL}/quantite-par-client"
}

URL_COMMANDES = {
    "prod_quantite": f"{BASE_URL}/produits-par-quantite",
    "profit_par_region": f"{BASE_URL}/profit-par-region",
    "cat_rentables": f"{BASE_URL}/categories-plus-rentables",
    "sous_cat_ventes": f"{BASE_URL}/sous-categories-par-ventes",
    "remise_moy": f"{BASE_URL}/produits-remise-moyenne"
}

URL_PERFORMANCE = {
    "ventes_globales": f"{BASE_URL}/ventes-globales",
    "nb_commandes": f"{BASE_URL}/nombre-commandes-global",
    "nb_produits": f"{BASE_URL}/nombre-produits-vendus",
    "profit_global": f"{BASE_URL}/profit-global",
    "remise_global": f"{BASE_URL}/remise-moyenne-globale"
}

##################################
#        ENTÊTE / HEADER         #
##################################
st.markdown("<div class='entete'><h1>Tableau de Bord E-commerce</h1></div>", unsafe_allow_html=True)

col_anim, col_titre = st.columns([1,2])
with col_anim:
    st_lottie(anim_lottie, height=150, key="animation-lottie")
with col_titre:
    st.write("### Bienvenue dans un tableau de bord interactif pour analyser vos ventes, commandes et performances.")
    st.write("Utilisez les **filtres** (dates, top N) et naviguez entre les onglets ci-dessous.")

##################################
#   FILTRE DATES (SIDEBAR)       #
##################################
st.sidebar.title("Filtres")
st.sidebar.write("#### Filtre Date")
default_start = datetime.date(2023, 1, 1)
default_end = datetime.date.today()
date_range = st.sidebar.date_input("Intervalle de dates", (default_start, default_end))
if len(date_range) == 2:
    date_debut, date_fin = date_range
else:
    date_debut, date_fin = default_start, default_end

##################################
#      ONGLETS / TABS            #
##################################
onglet1, onglet2, onglet3 = st.tabs(["Clients", "Commandes", "Performance Globale"])

##################################
#          ONGLET : CLIENTS      #
##################################
with onglet1:
    st.subheader("Analyse des Clients")

    # Slider pour limiter le nombre de barres (top N)
    top_n_clients = st.slider("Nombre de Clients à Afficher (TOP N)", 5, 30, 5, key="topNClients")

    # Récupération des données
    df_ventes = requete_api(URL_CLIENTS["ventes_client"], date_debut, date_fin)
    df_commandes = requete_api(URL_CLIENTS["commandes_client"], date_debut, date_fin)
    df_panier = requete_api(URL_CLIENTS["panier_moyen"], date_debut, date_fin)
    df_profit = requete_api(URL_CLIENTS["profit_client"], date_debut, date_fin)
    df_quantite = requete_api(URL_CLIENTS["quantite_client"], date_debut, date_fin)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='conteneur-kpi'><h3>Ventes Totales (par Client)</h3></div>", unsafe_allow_html=True)
        if not df_ventes.empty:
            # On trie selon ventes_totales
            df_ventes_top = df_ventes.sort_values("ventes_totales", ascending=False).head(top_n_clients)
            fig_ventes = px.bar(df_ventes_top, x="ventes_totales", y="_id", orientation="h",
                                color="ventes_totales", color_continuous_scale="Blues")
            st.plotly_chart(fig_ventes, use_container_width=True)

        st.markdown("<div class='conteneur-kpi'><h3>Panier Moyen</h3></div>", unsafe_allow_html=True)
        if not df_panier.empty:
            df_panier_top = df_panier.sort_values("panier_moyen", ascending=False).head(top_n_clients)
            fig_panier = px.bar(df_panier_top, x="panier_moyen", y="_id", orientation="h",
                                color="panier_moyen", color_continuous_scale="algae")
            st.plotly_chart(fig_panier, use_container_width=True)

    with col2:
        st.markdown("<div class='conteneur-kpi'><h3>Nombre de Commandes (par Client)</h3></div>", unsafe_allow_html=True)
        if not df_commandes.empty:
            df_cmd_top = df_commandes.sort_values("nombre_commandes", ascending=False).head(top_n_clients)
            fig_cmd = px.bar(df_cmd_top, x="nombre_commandes", y="_id", orientation="h",
                             color="nombre_commandes", color_continuous_scale="sunset")
            st.plotly_chart(fig_cmd, use_container_width=True)

        st.markdown("<div class='conteneur-kpi'><h3>Profit (par Client)</h3></div>", unsafe_allow_html=True)
        if not df_profit.empty:
            df_profit_top = df_profit.sort_values("profit_total", ascending=False).head(top_n_clients)
            fig_profit = px.bar(df_profit_top, x="profit_total", y="_id", orientation="h",
                                color="profit_total", color_continuous_scale="amp")
            st.plotly_chart(fig_profit, use_container_width=True)

    st.markdown("<div class='conteneur-kpi'><h3>Quantité Totale de Produits Achetés</h3></div>", unsafe_allow_html=True)
    if not df_quantite.empty:
        df_quantite_top = df_quantite.sort_values("quantite_totale", ascending=False).head(top_n_clients)
        fig_quantite = px.bar(df_quantite_top, x="quantite_totale", y="_id", orientation="h",
                              color="quantite_totale", color_continuous_scale="reds")
        st.plotly_chart(fig_quantite, use_container_width=True)

##################################
#        ONGLET : COMMANDES      #
##################################
with onglet2:
    st.subheader("Analyse des Commandes")

    # Slider pour limiter le nombre de barres (top N)
    top_n_commandes = st.slider("Nombre de Barres (TOP N) - Commandes", 5, 30, 5, key="topNCommandes")

    df_produits_qte = requete_api(URL_COMMANDES["prod_quantite"], date_debut, date_fin)
    df_profit_reg = requete_api(URL_COMMANDES["profit_par_region"], date_debut, date_fin)
    df_cat = requete_api(URL_COMMANDES["cat_rentables"], date_debut, date_fin)
    df_souscat = requete_api(URL_COMMANDES["sous_cat_ventes"], date_debut, date_fin)
    df_remise = requete_api(URL_COMMANDES["remise_moy"], date_debut, date_fin)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='conteneur-kpi'><h3>Produits par Quantité Vendue</h3></div>", unsafe_allow_html=True)
        if not df_produits_qte.empty:
            df_qte_top = df_produits_qte.sort_values("quantite_vendue", ascending=False).head(top_n_commandes)
            fig_qte = px.bar(df_qte_top, x="quantite_vendue", y="_id", orientation="h",
                             color="quantite_vendue", color_continuous_scale="blues")
            st.plotly_chart(fig_qte, use_container_width=True)

        st.markdown("<div class='conteneur-kpi'><h3>Catégories les plus Rentables</h3></div>", unsafe_allow_html=True)
        if not df_cat.empty:
            df_cat_top = df_cat.sort_values("profit_total", ascending=False).head(top_n_commandes)
            fig_cat = px.pie(df_cat_top, names="_id", values="profit_total",
                             color_discrete_sequence=px.colors.sequential.Tealgrn,
                             title="Répartition du Profit par Catégorie")
            st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.markdown("<div class='conteneur-kpi'><h3>Profit par Région</h3></div>", unsafe_allow_html=True)
        if not df_profit_reg.empty:
            df_reg_top = df_profit_reg.sort_values("profit_total", ascending=False).head(top_n_commandes)
            fig_reg = px.bar(df_reg_top, x="profit_total", y="_id", orientation="h",
                             color="profit_total", color_continuous_scale="reds")
            st.plotly_chart(fig_reg, use_container_width=True)

        st.markdown("<div class='conteneur-kpi'><h3>Sous-Catégories par Ventes</h3></div>", unsafe_allow_html=True)
        if not df_souscat.empty:
            df_souscat_top = df_souscat.sort_values("ventes_totales", ascending=False).head(top_n_commandes)
            fig_souscat = px.bar(df_souscat_top, x="ventes_totales", y="_id", orientation="h",
                                 color="ventes_totales", color_continuous_scale="amp")
            st.plotly_chart(fig_souscat, use_container_width=True)

    st.markdown("<div class='conteneur-kpi'><h3>Produits - Remise Moyenne</h3></div>", unsafe_allow_html=True)
    if not df_remise.empty:
        df_rem_top = df_remise.sort_values("remise_moyenne", ascending=False).head(top_n_commandes)
        fig_rem = px.bar(df_rem_top, x="remise_moyenne", y="_id", orientation="h",
                         color="remise_moyenne", color_continuous_scale="peach")
        st.plotly_chart(fig_rem, use_container_width=True)

##################################
#    ONGLET : PERFORMANCE GLOBALE
##################################
with onglet3:
    st.subheader("Performance Globale")

    # Ici, tu n’as pas vraiment de bar charts, mais on pourrait imaginer un top N
    # s’il y avait des métriques par région / segment. Si tu veux l’ajouter, tu peux.
    # Pour l’instant, on laisse le slider de côté ici, ou on peut le commenter.

    df_ventes_glob = requete_api(URL_PERFORMANCE["ventes_globales"], date_debut, date_fin)
    df_nb_cmd = requete_api(URL_PERFORMANCE["nb_commandes"], date_debut, date_fin)
    df_nb_prod = requete_api(URL_PERFORMANCE["nb_produits"], date_debut, date_fin)
    df_profit_g = requete_api(URL_PERFORMANCE["profit_global"], date_debut, date_fin)
    df_discount_g = requete_api(URL_PERFORMANCE["remise_global"], date_debut, date_fin)

    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown("<div class='conteneur-kpi'><h3>Ventes Globales</h3></div>", unsafe_allow_html=True)
        if not df_ventes_glob.empty:
            val_ventes = df_ventes_glob.iloc[0].get("ventes_globales", 0)
            st.metric("Montant Total (€)", f"{val_ventes:,.2f}")

        st.markdown("<div class='conteneur-kpi'><h3>Commandes Totales</h3></div>", unsafe_allow_html=True)
        if not df_nb_cmd.empty:
            val_cmd = df_nb_cmd.iloc[0].get("total_commandes", 0)
            st.metric("Nb Commandes", f"{val_cmd:,}")

    with colB:
        st.markdown("<div class='conteneur-kpi'><h3>Produits Vendus</h3></div>", unsafe_allow_html=True)
        if not df_nb_prod.empty:
            val_prod = df_nb_prod.iloc[0].get("quantite_totale_vendue", 0)
            st.metric("Qté Produits", f"{val_prod:,}")

        st.markdown("<div class='conteneur-kpi'><h3>Profit Global</h3></div>", unsafe_allow_html=True)
        if not df_profit_g.empty:
            val_profit = df_profit_g.iloc[0].get("profit_total", 0)
            st.metric("Profit (€)", f"{val_profit:,.2f}")

    with colC:
        st.markdown("<div class='conteneur-kpi'><h3>Remise Moyenne</h3></div>", unsafe_allow_html=True)
        if not df_discount_g.empty:
            val_remise = df_discount_g.iloc[0].get("remise_globale", 0)
            st.metric("Taux de Remise (%)", f"{val_remise*100:.2f}%")
