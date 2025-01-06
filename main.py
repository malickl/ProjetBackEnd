from fastapi import FastAPI
from typing import Optional
from pymongo import MongoClient
import uvicorn
import datetime

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["ecommerce"]

##################################################
#  FONCTION UTILE POUR CONSTRUIRE LE MATCH DATE  #
##################################################

def build_date_match_clause(date_debut: Optional[str], date_fin: Optional[str]):
    """
    Construit un match_clause pour filtrer Orders selon l'intervalle [date_debut, date_fin].
    Les dates sont en format 'YYYY-MM-DD'. Retourne un dict qu'on pourra insérer dans le pipeline.
    """
    if date_debut and date_fin:
        # Convertir en datetime
        d_debut = datetime.datetime.fromisoformat(date_debut)
        d_fin = datetime.datetime.fromisoformat(date_fin)
        return {
            "Order Date": {
                "$gte": d_debut,
                "$lte": d_fin
            }
        }
    return {}


##################################
#          PAGE CLIENTS          #
##################################

# 1 : Ventes par Client (avec date)
@app.get("/kpi/ventes-par-client")
async def ventes_par_client(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Products",
                "localField": "Product ID",
                "foreignField": "Product ID",
                "as": "product_info"
            }
        },
        {
            "$lookup": {
                "from": "Customers",
                "localField": "Customer ID",
                "foreignField": "Customer ID",
                "as": "customer_info"
            }
        },
        {
            "$lookup": {
                "from": "Locations",
                "localField": "Postal Code",
                "foreignField": "Postal Code",
                "as": "location_info"
            }
        },
        {"$unwind": "$product_info"},
        {"$unwind": "$customer_info"},
        {"$unwind": "$location_info"},
        {
            "$group": {
                "_id": "$customer_info.Customer Name",
                "ventes_totales": {"$sum": "$Sales"}
            }
        },
        {"$sort": {"ventes_totales": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


# 2 : Commandes par Client (NOUVEAU KPI)
@app.get("/kpi/commandes-par-client")
async def commandes_par_client(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    """
    Compte le nombre total de *lignes* de commande par client
    OU de commandes distinctes, si tu utilises l'Order ID (adaptation possible).
    Ici, on fait un group par "Customer Name" et on somme +1 par ligne.
    """
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Customers",
                "localField": "Customer ID",
                "foreignField": "Customer ID",
                "as": "info_client"
            }
        },
        {"$unwind": "$info_client"},
        # Si tu veux compter distinctement les "Order ID", fais:
        # {
        #   "$group": {
        #       "_id": {
        #           "client": "$info_client.Customer Name",
        #           "order_id": "$Order ID"
        #       }
        #   }
        # },
        # {
        #   "$group": {
        #       "_id": "$_id.client",
        #       "nombre_commandes": {"$sum": 1}
        #   }
        # },
        # Sinon, juste par ligne:
        {
            "$group": {
                "_id": "$info_client.Customer Name",
                "nombre_commandes": {"$sum": 1}
            }
        },
        {"$sort": {"nombre_commandes": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


# 3 : Panier Moyen par Client (avec date)
@app.get("/kpi/panier-moyen-par-client")
async def panier_moyen_par_client(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Customers",
                "localField": "Customer ID",
                "foreignField": "Customer ID",
                "as": "info_client"
            }
        },
        {"$unwind": "$info_client"},
        {
            "$group": {
                "_id": "$info_client.Customer Name",
                "panier_moyen": {"$avg": "$Sales"}
            }
        },
        {"$sort": {"panier_moyen": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


# 4 : Clients par Profit
@app.get("/kpi/clients-par-profit")
async def clients_par_profit(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Customers",
                "localField": "Customer ID",
                "foreignField": "Customer ID",
                "as": "info_client"
            }
        },
        {"$unwind": "$info_client"},
        {
            "$group": {
                "_id": "$info_client.Customer Name",
                "profit_total": {"$sum": "$Profit"}
            }
        },
        {"$sort": {"profit_total": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


# 5 : Quantité par Client
@app.get("/kpi/quantite-par-client")
async def quantite_par_client(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Customers",
                "localField": "Customer ID",
                "foreignField": "Customer ID",
                "as": "info_client"
            }
        },
        {"$unwind": "$info_client"},
        {
            "$group": {
                "_id": "$info_client.Customer Name",
                "quantite_totale": {"$sum": "$Quantity"}
            }
        },
        {"$sort": {"quantite_totale": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


##################################
#       PAGE COMMANDES           #
##################################

# 6 : Produits par Quantité Vendue
@app.get("/kpi/produits-par-quantite")
async def produits_par_quantite(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Products",
                "localField": "Product ID",
                "foreignField": "Product ID",
                "as": "product_info"
            }
        },
        {"$unwind": "$product_info"},
        {
            "$group": {
                "_id": "$product_info.Product Name",
                "quantite_vendue": {"$sum": "$Quantity"}
            }
        },
        {"$sort": {"quantite_vendue": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


# 7 : Profit par Région
@app.get("/kpi/profit-par-region")
async def profit_par_region(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Locations",
                "localField": "Postal Code",
                "foreignField": "Postal Code",
                "as": "location_info"
            }
        },
        {"$unwind": "$location_info"},
        {
            "$group": {
                "_id": "$location_info.Region",
                "profit_total": {"$sum": "$Profit"}
            }
        },
        {"$sort": {"profit_total": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


# 8 : Catégories plus Rentables
@app.get("/kpi/categories-plus-rentables")
async def categories_plus_rentables(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Products",
                "localField": "Product ID",
                "foreignField": "Product ID",
                "as": "info_produit"
            }
        },
        {"$unwind": "$info_produit"},
        {
            "$group": {
                "_id": "$info_produit.Category",
                "profit_total": {"$sum": "$Profit"}
            }
        },
        {"$sort": {"profit_total": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


# 9 : Sous-Catégories par Ventes
@app.get("/kpi/sous-categories-par-ventes")
async def sous_categories_par_ventes(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Products",
                "localField": "Product ID",
                "foreignField": "Product ID",
                "as": "info_produit"
            }
        },
        {"$unwind": "$info_produit"},
        {
            "$group": {
                "_id": "$info_produit.Sub-Category",
                "ventes_totales": {"$sum": "$Sales"}
            }
        },
        {"$sort": {"ventes_totales": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


# 10 : Produits - Remise Moyenne
@app.get("/kpi/produits-remise-moyenne")
async def produits_remise_moyenne(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$lookup": {
                "from": "Products",
                "localField": "Product ID",
                "foreignField": "Product ID",
                "as": "info_produit"
            }
        },
        {"$unwind": "$info_produit"},
        {
            "$group": {
                "_id": "$info_produit.Product Name",
                "remise_moyenne": {"$avg": "$Discount"}
            }
        },
        {"$sort": {"remise_moyenne": -1}}
    ]
    result = list(db.Orders.aggregate(pipeline))
    return {"data": result}


##################################
# PAGE PERFORMANCE GLOBALE
##################################

@app.get("/kpi/ventes-globales")
async def ventes_globales(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$group": {
                "_id": None,
                "ventes_globales": {"$sum": "$Sales"}
            }
        }
    ]
    data = list(db.Orders.aggregate(pipeline))
    return {"data": data}


@app.get("/kpi/nombre-commandes-global")
async def nombre_commandes_global(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$group": {
                "_id": None,
                "total_commandes": {"$sum": 1}
            }
        }
    ]
    data = list(db.Orders.aggregate(pipeline))
    return {"data": data}


@app.get("/kpi/nombre-produits-vendus")
async def nombre_produits_vendus(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$group": {
                "_id": None,
                "quantite_totale_vendue": {"$sum": "$Quantity"}
            }
        }
    ]
    data = list(db.Orders.aggregate(pipeline))
    return {"data": data}


@app.get("/kpi/profit-global")
async def profit_global(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$group": {
                "_id": None,
                "profit_total": {"$sum": "$Profit"}
            }
        }
    ]
    data = list(db.Orders.aggregate(pipeline))
    return {"data": data}


@app.get("/kpi/remise-moyenne-globale")
async def remise_moyenne_globale(date_debut: Optional[str] = None, date_fin: Optional[str] = None):
    pipeline = []
    match_clause = build_date_match_clause(date_debut, date_fin)
    if match_clause:
        pipeline.append({"$match": match_clause})

    pipeline += [
        {
            "$group": {
                "_id": None,
                "remise_globale": {"$avg": "$Discount"}
            }
        }
    ]
    data = list(db.Orders.aggregate(pipeline))
    return {"data": data}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
