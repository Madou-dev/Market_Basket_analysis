import re

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter 

@st.cache_data                                  # Met en cache le resultat : le CSV n'est relu
                                                 # et recalcule qu'une seule fois, pas a chaque interaction Streamlit
def load_data():

    df = pd.read_csv(                            # On charge le fichier CSV dans un DataFrame
        "data/Market_Basket_Optimisation.csv",
        header=None                              # Le fichier n'a pas de ligne d'en-tete, donc pas de noms de colonnes
    )

    # -------- Liste des produits uniques --------
    produits = []                                # Liste vide qui va recevoir tous les produits (avec doublons pour l'instant)
    for col in df.columns:                       # On parcourt chaque colonne du DataFrame (chaque "position" dans le panier)
        produits.extend(                          # On ajoute les elements de la colonne a la liste produits
            df[col]                               # La colonne courante
            .dropna()                             # On enleve les cases vides (paniers plus petits que le nombre max de colonnes)
            .astype(str)                          # On force le type texte (au cas ou pandas aurait mal type certaines valeurs)
            .tolist()                             # On convertit la colonne en simple liste Python
        )
    produits = sorted(list(set(produits)))        # set() enleve les doublons, list() reconvertit en liste, sorted() trie par ordre alphabetique

    # -------- Top 20 produits + tailles de panier --------
    all_products = []                             # Liste qui va contenir TOUS les produits achetes (avec doublons, utile pour compter les frequences)
    basket_size = []                              # Liste qui va contenir la taille de chaque panier (nombre de produits par transaction)

    for row in df.values:                         # On parcourt chaque ligne du DataFrame (= chaque transaction/panier), .values donne un tableau numpy
        for item in row:                          # On parcourt chaque produit a l'interieur de ce panier
            if pd.notna(item):                    # On verifie que la case n'est pas vide (NaN)
                all_products.append(item)          # Si elle contient un produit, on l'ajoute a la liste globale
        basket_size.append(pd.notna(row).sum())    # pd.notna(row) donne un tableau de True/False, .sum() compte les True = taille reelle du panier

    products_counts = Counter(all_products)        # Counter compte automatiquement le nombre d'occurrences de chaque produit
    top20 = products_counts.most_common(20)         # most_common(20) retourne les 20 produits les plus frequents sous forme de tuples (produit, frequence)
    top20_products_df = pd.DataFrame(               # On transforme cette liste de tuples en DataFrame pour pouvoir la donner a plotly
        top20,
        columns=['Produit', 'Frequence']            # On nomme les deux colonnes du DataFrame
    )

    basket_distribution = Counter(basket_size)      # On compte combien de paniers ont telle ou telle taille (ex: 500 paniers de taille 3)
    size = list(basket_distribution.keys())         # Les differentes tailles de panier rencontrees (ex: 1, 2, 3, 4...)
    frequencies = list(basket_distribution.values()) # Le nombre de transactions correspondant a chaque taille

    return produits, top20_products_df, size, frequencies   # On retourne les 4 resultats pour pouvoir les utiliser partout dans l'app


produits, top20_products_df, size, frequencies = load_data()   # On appelle la fonction une seule fois au demarrage de l'app
                                                                  # et on recupere les 4 variables prêtes a l'emploi

def clean_itemset(text):
    """Transforme frozenset({'soup', 'milk'}) en 'soup, milk'"""
    items = re.findall(r"'([^']+)'", str(text))
    return ", ".join(items) if items else str(text)


#Configuration de la page
st.set_page_config(
    page_title="Market Basket Analysis",
    page_icon="🛒",
    layout="wide"
)
# Theme custom (fond, sidebar, metriques, titres)
st.markdown("""
    <style>
    /* Fond général de la page */
    .stApp {
        background-color: #000000;
    }
 
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F0B13B;
    }
    section[data-testid="stSidebar"] * {
        color: #F4F6F8 !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 15px;
    }
 
    /* Titres */
    h1, h2, h3 {
        color: #1F2A44;
        font-family: 'Segoe UI', sans-serif;
    }
 
    /* Cartes de metriques (st.metric) */
    div[data-testid="stMetric"] {
        background-color: #90A4AE;
        border: 1px solid #E0E4E8;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricLabel"] {
        color: #6B7280;
    }
    div[data-testid="stMetricValue"] {
        color: #2E86AB;
    }
 
    /* Boutons et sliders (accent color) */
    .stSlider > div > div > div > div {
        background-color: #2E86AB;
    }
    div.stButton > button {
        background-color: #2E86AB;
        color: white;
        border-radius: 8px;
        border: none;
    }
 
    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E0E4E8;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* KPI Cards */
.metric-card {
    background-color: #262730;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #404040;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    padding: 35px;
    border-radius: 20px;
    border: 1px solid #334155;
    margin-bottom: 25px;
}

.hero-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
}

.hero-text {
    font-size: 18px;
    color: #cbd5e1;
}

/* Info Cards */
.custom-card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 15px;
    border-left: 6px solid #38bdf8;
    margin-top: 10px;
    margin-bottom: 10px;
}

/* Result Card */
.result-card {
    background: linear-gradient(135deg,#064e3b,#065f46);
    padding: 20px;
    border-radius: 15px;
    color: white;
    margin-top: 15px;
}

/* Business Card */
.business-card {
    background: linear-gradient(135deg,#78350f,#92400e);
    padding: 20px;
    border-radius: 15px;
    color: white;
    margin-top: 15px;
}

</style>
""", unsafe_allow_html=True)

st.sidebar.image(
    "images/logo.png",
    width=200
)

#Menu lateral
page = st.sidebar.radio(
    "Navigation",
    [
        "Accueil",
        "EDA",
        "Apriori",
        "FP-Growth",
        "Comparaison",
        "Analyse Produit",
        "Recommandations"
    ]
)

selected_product = st.sidebar.selectbox(
    "🔍 Choisir un produit pour l'analyse",
    produits
)
# ==========================================================
#PAGE D'ACCUEIL
# ==========================================================
if page == "Accueil":
    # st.title("🛒 Market Basket Analysis")
    st.markdown("""
<div class="hero">

<div class="hero-title">
🛒 Market Basket Analysis
</div>

<div class="hero-text">

Analyse intelligente des comportements d'achat
à l'aide des algorithmes Apriori et FP-Growth.

Découverte des associations entre produits,
cross-selling et recommandations commerciales.

</div>

</div>
""", unsafe_allow_html=True)
    st.markdown("""
<div class="custom-card">

<h3>📌 Contexte métier</h3>

Les enseignes de distribution génèrent
des milliers de transactions chaque jour.

L'objectif de ce projet est d'identifier
les produits fréquemment achetés ensemble afin :

<ul>
<li> d'augmenter les ventes ;</li>
<li> d'optimiser les promotions ;</li>
<li> d'améliorer le cross-selling ;</li>
<li> d'organiser les rayons ;</li>
<li> de recommander des produits ;</li>
</ul>

</div>
""", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
        <h1>7501</h1>
        <p>Transactions</p>
        </div>
    """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
        <h1>120</h1>
        <p>Produits</p>
        </div>
    """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
        <h1>103</h1>
        <p>Associations de produits</p>
        </div>
    """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
        <h1>94</h1>
        <p>Relations d'achat identifiées</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
<div class="result-card">

<h2>🏆 Meilleure association détectée</h2>

<h3>Spaghetti ➜ Ground Beef</h3>

<p>
Lift = 2.29
</p>

<p>
Les clients achetant des spaghetti
ont une probabilité significativement plus élevée
d'acheter également du ground beef.
</p>

</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="business-card">

<h2>💼 Impact Business</h2>

<ul>
<li>Cross-selling</li>
<li>Promotions ciblées</li>
<li>Packs produits</li>
<li>Optimisation des rayons</li>
<li>Systèmes de recommandation</li>
<li>Augmentation du panier moyen</li>
</ul>

</div>
""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
    <div class="custom-card">

    <h3>🔍 Apriori</h3>

    Recherche des combinaisons
    fréquentes de produits.

    Génération des règles d'association.

    </div>
    """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="custom-card">

    <h3>⚡ FP-Growth</h3>

    Optimisation d'Apriori via
    une structure FP-Tree.

    Réduction des calculs inutiles.

    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
### 📚 Comprendre les indicateurs clés

""")

    col3, col4 = st.columns(2)

    with col3:

        st.markdown("""
    <div class="custom-card">

    <h3>📈 Confidence</h3>

    La confidence mesure la probabilité qu'un client
    achète un produit B lorsqu'il a déjà acheté
    un produit A.

    <b>Exemple :</b>

    Spaghetti → Ground Beef

    Confidence = 22,5 %

    Cela signifie que parmi les clients ayant acheté
    des spaghetti, 22,5 % ont également acheté
    du ground beef.

    Plus la confidence est élevée,
    plus la règle est fiable.

    </div>
    """, unsafe_allow_html=True)

    with col4:

        st.markdown("""
    <div class="custom-card">

    <h3>🚀 Lift</h3>

    Le lift mesure la force réelle de l'association
    entre deux produits.

    Il compare la fréquence observée de l'association
    à celle que l'on obtiendrait par hasard.

    <b>Interprétation :</b>

    • Lift < 1 : association négative       • Lift = 1 : aucune relation

    • Lift > 1 : association positive

    <b>Exemple :</b> Lift = 2,29
    
    Les clients achètent ces deux produits
    2,29 fois plus souvent que ce qui serait attendu
    par hasard.

    </div>
    """, unsafe_allow_html=True)

# ==========================================================
#PAGE EDA
# ==========================================================
elif page == "EDA":
    st.title("Analyse Exploratoire")
    
    fig = px.bar(top20_products_df, x='Produit', y='Frequence', title='Top 20 des produits les plus vendus')
    fig.update_layout(xaxis_title="Produit", yaxis_title="Nombre d'achats")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Voir L'interprétation du graphique"):
        st.markdown("""
        📌 Interprétation

    *   Mineral Water est le produit le plus acheté avec 1788 occurrences.

    *   Les produits alimentaires de consommation courante
    (eggs, spaghetti, french fries, chocolate)
    dominent également les ventes.

    *   Cela suggère que les comportements d'achat sont centrés
    sur les produits du quotidien.
       """)

    fig2 = px.bar(
        x=size,
        y=frequencies,
        title="Distribution des tailles de panier",
        labels={"x": "Taille de panier", "y": "Nombre de transactions"}
    )
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Voir L'interprétation du graphique"):
        st.markdown("""
         📌 Interprétation

    *   La taille moyenne des paniers est de 3,91 produits.

    *   La majorité des clients achètent entre 2 et 5 produits,
    ce qui traduit un comportement d'achat relativement ciblé.

    *   Les très grands paniers sont rares.
""")
   
# ==========================================================
#PAGE APRIORI
# ==========================================================
elif page == "Apriori":

    st.title("🔍 Algorithme Apriori")

    st.metric(
        "Itemsets frequents",
        103
    )

    st.metric(
        "Regles generees",
        94
    )

    rules = pd.read_csv("results/rules.csv")

    display_cols = [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift",
        "leverage",
        "conviction"
    ]

    # --- Dataset 1 : filtrage par lift / confidence ---
    st.subheader("🎛️ Filtrer les règles")

    lift_min = st.slider(
        "Lift minimum",
        1.0,
        3.0,
        1.5,
        key="apriori_lift"
    )

    confidence_min = st.slider(
        "Confidence minimum",
        0.0,
        1.0,
        0.2,
        key="apriori_confidence"
    )

    filtered_rules = rules[
        (rules["lift"] >= lift_min)
        & (rules["confidence"] >= confidence_min)
    ]

    filtered_rules_display = filtered_rules.copy()
    filtered_rules_display["antecedents"] = filtered_rules_display["antecedents"].apply(clean_itemset)
    filtered_rules_display["consequents"] = filtered_rules_display["consequents"].apply(clean_itemset)

    st.dataframe(filtered_rules_display[display_cols])

    # --- Dataset 2 : top 10 par lift ---
    st.subheader("🏆 Top 10 règles par Lift")

    top_rules = rules.sort_values(
        by="lift",
        ascending=False
    ).head(10)

    top_rules_display = top_rules.copy()
    top_rules_display["antecedents"] = top_rules_display["antecedents"].apply(clean_itemset)
    top_rules_display["consequents"] = top_rules_display["consequents"].apply(clean_itemset)

    st.dataframe(top_rules_display[display_cols])

# ==========================================================
#PAGE FP-GROWTH
# ==========================================================
elif page == "FP-Growth":

    st.title("🚀 Algorithme FP-Growth")

    st.metric(
        "Itemsets frequents",
        103
    )

    st.metric(
        "Regles generees",
        94
    )

    rules = pd.read_csv("results/fp_rules.csv")

    display_cols = [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift",
        "leverage",
        "conviction"
    ]

    # --- Dataset 1 : filtrage par lift / confidence ---
    st.subheader("🎛️ Filtrer les règles")

    lift_min = st.slider(
        "Lift minimum",
        1.0,
        3.0,
        1.5,
        key="fp_lift"
    )

    confidence_min = st.slider(
        "Confidence minimum",
        0.0,
        1.0,
        0.2,
        key="fp_confidence"
    )

    filtered_rules = rules[
        (rules["lift"] >= lift_min)
        & (rules["confidence"] >= confidence_min)
    ]

    filtered_rules_display = filtered_rules.copy()
    filtered_rules_display["antecedents"] = filtered_rules_display["antecedents"].apply(clean_itemset)
    filtered_rules_display["consequents"] = filtered_rules_display["consequents"].apply(clean_itemset)

    st.dataframe(filtered_rules_display[display_cols])

    # --- Dataset 2 : top 10 par lift ---
    st.subheader("🏆 Top 10 règles par Lift")

    top_rules = rules.sort_values(
        by="lift",
        ascending=False
    ).head(10)

    top_rules_display = top_rules.copy()
    top_rules_display["antecedents"] = top_rules_display["antecedents"].apply(clean_itemset)
    top_rules_display["consequents"] = top_rules_display["consequents"].apply(clean_itemset)

    st.dataframe(top_rules_display[display_cols])

# ==========================================================
#PAGE COMPARAISON
# ==========================================================
elif page == "Comparaison":

    st.title("⚖️ Comparaison")

    comparaison = pd.DataFrame({
        "Algorithme": [
            "Apriori",
            "FP-Growth"
        ],
        "Temps": [
            0.119,
            1.025
        ]
    })

    st.dataframe(
        comparaison
    )

    # --- Comparaison des temps d'exécution (Plotly) ---
    fig_temps = px.bar(
        comparaison,
        x="Algorithme",
        y="Temps",
        color="Algorithme",
        text="Temps",
        labels={"Temps": "Temps d'exécution (secondes)"},
        title="Comparaison des temps d'exécution"
    )

    fig_temps.update_traces(texttemplate="%{text:.3f}s", textposition="outside")
    fig_temps.update_layout(showlegend=False)

    st.plotly_chart(fig_temps, use_container_width=True)

    # --- Heatmap des associations (Plotly) ---
    rules = pd.read_csv("results/rules.csv")

    # Garder uniquement les règles simples (1 antécédent, 1 conséquent) pour une matrice lisible
    rules_single = rules[
        rules["antecedents"].apply(lambda x: str(x).count("'") == 2) &
        rules["consequents"].apply(lambda x: str(x).count("'") == 2)
    ].copy()

    rules_single["antecedent_clean"] = rules_single["antecedents"].apply(clean_itemset)
    rules_single["consequent_clean"] = rules_single["consequents"].apply(clean_itemset)

    # Limiter aux produits les plus fréquents pour garder une heatmap lisible
    top_products = pd.concat([
        rules_single["antecedent_clean"],
        rules_single["consequent_clean"]
    ]).value_counts().head(15).index.tolist()

    heatmap_data = rules_single[
        rules_single["antecedent_clean"].isin(top_products)
        & rules_single["consequent_clean"].isin(top_products)
    ]

    pivot = heatmap_data.pivot_table(
        index="antecedent_clean",
        columns="consequent_clean",
        values="lift",
        aggfunc="mean"
    )

    fig_heatmap = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn",
        labels=dict(x="Conséquent", y="Antécédent", color="Lift"),
        title="Heatmap des associations (Lift)",
        text_auto=".2f"
    )

    fig_heatmap.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig_heatmap, use_container_width=True)
    with st.expander("💡 Voir l'interprétation clé de ce graphique"):
        st.markdown("""
        📌 Interprétation
    *   La heatmap permet d'identifier l'intensite de la relation entre un produit achete (Antécédent) 
        et le produit suivant (Conséquent).

    *   Les couples Spaghetti–Ground Beef
        et Olive Oil–Spaghetti présentent
        les valeurs de Lift les plus élevées.

    *    Ces associations peuvent être exploitées
        pour des stratégies de cross-selling.
    """)
  
    st.image(
        "images/reseau_associations_produits.png"
    )
    with st.expander("💡 Voir l'interprétation clé de ce graphique"):
        st.markdown("""
      Ce graphe modelise la structure globale des comportements d'achat et segmente visuellement les profils de paniers.
                    
    📌 Interpretation 
    *   On observe une forte structure interconnectee autour de l'axe mineral water, soup, ground beef, olive oil et spaghetti (qui mene aussi aux tomatoes).
           
    *   Mineral water agit comme un produit pivot (commun a beaucoup de paniers de repas), 
            tandis que le sous-groupe boeuf/huile d'olive/spaghetti/tomatoes represente le profil type du repas familial ou italien
    *   Les communautes isolees (Paniers specifiques):
            Le duo frozen vegetables - Milk : indique un profil d'achat de produits de base du quotidien / stockage
            Le duo eggs - burgers : represente un comportement d'achat oriente restauration rapide / fast-food a la maison ou petit-dejeuner proteine
  
             """)

    st.image(
        "images/Support_VS_Confidence.png"
    )
    with st.expander("💡 Voir l'interprétation clé de ce graphique"):
        st.markdown("""
    *    Le Scatter plot offre vu globale de la qualite et de la performance de toutes les regles extraites.
                    
    📌 Interpretation              
    *   Règles à fort volume (À droite) : Quelques points se situent à un support élevé (~ 0.06). Ce sont les combinaisons de produits les plus courantes,
        mais leur couleur violette/bleue (Lift plus bas) indique que cette association est en partie due à la forte popularité individuelle de ces produits.
            
    *   Règles pépites (Points clairs / Jaunes) : Situées à un support modéré (~ 0.025 - 0.04) mais avec une confiance élevée (> 35%) et un Lift maximal (> 2.0). 
        Ce sont les règles les plus prédictives et les plus rentables à exploiter pour des campagnes marketing ciblées.           
        """)
# ==========================================================
#PAGE ANALYSE PRODUIT
# ==========================================================
elif page == "Analyse Produit":

    st.title(
        "🔎 Analyse Produit"
    )

    st.subheader(
        f"Produit sélectionné : {selected_product}"
    )
    #Charger les regles Apriori. 
    rules = pd.read_csv(
        "results/rules.csv"
    )

    #Chercher les associations du produit. 
    filtered_rules = rules[
        rules["antecedents"]
        .str.contains(
            selected_product,
            case=False,
            na=False
        )
    ]

    #Trier par Lift
    filtered_rules = filtered_rules.sort_values(
        by="lift",
        ascending=False
    )

    #Afficher les résultats
    st.subheader(
        "Top associations"
    )

    filtered_rules_display = filtered_rules.head(10).copy()
    filtered_rules_display["antecedents"] = filtered_rules_display["antecedents"].apply(clean_itemset)
    filtered_rules_display["consequents"] = filtered_rules_display["consequents"].apply(clean_itemset)

    st.dataframe(
        filtered_rules_display
    )

    # --- Graphique interactif Plotly ---
    top_rules = filtered_rules.head(10).copy()
    top_rules["produit_associe"] = top_rules["consequents"].apply(clean_itemset)

    if len(top_rules) > 0:
        fig = px.bar(
            top_rules.sort_values("lift"),
            x="lift",
            y="produit_associe",
            orientation="h",
            color="lift",
            color_continuous_scale="Blues",
            hover_data={
                "confidence": ":.2%",
                "support": ":.3%",
                "lift": ":.2f",
                "produit_associe": False
            },
            labels={"lift": "Lift", "produit_associe": "Produit associé"},
            title=f"Produits associés à {selected_product}"
        )

        fig.update_layout(
            yaxis_title=None,
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # --- Insight métier avec tranches de lift ---
    if len(filtered_rules) > 0:

        best_rule = filtered_rules.iloc[0]

        consequent = clean_itemset(best_rule["consequents"])
        lift = round(best_rule["lift"], 2)
        confidence = round(best_rule["confidence"] * 100, 2)
        support = round(best_rule["support"] * 100, 3)

        if lift > 2.5:
            st.success(f"""
            📌 Insight métier — Association TRÈS FORTE

            **{selected_product}** → **{consequent}** (Lift = {lift})

            Ces deux produits sont achetés ensemble bien plus souvent que le hasard
            ne le prédirait. C'est l'une des associations les plus fiables du dataset.

            Confidence : {confidence} % — Support : {support} %

            Recommandations :
            ✓ Pack promotionnel dédié (bundle)
            ✓ Placement côte à côte en rayon prioritaire
            ✓ Mettre en avant dans les recommandations produit du site
            """)

        elif lift > 2:
            st.success(f"""
            📌 Insight métier — Association forte

            **{selected_product}** → **{consequent}** (Lift = {lift})

            Confidence : {confidence} % — Support : {support} %

            Recommandations :
            ✓ Cross-selling actif (bannière, suggestion en caisse)
            ✓ Promotion groupée occasionnelle
            """)

        elif lift > 1.5:
            st.success(f"""
            📌 Insight métier — Association modérée

            **{selected_product}** → **{consequent}** (Lift = {lift})

            Confidence : {confidence} % — Support : {support} %

            Recommandations :
            ✓ Suggestion produit lors du passage en caisse
            ✓ À surveiller pour un futur pack promotionnel
            """)

        elif lift > 1:
            st.info(f"""
            📌 Insight métier — Association faible

            **{selected_product}** → **{consequent}** (Lift = {lift})

            Le lien existe mais reste léger. Pas suffisant pour justifier
            un investissement marketing important à lui seul.

            Confidence : {confidence} % — Support : {support} %

            Recommandations :
            ✓ Surveiller l'évolution dans le temps
            ✓ Combiner avec d'autres règles plus fortes avant d'agir
            """)

        elif lift == 1:
            st.warning(f"""
            📌 Insight métier — Indépendance statistique

            **{selected_product}** et **{consequent}** sont achetés indépendamment
            l'un de l'autre (Lift = 1).

            Confidence : {confidence} % — Support : {support} %

            Recommandations :
            ⚠ Pas de cross-selling pertinent ici
            ⚠ Chercher d'autres produits associés avec un Lift plus élevé
            """)

        elif lift > 0:
            st.error(f"""
            📌 Insight métier — Association négative

            **{selected_product}** et **{consequent}** sont achetés
            *moins* souvent ensemble que prévu par le hasard (Lift = {lift}).

            Confidence : {confidence} % — Support : {support} %

            Recommandations :
            ✗ Éviter la promotion croisée
            ✗ Ce sont potentiellement des produits substituts
            """)

        else:  # cas défensif, ne devrait pas arriver
            st.info(f"""
            📌 Donnée insuffisante ou invalide pour {selected_product} → {consequent}
            (Lift = {lift}).
            """)

    else:
        st.info(f"Aucune règle d'association trouvée pour **{selected_product}**.")


# ==========================================================
# PAGE RECOMMANDATIONS BUSINESS
# ==========================================================
elif page == "Recommandations":

    st.title("💼 Recommandations Business")

    # ==========================
    # KPI BUSINESS
    # ==========================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Actions proposées",
        "6"
    )

    col2.metric(
        "Impact élevé",
        "3"
    )

    col3.metric(
        "Quick Wins",
        "2"
    )

    st.markdown("""
    <div class="custom-card">

    Les règles d'association identifiées par Apriori et FP-Growth
    ont été transformées en recommandations métier exploitables.

    L'objectif est d'aider les décideurs à augmenter les ventes,
    optimiser le merchandising et améliorer les performances
    commerciales du magasin.

    </div>
    """, unsafe_allow_html=True)

    # ==========================
    # ONGLETS
    # ==========================

    tab1, tab2, tab3, tab4 = st.tabs([
        "🛍️ Cross-selling",
        "🏪 Merchandising",
        "🎁 Packs & Promotions",
        "📈 Plan d'action"
    ])

    # ==========================
    # DONNEES RECOMMANDATIONS
    # ==========================

    recommendations = {

        "cross_selling": [

            {
                "title": "Spaghetti → Ground Beef",
                "impact": "Élevé",
                "effort": "Faible",
                "lift": 2.29,
                "confidence": "22.5 %",
                "action": """
                Suggestion automatique en caisse
                et sur le site e-commerce lors de l'ajout
                de spaghetti au panier.
                """
            },

            {
                "title": "Olive Oil → Spaghetti",
                "impact": "Moyen",
                "effort": "Faible",
                "lift": 2.00,
                "confidence": "34.8 %",
                "action": """
                Mise en place d'un encart
                « Souvent achetés ensemble »
                sur les fiches produits.
                """
            }
        ],

        "merchandising": [

            {
                "title": "Espace Cuisine Italienne",
                "impact": "Moyen",
                "effort": "Moyen",
                "lift": 2.29,
                "confidence": "22.5 %",
                "action": """
                Regrouper Spaghetti,
                Ground Beef,
                Olive Oil
                et Tomatoes dans un espace thématique.
                """
            },

            {
                "title": "Rayon Petit-déjeuner / Snacking",
                "impact": "Moyen",
                "effort": "Faible",
                "lift": 1.84,
                "confidence": "33.0 %",
                "action": """
                Rapprocher Eggs et Burgers
                afin de favoriser les achats combinés.
                """
            }
        ],

        "packs": [

            {
                "title": "Pack Burger Maison",
                "impact": "Élevé",
                "effort": "Moyen",
                "lift": 1.84,
                "confidence": "33.0 %",
                "action": """
                Création d'un bundle
                Burgers + Eggs + Condiments
                avec mise en avant le week-end.
                """
            },

            {
                "title": "Pack Pâtes du Chef",
                "impact": "Moyen",
                "effort": "Moyen",
                "lift": 2.29,
                "confidence": "22.5 %",
                "action": """
                Création d'un bundle
                Spaghetti + Ground Beef + Olive Oil
                avec réduction promotionnelle.
                """
            }
        ]
    }

    # ==========================
    # COULEURS
    # ==========================

    impact_color = {
        "Élevé": "#065f46",
        "Moyen": "#78350f",
        "Faible": "#374151"
    }

    # ==========================
    # FONCTION CARTE
    # ==========================

    def render_card(rec):

        st.markdown(f"""
        <div class="business-card"
        style="background: linear-gradient(
        135deg,
        {impact_color[rec['impact']]},
        #1e293b
        );">

        <h3>{rec['title']}</h3>

        <p>{rec['action']}</p>

        <hr>

        <b>Lift :</b> {rec['lift']}<br>

        <b>Confidence :</b> {rec['confidence']}<br>

        <b>Impact :</b> {rec['impact']}<br>

        <b>Effort :</b> {rec['effort']}

        </div>
        """, unsafe_allow_html=True)

    # ==========================
    # ONGLET CROSS-SELLING
    # ==========================

    with tab1:

        st.subheader(
            "🛍️ Opportunités de Cross-Selling"
        )

        for rec in recommendations["cross_selling"]:
            render_card(rec)

        st.info("""
        📌 Interprétation

        Les règles présentant les Lift les plus élevés
        peuvent être utilisées pour recommander automatiquement
        des produits complémentaires.

        L'objectif est d'augmenter le panier moyen
        sans modifier significativement le comportement d'achat.
        """)

    # ==========================
    # ONGLET MERCHANDISING
    # ==========================

    with tab2:

        st.subheader(
            "🏪 Optimisation du Merchandising"
        )

        for rec in recommendations["merchandising"]:
            render_card(rec)

        st.info("""
        📌 Interprétation

        Les produits fréquemment achetés ensemble
        devraient être positionnés à proximité.

        Cette stratégie réduit l'effort du client
        et augmente la probabilité d'achats additionnels.
        """)

    # ==========================
    # ONGLET PACKS
    # ==========================

    with tab3:

        st.subheader(
            "🎁 Packs et Promotions"
        )

        for rec in recommendations["packs"]:
            render_card(rec)

        st.info("""
        📌 Interprétation

        Les associations fortes identifiées
        constituent d'excellents candidats
        pour la création de bundles promotionnels.

        Cette approche permet d'augmenter
        les ventes croisées et la valeur du panier.
        """)

    # ==========================
    # ONGLET PLAN D'ACTION
    # ==========================

    with tab4:

        st.subheader(
            "🎯 Matrice Impact / Effort"
        )

        impact_effort = pd.DataFrame({

            "Action": [

                "Cross-selling Spaghetti",

                "Pack Burger Maison",

                "Pack Pâtes du Chef",

                "Cuisine Italienne",

                "Réorganisation rayon"

            ],

            "Impact": [

                9,
                8,
                7,
                6,
                5

            ],

            "Effort": [

                2,
                5,
                4,
                7,
                8

            ]
        })

        fig = px.scatter(
            impact_effort,
            x="Effort",
            y="Impact",
            text="Action",
            size="Impact",
            title="Priorisation des actions commerciales"
        )

        fig.update_traces(
            textposition="top center"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("""
        <div class="result-card">

        <h3>🗓️ Priorisation suggérée</h3>

        <b>Court terme (0-1 mois)</b>

        <ul>
        <li>Cross-selling Spaghetti → Ground Beef</li>
        <li>Suggestion automatique de produits</li>
        </ul>

        <b>Moyen terme (1-3 mois)</b>

        <ul>
        <li>Pack Burger Maison</li>
        <li>Pack Pâtes du Chef</li>
        </ul>

        <b>Long terme (3+ mois)</b>

        <ul>
        <li>Création d'un espace Cuisine Italienne</li>
        <li>Réorganisation des rayons</li>
        </ul>

        </div>
        """, unsafe_allow_html=True)

        st.info("""
        📌 Méthode de priorisation

        L'impact est estimé à partir
        des valeurs de Lift et de Confidence.

        L'effort dépend des ressources
        nécessaires à la mise en œuvre
        de chaque action commerciale.
        """)

        st.markdown("""
        <div class="custom-card">

        <h3>💰 Bénéfices attendus</h3>

        <ul>

        <li>Augmentation du panier moyen</li>

        <li>Amélioration du cross-selling</li>

        <li>Hausse du chiffre d'affaires</li>

        <li>Optimisation du merchandising</li>

        <li>Amélioration de l'expérience client</li>

        <li>Valorisation des données transactionnelles</li>

        </ul>

        </div>
        """, unsafe_allow_html=True)