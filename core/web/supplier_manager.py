"""
Module de gestion des commandes fournisseurs.
Fonctions pour initialiser et traiter les commandes fournisseurs.
"""

import logging
from utils.connect_db import connect_athena_rec
from utils.request import update_eligible_yakaedi, get_supplier_order, get_order_status_num_tic
from athena.athena import (
    connect_and_open_athena,
    supplier_orders,
    get_cmd_client,
    get_supplier,
    get_code_intern
)
from vtom.wms import vtom_traitement_reception_commande


def init_supplier(orders, athena_conn):
    """
    Initialise et organise les commandes fournisseurs à partir des commandes clients.
    
    Filtre les produits selon leur état (ECD ou ACD) et les regroupe par fournisseur
    pour faciliter le traitement des commandes fournisseurs.
    
    Args:
        orders: Liste de tuples (products, num_ticket) où :
            - products: Liste de dictionnaires contenant les infos produits avec 'qty'
            - num_ticket: Numéro du ticket de commande
        athena_conn: Connexion à la base de données Athena
    
    Returns:
        dict: Dictionnaire organisé par fournisseur, format :
            {
                'supplier_id': [
                    {
                        'cmd': commande_client,
                        'num_tic': numéro_ticket,
                        'code8': code_interne,
                        'state': état_produit,
                        'type': 'mono',
                        'qty': quantité
                    },
                    ...
                ]
            }
    """
    # États de produits nécessitant une commande fournisseur
    STATE_TO_ORDER = {'ECD', 'ACD'}  # Utilisation d'un set pour performance O(1)
    
    to_order = {}
    
    for products, num_ticket in orders:
        # Récupération des états de tous les produits du ticket
        states = get_order_status_num_tic(athena_conn, num_ticket)
        
        # Skip si aucun produit n'est dans un état à commander
        if not any(state in STATE_TO_ORDER for state in states):
            continue
        
        # Traitement de chaque produit
        for index, product in enumerate(products):
            # Vérifier si ce produit spécifique nécessite une commande
            current_state = states[index]
            if current_state not in STATE_TO_ORDER:
                continue
            
            # Récupération des informations du produit
            try:
                cmd_client = get_cmd_client(athena_conn, num_ticket, index)
                supplier = get_supplier(athena_conn, cmd_client)
                code8 = get_code_intern(athena_conn, cmd_client)
            except Exception as e:
                logging.error(
                    f"Erreur récupération infos pour ticket {num_ticket}, "
                    f"index {index}: {e}"
                )
                continue
            
            # Validation des données
            if not supplier or not cmd_client:
                logging.warning(
                    f"Données manquantes pour ticket {num_ticket}, index {index}"
                )
                continue
            
            # Initialisation de la liste pour ce fournisseur si nécessaire
            if supplier not in to_order:
                to_order[supplier] = []
            
            # Ajout de la commande pour ce fournisseur
            to_order[supplier].append({
                'cmd': cmd_client,
                'num_tic': num_ticket,
                'code8': code8,
                'state': current_state,
                'type': 'mono',
                'qty': product.get('qty', 1)  # Valeur par défaut si 'qty' absent
            })
    
    # Log du résultat
    if to_order:
        print(f"\n📦 {len(to_order)} fournisseur(s) à traiter")
        for supplier, items in to_order.items():
            print(f"  - Fournisseur {supplier}: {len(items)} produit(s)")
    else:
        print("\n✓ Aucune commande fournisseur à traiter")
    
    return to_order


def process_supplier_orders(desktop, to_order, athena_conn):
    """
    Traite les commandes fournisseurs dans Athena.
    
    Args:
        desktop: Instance du desktop automation
        to_order: Dictionnaire des commandes par fournisseur
            (résultat de init_supplier)
    
    Returns:
        dict: to_order enrichi avec les numéros de commande fournisseur
    """
    print("\n🏭 Traitement des commandes fournisseurs...")
    
    # Désactivation de l'éligibilité Yakaedi
    print("  - Désactivation Yakaedi...")
    for _, products in to_order.items():
        for product in products:
            try:
                update_eligible_yakaedi(athena_conn, 0, product['num_tic'])
            except Exception as e:
                logging.error(
                    f"Erreur désactivation Yakaedi pour ticket "
                    f"{product['num_tic']}: {e}"
                )
    
    # Ouverture d'Athena et passage des commandes fournisseurs
    print("  - Ouverture Athena...")
    try:
        connect_and_open_athena(desktop)
        
        print("  - Passage des commandes...")
        supplier_orders(to_order)
        
        desktop.close_all_applications()
    except Exception as e:
        logging.error(f"Erreur passage commandes fournisseurs: {e}")
        try:
            desktop.close_all_applications()
        except:
            pass
        raise
    
    # Traitement de la réception
    print("  - Traitement réception...")
    try:
        vtom_traitement_reception_commande()
    except Exception as e:
        logging.error(f"Erreur traitement réception: {e}")
        raise
    
    # Récupération des numéros de commande fournisseur
    print("  - Récupération numéros commandes...")
    for _, products in to_order.items():
        for product in products:
            try:
                supplier_order = get_supplier_order(athena_conn, product['cmd'])
                product['supplier_order'] = supplier_order
            except Exception as e:
                logging.error(
                    f"Erreur récupération supplier_order pour "
                    f"cmd {product['cmd']}: {e}"
                )
                product['supplier_order'] = None
    
    print("✅ Commandes fournisseurs traitées\n")
    
    return to_order


def get_supplier_summary(to_order):
    """
    Génère un résumé des commandes fournisseurs.
    
    Args:
        to_order: Dictionnaire retourné par init_supplier
    
    Returns:
        dict: Résumé avec statistiques par fournisseur
    """
    summary = {}
    
    for supplier, items in to_order.items():
        total_qty = sum(item['qty'] for item in items)
        unique_products = len(set(item['code8'] for item in items))
        states = {}
        
        for item in items:
            state = item['state']
            states[state] = states.get(state, 0) + 1
        
        summary[supplier] = {
            'total_items': len(items),
            'total_quantity': total_qty,
            'unique_products': unique_products,
            'states': states,
            'tickets': list(set(item['num_tic'] for item in items))
        }
    
    return summary


def print_supplier_summary(to_order):
    """
    Affiche un résumé formaté des commandes fournisseurs.
    
    Args:
        to_order: Dictionnaire retourné par init_supplier
    """
    summary = get_supplier_summary(to_order)
    
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES COMMANDES FOURNISSEURS")
    print("="*80)
    
    for supplier, stats in summary.items():
        print(f"\n🏭 Fournisseur: {supplier}")
        print(f"  • Total articles: {stats['total_items']}")
        print(f"  • Quantité totale: {stats['total_quantity']}")
        print(f"  • Produits uniques: {stats['unique_products']}")
        print(f"  • États: {stats['states']}")
        print(f"  • Tickets: {', '.join(stats['tickets'])}")
    
    print("\n" + "="*80 + "\n")