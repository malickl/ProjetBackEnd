**Projet E-commerce Dashboard**
===============================

Ce dépôt contient un **tableau de bord** pour l'analyse d'un jeu de données e-commerce. Il repose sur **MongoDB** (base de données), **FastAPI** (API backend) et **Streamlit** (application front-end). L'objectif est de proposer une solution clé en main pour visualiser et analyser les ventes, clients, produits et performances globales d'un site e-commerce.

* * * * *

**1\. Origine du TP**
---------------------

Ce projet est issu d'un **travail pratique** (TP) visant à :

1.  Découvrir la conception d'un **backend** avec **FastAPI** et l'exploitation d'une base de données **MongoDB**.
2.  Créer un **tableau de bord** interactif grâce à **Streamlit**, permettant de manipuler et d'afficher les données de façon conviviale.
3.  Mettre en pratique la **connexion** entre une API REST et une interface utilisateur, démontrant les principes de requêtes HTTP, de pipelines d'agrégation MongoDB et de visualisations (bar charts, pie charts, KPIs, etc.).

* * * * *

**2\. Objectif du Projet**
--------------------------

-   **Analyser** rapidement les ventes, les profits, le nombre de commandes, la fidélité client, etc.
-   **Fournir** un outil de prise de décision en temps réel (filtre par dates, top N produits/clients, etc.).
-   **Développer** une architecture modulaire et évolutive (MongoDB pour la base, FastAPI pour l'API, Streamlit pour l'IHM).

* * * * *

**3\. Composition du Projet**
-----------------------------

Le projet comprend **plusieurs fichiers** principaux :

1.  **`main.py`** :

    -   Contient l'API **FastAPI**.
    -   Se connecte à MongoDB, exécute des **pipelines d'agrégation**, et expose des endpoints (ex. `/kpi/ventes-par-client`, `/kpi/ventes-globales`, etc.).
    -   Se lance via **uvicorn**.
2.  **`app.py`** :

    -   Fichier **Streamlit** contenant l'interface de visualisation.
    -   Réalise des requêtes GET vers les endpoints de l'API et affiche les résultats dans des **graphes** ou **KPIs** (grâce à **plotly**, **streamlit-lottie**, etc.).
    -   Comprend un **filtre de dates** et des onglets : "Clients", "Commandes" et "Performance Globale".
3.  **`requirements.txt`** :

    -   Liste des dépendances Python nécessaires.
4.  **Fichiers annexes** (ex. `animation.json`) :

    -   Utilisé par la librairie **streamlit_lottie** pour animer l'interface.

* * * * *

**4\. Comment le Projet a été Réalisé**
---------------------------------------

1.  **Analyse du Jeu de Données** :\
    Les données brutes (Orders, Products, Customers, Locations) ont été importées dans une base de données **MongoDB**.
2.  **Création de l'API** (fichier `main.py`) :
    -   Mise en place des **routes** (endpoints) pour calculer différents indicateurs (ventes, profit, etc.) via des **pipelines d'agrégation**.
    -   Utilisation de **`pymongo`** pour se connecter et interroger MongoDB.
    -   Configuration de **FastAPI** et **uvicorn** pour le lancement du serveur API.
3.  **Construction du Dashboard** (fichier `app.py`) :
    -   Réalisation d'une **interface Streamlit** avec onglets pour segmenter l'analyse (Clients, Commandes, Performance).
    -   Intégration d'un **slider** pour sélectionner le top N éléments à afficher et d'un **sélecteur de dates** (sidebar) pour filtrer la période d'analyse.
    -   Appels HTTP vers les routes de l'API, conversion en **DataFrame** Pandas, puis création de **visualisations** avec Plotly.

* * * * *

**5\. Installation sur une Autre Machine**
------------------------------------------

### **5.1 Cloner le dépôt Git**

bash

Copier le code

`git clone https://github.com/malickl/ProjetBackEnd.git`


### **5.2 Installer les dépendances**

Assurez-vous d'avoir **Python 3.8+** installé. Ensuite, exécutez :

bash

Copier le code

`pip install -r requirements.txt`

### **5.3 Configurer MongoDB**

1.  Installer et lancer **MongoDB** (en local ou via un service hébergé).
2.  Importer vos collections ("Orders", "Products", "Customers", "Locations") dans la base nommée **`ecommerce`**.

### **5.4 Lancer l'API FastAPI**

Dans un terminal, exécutez :

bash

Copier le code

`uvicorn main:app --host 0.0.0.0 --port 8000`

> *Par défaut, l'API sera accessible à l'adresse <http://localhost:8000>*

Vous pouvez tester la documentation interactive générée automatiquement par FastAPI en allant sur http://localhost:8000/docs.

### **5.5 Lancer l'Application Streamlit**

Dans un **nouveau terminal** :

bash

Copier le code

`streamlit run app.py`

> *L'interface Streamlit est généralement accessible à l'adresse http://localhost:8501*

Vérifiez que la configuration dans `app.py` (URL de l'API) pointe bien vers le **<http://localhost:8000>** ou l'URL adéquate si vous hébergez l'API ailleurs.

* * * * *

**6\. Fichier `requirements.txt`**
----------------------------------

Voici un **exemple** de contenu pour vos dépendances. Vous pouvez ajuster les versions si nécessaire :

txt

Copier le code

`fastapi==0.88.0
uvicorn==0.20.0
pymongo==4.2.0
requests==2.28.1
streamlit==1.13.0
pandas==1.5.0
plotly==5.10.0
streamlit-lottie==0.0.2`

* * * * *

**7\. Usage**
-------------

1.  **Sélectionner un intervalle de dates** via la sidebar.
2.  **Explorer** les onglets "Clients", "Commandes" et "Performance Globale" pour visualiser les différents indicateurs.
3.  **Ajuster** la valeur du slider (top N) pour afficher plus ou moins de produits/clients dans les graphiques.
