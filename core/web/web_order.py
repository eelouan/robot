import re, os
import time

from dotenv import load_dotenv

from web.create import create_cart
from core.web import web_common, web_payment
from config import *

def create_order(desktop, browser, commandes, seller_mode=False):
    """
    Crée des commandes sur le site web pour tous les produits spécifiés.
    
    Args:
        desktop: Instance du desktop automation
        browser: Instance du navigateur (Selenium/Robot Framework)
        commandes: Liste des commandes à créer, chaque commande contenant:
            - is_connect: Boolean indiquant si l'utilisateur doit être connecté
            - mag: Code du magasin
            - produits: Liste des produits à commander
            - cod_mag: Code du magasin pour le tunnel d'achat
    
    Returns:
        list: Liste de tuples (infos_produits, numéro_commande) pour chaque commande créée
    """
    orders = []
    connect_before = False
    
    for commande in commandes:
        time.sleep(2)
        
        if not seller_mode:
            # Gestion de la connexion utilisateur
            connect_before = _handle_user_connection(desktop, commande, connect_before)
        
        # Changement de magasin
        web_common.change_mag(browser, commande['mag'])
        
        # Préparation des produits et détection des modes de livraison
        product_infos, delivery_modes = _prepare_products_and_delivery(browser, commande['produits'])
        
        # Passage du tunnel d'achat
        order_result = web_payment.tunnel_achat(
            desktop, 
            browser, 
            product_infos, 
            commande['is_connect'], 
            delivery_modes, 
            commande["cod_mag"],
            seller_mode=seller_mode
        )
        orders.append(order_result)
    
    return orders

def _handle_user_connection(desktop, commande, connect_before):
    """
    Gère la connexion/déconnexion de l'utilisateur selon les besoins.
    
    Args:
        desktop: Instance du desktop automation
        commande: Dictionnaire de la commande en cours
        connect_before: Boolean indiquant si l'utilisateur était connecté avant
    
    Returns:
        bool: Nouvel état de connexion
    """
    # Déconnexion si nécessaire (utilisateur connecté mais commande sans connexion)
    if connect_before and not commande['is_connect']:
        web_common.disconnect()
    
    # Connexion selon les besoins de la commande
    return web_common.connect(desktop, commande['is_connect'], connect_before)

def _prepare_products_and_delivery(browser, produits):
    """
    Prépare les informations des produits et détecte les modes de livraison nécessaires.
    
    Args:
        browser: Instance du navigateur
        produits: Liste des produits à commander
    
    Returns:
        tuple: (liste des infos produits, liste des modes de livraison)
            - product_infos: Liste des dictionnaires d'informations produits
            - delivery_modes: Liste des codes de mode de livraison (1=cac, 2=sfs, 3=mr)
    """
    product_infos = []
    delivery_modes = []
    
    # Dictionnaire pour suivre quels modes ont déjà été ajoutés
    mode_already_added = {'cac': False, 'sfs': False, 'mr': False}
    
    # Mapping des modes textuels vers les codes numériques
    mode_to_code = {
        'cac': 1,  # Click & Collect
        'sfs': 2,  # Ship From Store (domicile)
        'mr': 3    # Mondial Relay
    }
    
    for produit in produits:
        mode = produit.get("mode", "")
        
        # Ajouter le mode de livraison uniquement s'il n'a pas déjà été ajouté
        if mode in mode_to_code and not mode_already_added[mode]:
            delivery_modes.append(mode_to_code[mode])
            mode_already_added[mode] = True
        
        # Créer la commande pour ce produit sur le site
        product_info = create_cart(browser, produit, select=True)
        product_infos.append(product_info)
        
        # Retour à la page d'accueil entre chaque produit
        browser.go_to(os.getenv("pp_web_site"))
    
    return product_infos, delivery_modes
