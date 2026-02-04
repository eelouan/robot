"""
Module de traitement EGO.
Gère le workflow complet EGO : envoi, réception, préparation et expédition.
"""

import os
import logging
import time
from ego.connect import ego_init, ego_connect
from ego.to_order import (
    simple_recip,
    addressing_char_reception,
    addressing_mission_reception
)
from ego.ordre_de_sortie import create_ordre_de_sortie
from ego.preparation import valid_preparation
from ego.expedition import expedition
from ego.connect import pda_connect
from vtom.wms import vtom_envoi_commande, vtom_traitement_reception_commande
from vtom.wms_jour import (
    vtom_traitement_commande_rbr,
    vtom_prepare,
    vtom_traitement_commande_epo,
    vtom_traitement_commande_shi
)
from ego.function import sort_ego
from config.img import load_lobby


def process_ego(desktop, browser, orders, to_order):
    """
    Traite le workflow EGO complet.
    
    Args:
        desktop: Instance du desktop automation
        browser: Instance du navigateur
        orders: Liste des commandes créées (tuples products, num_ticket)
        to_order: Dictionnaire des commandes fournisseurs (peut être vide)
    """
    print("\n🏭 TRAITEMENT EGO")
    print("="*80)
    
    try:
        
        # Étape 2 : Connexion EGO
        _connect_to_ego(desktop)
        
        # Étape 3 : Réception des commandes fournisseurs (si nécessaire)
        if to_order:
            _process_supplier_reception(desktop, to_order)
        
        # Étape 4 : Préparation des ordres de sortie
        ego_order = sort_ego(orders)
        array_num = _prepare_orders(desktop, ego_order)
        
        # Étape 5 : Expédition
        _ship_orders(desktop, browser, ego_order, array_num)
        
        print("\n✅ Workflow EGO terminé")
        print("="*80 + "\n")
        
    except Exception as e:
        logging.error(f"❌ Erreur workflow EGO: {e}", exc_info=True)
        raise


def _connect_to_ego(desktop):
    """
    Initialise et connecte à EGO.
    
    Args:
        desktop: Instance du desktop automation
    """
    
    ego_init()
    ego_connect(desktop)


def _process_supplier_reception(desktop, to_order):
    """
    Traite la réception des commandes fournisseurs.
    
    Args:
        desktop: Instance du desktop automation
        to_order: Dictionnaire des commandes fournisseurs
    """
    print("\n📦 Traitement réception fournisseurs...")
    
    try:
        # Réception simple
        chars = simple_recip(desktop, to_order)
        print(f"  ✓ Réception simple effectuée (chars: {chars})")
        
        # Traitement des caractères si nécessaire
        if len(chars) != 1 or chars[0] not in "crmono1":
            print("  - Adressage char réception...")
            addressing_char_reception(chars)
            
            print("  - Adressage mission réception...")
            addressing_mission_reception(chars)
        else:
            print("  ✓ Pas d'adressage nécessaire")
        
        # VTOM : Traitement RBR
        vtom_traitement_commande_rbr()
        print("  ✓ Traitement RBR effectué")
        
    except Exception as e:
        logging.error(f"Erreur réception fournisseurs: {e}")
        raise


def _prepare_orders(desktop, ego_order):
    """
    Prépare les ordres de sortie pour chaque transporteur.
    
    Args:
        desktop: Instance du desktop automation
        ego_order: Dictionnaire des commandes par transporteur
    
    Returns:
        dict: Numéros de missions par transporteur
    """
    print("\n📋 Préparation des ordres de sortie...")
    
    array_num = {'dpd': [], 'tnt': [], 'mr': []}
    
    for transport, cmd in ego_order.items():
        if not cmd:
            print(f"  ✓ Pas de commande pour {transport}")
            continue
        
        print(f"\n  🚚 {transport.upper()}")
        
        try:
            # Attente du lobby
            wait(load_lobby)
            
            # Création de l'ordre de sortie
            print(f"    - Création ordre de sortie...")
            create_ordre_de_sortie(desktop, orders=cmd)
            
            # Validation de la préparation
            print(f"    - Validation préparation...")
            array_num = valid_preparation(desktop, cmd, transport, array_num)
            
            print(f"    ✓ {len(array_num[transport])} mission(s) créée(s)")
            
        except Exception as e:
            logging.error(f"Erreur préparation {transport}: {e}")
            raise
    
    print(f"\n✅ Préparation terminée")
    print(f"  - Missions créées: {sum(len(v) for v in array_num.values())}")
    for transport, missions in array_num.items():
        if missions:
            print(f"    • {transport}: {missions}")
    
    return array_num


def _ship_orders(desktop, browser, ego_order, array_num):
    """
    Effectue l'expédition des commandes.
    
    Args:
        desktop: Instance du desktop automation
        browser: Instance du navigateur
        ego_order: Dictionnaire des commandes par transporteur
        array_num: Numéros de missions par transporteur
    """
    print("\n📦 Expédition des commandes...")
    
    try:
        # Connexion PDA
        print("  - Connexion PDA...")
        pda_connect(desktop)
        
        # Expédition
        print("  - Traitement expédition...")
        expedition(desktop, ego_order, array_num)
        print("  ✓ Expédition effectuée")
        
        # Retour page d'attente
        wait_url = r"C:\Users\adm-moreau\Documents\Robot\Robocorp\wait.html"
        browser.go_to(wait_url)
        
        # VTOM : Traitements finaux
        print("  - Traitements VTOM finaux...")
        vtom_prepare()
        vtom_traitement_commande_epo()
        vtom_traitement_commande_shi()
        print("  ✓ Traitements VTOM terminés")
        
    except Exception as e:
        logging.error(f"Erreur expédition: {e}")
        raise


def get_ego_summary(ego_order, array_num):
    """
    Génère un résumé du traitement EGO.
    
    Args:
        ego_order: Dictionnaire des commandes par transporteur
        array_num: Numéros de missions par transporteur
    
    Returns:
        dict: Statistiques du traitement EGO
    """
    summary = {
        'total_orders': 0,
        'total_missions': 0,
        'by_transport': {}
    }
    
    for transport, orders in ego_order.items():
        if not orders:
            continue
        
        order_count = len(orders)
        mission_count = len(array_num.get(transport, []))
        
        summary['total_orders'] += order_count
        summary['total_missions'] += mission_count
        
        summary['by_transport'][transport] = {
            'orders': order_count,
            'missions': mission_count,
            'mission_numbers': array_num.get(transport, [])
        }
    
    return summary


def print_ego_summary(ego_order, array_num):
    """
    Affiche un résumé formaté du traitement EGO.
    
    Args:
        ego_order: Dictionnaire des commandes par transporteur
        array_num: Numéros de missions par transporteur
    """
    summary = get_ego_summary(ego_order, array_num)
    
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DU TRAITEMENT EGO")
    print("="*80)
    
    print(f"\n📦 Total commandes: {summary['total_orders']}")
    print(f"📋 Total missions: {summary['total_missions']}")
    
    if summary['by_transport']:
        print("\n🚚 Par transporteur:")
        for transport, stats in summary['by_transport'].items():
            print(f"\n  {transport.upper()}")
            print(f"    • Commandes: {stats['orders']}")
            print(f"    • Missions: {stats['missions']}")
            if stats['mission_numbers']:
                print(f"    • Numéros: {', '.join(stats['mission_numbers'])}")
    
    print("\n" + "="*80 + "\n")


# Import de wait depuis conf
try:
    from config.img import wait
except ImportError:
    # Fallback si wait n'est pas dans conf
    def wait(image, timeout=30):
        """Fonction wait de secours."""
        import time
        time.sleep(2)
        logging.warning("Utilisation de wait() de secours - import depuis conf échoué")