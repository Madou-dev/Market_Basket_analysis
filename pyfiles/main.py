##############################################
# MARKET BASKET ANALYSIS - Analyse des regles d'association
# Projet de certification GOMYCODE
##############################################

##############################################
# IMPORTATION DES BIBLIOTHEQUES
##############################################
import pandas as pd     #Bibliotheque pour manipuler les donnees
import numpy as np      #Bibliotheque pour faire des calculs
import matplotlib.pyplot as plt     #Bibliotheques pour des graphiques statiques
import seaborn as sns
import plotly_express as px
from collections import Counter     #permet de compter automatiquement les occurences
from mlxtend.preprocessing import TransactionEncoder        #sert a transformer une liste de transactions en une matrice booleenne
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules     #qui prend les itemsets fréquents trouvés par Apriori et génère automatiquement des règles.
import time
from mlxtend.frequent_patterns import fpgrowth
import networkx as nx       #Cette bibliothèque permet de créer et manipuler des graphes.

##############################################
# Importation du dataset
##############################################
df = pd.read_csv('data/Market_Basket_Optimisation.csv', header=None)

############################################## 
# Affichage des données (exploration rapide du dataset)
##############################################
print(df.head())                # Apercu des 5 premieres lignes (paniers)
print(df.shape)                 # Dimensions du dataset (lignes, colonnes)
print(df.info())                # Types de donnees et valeurs non nulles par colonne
print(df.describe())            # Statistiques descriptives (peu utile ici car donnees textuelles)
print(df.isnull().sum())        # Nombre de valeurs manquantes par colonne (paniers plus petits que 20 produits)
print(df.duplicated().sum())    # Nombre de lignes (transactions) strictement identiques

#Nombre de transaction
nb_transaction = df.shape[0]    # Chaque ligne = un panier/une transaction
print(nb_transaction)

nb_colonnes = df.shape[1]
print(nb_colonnes)      #ce qui signifie que chaque panier peut contenir jusqu'a 20 produits

##############################################
# Combien de produits sont vendus dans le magasin?
##############################################
all_products = []
for row in df.values:
    for item in row:
        if pd.notna(item):          # On ignore les cases vides (NaN) des paniers plus petits
            all_products.append(item)
#Combien de produits ont ete achetes au total
print("Le nombre total de produit achetes dans le magasin : ",len(all_products))

#Combien de produits uniques
unique_products = set(all_products)    # set() supprime automatiquement les doublons

#Compter les produits uniques
print("Nombre de produits uniques : ",len(unique_products))

##############################################
# Trouver les produits les plus vendus
##############################################
products_counts = Counter(all_products) #compter le nombre d'occurrences de chaque produit

#Top 20 des produits les plus vendus
top20_products = products_counts.most_common(20)    #most_common(20) retourne les 20 produits les plus fréquents.
top20_products_df = pd.DataFrame(
    top20_products,
    columns=['Produit','Frequence']
)
print(top20_products_df)

#Top 20 des produits les plus vendus 
fig = px.bar(top20_products_df, x='Produit', y='Frequence', title='Top 20 des produits les plus vendus')
fig.update_layout(xaxis_title="Produit", yaxis_title="Nombre d'achats")
fig.show()

##############################################
# Combien de produits les clients achetent-ils en moyenne
##############################################
basket_size = []
for row in df.values:
    size = pd.notna(row).sum()      # Nombre de valeurs non-NaN = taille reelle du panier
    basket_size.append(size)

print(f"Taille moyenne : {np.mean(basket_size):.2f}")
print("Taille mediane : ",np.median(basket_size))
print("Taille minimum : ",np.min(basket_size))
print("Taille maximum : ",np.max(basket_size))

##############################################
# Top 10 des produits les plus vendus en pourcentage
##############################################
top10 = products_counts.most_common(10)
products = [item[0] for item in top10]
counts = [item[1] for item in top10]
pourcentage = [
    count / len(df) * 100          # % de transactions contenant ce produit
    for count in counts
]
plt.figure(figsize=(10,6))
plt.bar(products, pourcentage)
plt.xticks(rotation=45)
plt.title("Top 10 des produits les plus vendus en pourcentage")
plt.xlabel("Produits")
plt.ylabel("Pourcentage (%)")
plt.tight_layout()
plt.show()

##############################################
# Distribution des tailles de panier
##############################################
basket_distribution = Counter(basket_size)
size = list(basket_distribution.keys())
frequencies = list(basket_distribution.values())

# plt.figure(figsize=(10,6))
# plt.bar(size, frequencies)
# plt.title("Nombre de transaction par taille de panier")
# plt.xlabel("Nombre de porduits")
# plt.ylabel("Nombre de transactions")
# plt.show()

#Distribution des tailles de panier avec plotly
fig2 = px.bar(
    x=size,
    y=frequencies,
    title="Distribution des tailles de panier",
    labels={"x": "Taille de panier", "y": "Nombre de transactions"}
)
fig2.show()
##############################################
# Transformer les donnees sous forme de transactions
##############################################
transactions = []
for row in df.values:
    basket = [item for item in row if pd.notna(item)]   # On enleve les NaN de chaque panier
    transactions.append(basket)
print("Nombre de transactions :", len(transactions))
print("Première transaction :")
print(transactions[0])

##############################################
# Encodage avec TransactionEncoder
##############################################
#Actuellement les produits sont en texte alors que Apriori et FP Growth ne comprennent pas le texte, ils attendent une matrice booleenne
te = TransactionEncoder()   #l'outil qui va apprendre tous les produits existants
te.fit(transactions)        #analyser toutes les transactions
print(len(te.columns_))     # Nombre de produits uniques appris par l'encodeur
encoded_array = te.transform(transactions)  #transforme les paniers en matrice True/False
print(encoded_array.shape)

#Convertir en DataFrame la matrice
df_encoded = pd.DataFrame(
    encoded_array,
    columns=te.columns_
)
print(df_encoded.head())                          # affichage explicite (necessaire hors notebook)
print(df_encoded.shape)
print(df_encoded.columns.duplicated().sum())       # verifie qu'il n'y a pas de colonnes produit dupliquees

##############################################
# ALGORITHME APRIORI
##############################################
start_time0 = time.time()
frequent_itemsets = apriori(
    df_encoded,     #la matrice encodee
    min_support=0.02,   #On garde les itemsets presents dans au moins 2% des transactions
    use_colnames=True
)
end_time = time.time()
apriori_time = end_time - start_time0     # temps reel mesure, reutilise plus bas dans le graphique de comparaison

print("Temps d'apriori : ",apriori_time)
print(frequent_itemsets.head())
#Combien d'itemsets frequents ?
print(
    "Le nombre d'itemsets frequents est : ",
    len(frequent_itemsets)
)

#Trier par support pour voir les produits ou combinaisons les plus frequents.
print(
    frequent_itemsets.sort_values(
        by = "support",
        ascending = False
    ).head(20)
)

##############################################
# Generer les regles d'apriori
##############################################
rules = association_rules(
    frequent_itemsets,  #resultat produit par apriori
    metric='lift',      #demander a l'algorithme d'evaluer les regles avec lift
    min_threshold=1     #On garde uniquement lift>=1;   rappel : lift = 1 pas d'association reelle, lift < 1 association negative , lift > 1 association positive, exemple lift = 2,5 signifie
                        #les porduits apparaissent ensemble 2,5 fois plus souvent que ce que le hasard laisserait prevoir
)
print("Le nombre de regles : ",len(rules))

top_rules = rules[
    [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift",
        "leverage",
        "conviction"
    ]
].sort_values(
    by="lift",
    ascending=False
).head(20)
print(top_rules.head(20))

##########################################
#FP-GROWTH
##########################################
start_time = time.time()

fp_itemsets = fpgrowth(
    df_encoded,
    min_support=0.02,   #Comme apriori ainsi la comparaison sera equitable
    use_colnames=True
)

end_time = time.time()
fp_time = end_time - start_time      # temps reel mesure, reutilise plus bas dans le graphique de comparaison
print("Temps FP-Growth : ", fp_time)
print("Nombre d'itemsets Fp-Growth : ",len(fp_itemsets))

print(
fp_itemsets.sort_values(
    by="support",
    ascending =False,
).head(20)
)

#Generer les regles de FP-Growth
fp_rules = association_rules(
    fp_itemsets,
    metric = "lift",
    min_threshold=1
)
print("Nombre de regles FP-Growth : ", len(fp_rules))

fp_top_rules = fp_rules[
    [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift",
        "leverage",
        "conviction"
    ]
].sort_values(
    by="lift",
    ascending=False
)
print(fp_top_rules.head(10))

##############################################
# Comparaison Apriori vs FP-Growth
##############################################
# CORRECTION: on utilise les temps reellement mesures (apriori_time, fp_time)
# et non des valeurs codees en dur, sinon le graphique ne reflete pas
# ce qui vient d'etre execute.
algorithms = ['Apriori', 'FP-Growth']
times = [apriori_time, fp_time]    # Temps d'execution reels mesures plus haut

plt.figure(figsize=(8,5))
plt.bar(algorithms, # Axe X : noms des algorithmes
        times       # Axe Y : temps d'exécution
    )
plt.title("Comparaison du temps d'execution")
plt.ylabel("Temps (secondes)")
plt.show()

##############################################
# Top 10 regles par lift
##############################################
# Trier les règles du plus grand lift au plus petit
top_rules = rules.sort_values(
    by="lift",
    ascending=False
).head(10)

# CORRECTION: construction des etiquettes en listant TOUS les produits
# d'un antecedent/consequent (et pas seulement le premier via list(a)[0],
# ce qui masquait l'info pour les regles multi-produits).
labels = [
    f"{', '.join(sorted(a))} → {', '.join(sorted(c))}"
    for a,c in zip(
        top_rules['antecedents'],
        top_rules['consequents']
    )
]
plt.figure(figsize=(12,6))

plt.barh(labels,        # Axe Y : noms des règles
          top_rules["lift"] # Axe X : valeurs du lift
    )

plt.title("Top 10 règles d'association par Lift")
plt.xlabel("Lift")
plt.tight_layout()
plt.show()

##############################################
# Heatmap des associations
##############################################
# On garde les 20 règles ayant le plus grand lift
top_rules = rules.sort_values(
    by="lift",
    ascending=False
).head(20).copy()

# CORRECTION: on convertit les antecedents/consequents (frozensets) en
# chaines de caracteres triees AVANT le pivot_table. Sans ca, deux regles
# avec le meme frozenset mais un ordre d'affichage different, ou des
# collisions d'index, peuvent etre agregees silencieusement (moyenne).
top_rules["antecedents_str"] = top_rules["antecedents"].apply(lambda x: ", ".join(sorted(x)))
top_rules["consequents_str"] = top_rules["consequents"].apply(lambda x: ", ".join(sorted(x)))

heatmap_data = pd.pivot_table(
    top_rules,
    values="lift",              # Valeur à afficher
    index="antecedents_str",    # Lignes
    columns="consequents_str"   # Colonnes
)
plt.figure(figsize=(12,8))
sns.heatmap(
    heatmap_data,
    annot=True               # Affiche les valeurs dans les cellules
)
plt.title("Heatmap des associations")
plt.tight_layout()
plt.show()

##############################################
# Reseau de cooccurrence
##############################################
G = nx.Graph()      #On cree un graphe vide

#On trie toutes les regles par lift decroissant
top_rules_network = rules.sort_values(
     by="lift",
     ascending=False
).head(15)  #On garde seulement les 15 meilleures regles.

for _, row in top_rules_network.iterrows():
     # NB: on ne prend que le premier element de chaque cote (list(...)[0])
     # pour garder un graphe simple produit-a-produit, lisible visuellement.
     # Les regles avec antecedent/consequent multi-produits sont donc
     # simplifiees ici (choix assume pour la clarte du graphe).
     antecedent = list(row["antecedents"])[0]
     consequent = list(row["consequents"])[0]

     G.add_edge(     #On ajoute une connexion entre les deux produits
         antecedent,
         consequent,
         weight=row["lift"]      #On stocke aussi la force de l'association
     )
plt.figure(figsize=(12,8))

#calculer où placer les nœuds. Sans layout tous les produits seront empilés. Avec spring_layout, NetworkX essaie de rapprocher les produits connectés et eloigner les autres non connectés
pos = nx.spring_layout(
     G,
     seed=42     #Fixe l'aleatoire, sans seed a chaque execution les produits changent de place
)

#Dessiner le graphe
nx.draw(
     G,      #Graphe a dessiner
     pos,    #Les positions calculées par spring_layout
     with_labels=True,        #Affiche les noms des produits
     node_size=1000,           #Taille des nœuds
     node_color = "skyblue",  #Couleur des nœuds
     font_weight="bold",      #Gras des noms des produits
     font_size=10,            #Taille des noms des produits
)
plt.title("Reseau des associations de produits")
plt.show()

##############################################
# Distribution des valeurs de lift
##############################################
plt.figure(figsize=(10,6))
plt.hist(
    rules["lift"],
    bins=20
)
plt.title("Distribution des valeurs de Lift")
plt.xlabel("Lift")
plt.ylabel("Nombre de règles")
plt.show()

##############################################
# Support vs Confidence coloré par le Lift
##############################################
plt.figure(figsize=(10, 6))

# Nuage de points avec coloration selon le Lift
scatter = plt.scatter(
    rules['support'],
    rules['confidence'],
    c=rules['lift'],          # Utilise la colonne 'lift' pour la couleur
    cmap='viridis',           # Palette de couleurs (ex: 'viridis', 'plasma', 'coolwarm')
    alpha=0.8,                # Légère transparence pour mieux voir les points superposés
    edgecolors='w',           # Contour blanc autour des points pour les détacher
    linewidths=0.5
)

# Ajout de la barre de couleur (Colorbar)
colorbar = plt.colorbar(scatter)
colorbar.set_label('Lift')   # Titre de la barre de couleur

# Titres et labels
plt.title("Support VS Confidence (coloré par le Lift)", fontsize=14, fontweight='bold')
plt.xlabel("Support", fontsize=12)
plt.ylabel("Confidence", fontsize=12)

# Optionnel : ajouter une grille discrète en arrière-plan
plt.grid(True, linestyle='--', alpha=0.5)

plt.show()

#Sauvegarder mes resultats
rules.to_csv("../results/rules.csv", index=False)
rules.to_csv("../results/fp_rules.csv", index=False)
