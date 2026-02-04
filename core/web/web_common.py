"""
Utilitaires d'initialisation web et de connexion pour l'interface web du ecommerce.
Fonctions pour la récupération de données produit, vérification des libellés,
génération de rapports HTML et validation XML.
Gère la configuration du navigateur, la sélection des magasins et les flux d'authentification.
"""
import os
import time
from typing import Optional, Tuple, Any, List, Dict
from datetime import datetime

from RPA.Desktop import Desktop
from RPA.Browser.Selenium import Selenium
from dotenv import load_dotenv

from utils.utils import open_browser, update_localstorage, parse_ticket_vente, wait, click_image, find_element
from web.connect import connect_with_good_id
from config.img import *
from config.img import state as State
from config.timeouts import TimeoutConfig
from utils.Assert import Assert
from utils.request import get_web_order, get_web_order_adress, get_web_customer, get_web_order_carrier, get_web_order_carrier_address
from utils.connect_db import connect_web_pp

# Sélecteurs centralisés
class WebSelectors:
    """Sélecteurs CSS pour les éléments de l'interface web."""
    STORE_CONFIRM_BUTTON = 'css:.check-button'
    
    # Clés LocalStorage
    NOTIFICATION_MINIMIZED = 'isNotificationMinimized'
    STORE_LOCATOR_OPEN = 'storeLocatorPopinOpen'
    STORE_LOCATOR_COUNTER = 'storeLocatorPopinCounter'


# Patterns d'URL des magasins par pays
STORE_URL_PATTERNS = {
    'fr': 'magasins',
    'es': 'tiendas',
    'it': 'punti-vendita'
}


def initialize_browser(accept_cookies: bool = True) -> Tuple[Desktop, Selenium]:
    """
    Initialise les instances du navigateur et du desktop avec la configuration de l'environnement web.
    
    Args:
        accept_cookies: Indique si la popup d'acceptation des cookies doit être gérée
        
    Returns:
        Tuple contenant (instance Desktop, instance Browser)
        
    Raises:
        Exception: Si l'initialisation du navigateur échoue
    """
    desktop = Desktop()
    browser = open_browser(os.getenv("pp_web_site"))
    
    try:
        # Gère le consentement des cookies si nécessaire
        if accept_cookies:
            _handle_cookie_consent(browser)
        
        # Configure le localStorage pour supprimer les popups
        _configure_localstorage(browser)
        
        return desktop, browser
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation du navigateur: {e}")
        raise


def _handle_cookie_consent(browser: Selenium) -> None:
    """Gère la popup de consentement des cookies si présente."""
    try:
        # TODO: Remplacer la détection par image par une méthode browser
        # Devrait utiliser browser.wait_and_click_button() à la place
        from utils.utils import wait, click_image
        from config.img import accept_cookies
        
        wait(accept_cookies, confidence=0.9)
        click_image(accept_cookies, confidence=0.9)
    except Exception as e:
        print(f"Consentement cookies introuvable ou déjà accepté: {e}")


def _configure_localstorage(browser: Selenium) -> None:
    """Configure les paramètres localStorage pour supprimer les popups."""
    settings = {
        WebSelectors.NOTIFICATION_MINIMIZED: 'true',
        WebSelectors.STORE_LOCATOR_OPEN: 'true',
        WebSelectors.STORE_LOCATOR_COUNTER: '3'
    }
    
    for key, value in settings.items():
        try:
            update_localstorage(browser, key, value)
        except Exception as e:
            print(f"Attention: Échec de la configuration localStorage[{key}]: {e}")


def change_store(browser: Selenium, store_id: str) -> None:
    """
    Navigue vers un magasin spécifique et confirme la sélection.
    
    Args:
        browser: Instance du navigateur
        store_id: Identifiant du magasin
        
    Raises:
        ValueError: Si l'état/pays actuel n'est pas supporté
        Exception: Si la sélection du magasin échoue
    """
    if State not in STORE_URL_PATTERNS:
        raise ValueError(f"État pays non supporté: {State}")
    
    url_pattern = STORE_URL_PATTERNS[State]
    store_url = f"{os.getenv("pp_web_site")}{url_pattern}/{store_id}"
    
    try:
        browser.go_to(store_url)
        browser.wait_and_click_button(WebSelectors.STORE_CONFIRM_BUTTON)
        time.sleep(TimeoutConfig.SHORT_WAIT)  # Attend que la sélection du magasin soit enregistrée
    except Exception as e:
        raise Exception(f"Échec du changement vers le magasin {store_id}: {e}")


def disconnect_account(browser: Selenium) -> None:
    """
    Se déconnecte du compte actuel.
    
    Args:
        browser: Instance du navigateur
        
    Note:
        Utilise actuellement la détection par image. Devrait être migré vers les méthodes browser.
    """
    try:
        # TODO: Remplacer par browser.wait_and_click_button() quand le sélecteur sera disponible
        from utils.utils import move_image, wait, click_image
        
        move_image(account)
        wait(button_disconnect)
        click_image(button_disconnect)
    except Exception as e:
        print(f"Attention: Échec de la déconnexion: {e}")


def authenticate_user(
    desktop: Desktop,
    browser: Optional[Selenium] = None,
    use_auth0: bool = False,
    seller_mode: bool = False,
    already_connected: bool = False
) -> None:
    """
    Authentifie l'utilisateur selon le mode choisi.
    
    Args:
        desktop: Instance Desktop pour la saisie clavier
        browser: Instance Browser (optionnel, pour la navigation)
        use_auth0: Utilise le flux d'authentification Auth0
        seller_mode: Utilise les identifiants vendeur au lieu de l'utilisateur normal
        already_connected: Ignore l'authentification si déjà connecté
        
    Raises:
        ValueError: Si la combinaison de mode d'authentification est invalide
    """
    if already_connected:
        return
    
    if use_auth0:
        _authenticate_with_auth0(desktop)
    elif seller_mode:
        _authenticate_seller(desktop)


def _authenticate_with_auth0(desktop: Desktop) -> None:
    """Gère le flux d'authentification Auth0."""
    try:
        from utils.utils import click_image, wait
        
        click_image(account, confidence=0.9)
        wait(connect_auth0, confidence=0.95)
        connect_with_good_id(desktop)
    except Exception as e:
        raise Exception(f"Échec de l'authentification Auth0: {e}")


def _authenticate_seller(desktop: Desktop) -> None:
    """
    Gère l'authentification en mode vendeur avec identifiants.
    
    Note:
        Utilise PyAutoGUI pour l'interaction avec le formulaire. Devrait être migré vers les méthodes browser.
    """
    try:
        from utils.utils import just_fill
        import pyautogui
        
        time.sleep(TimeoutConfig.DEFAULT_WAIT)
        
        # Remplit le nom d'utilisateur
        username = os.getenv('pp_seller_account')
        if not username:
            raise ValueError("pp_seller_account introuvable dans l'environnement")
        just_fill(desktop, username)
        
        time.sleep(TimeoutConfig.SHORT_WAIT)
        pyautogui.press('tab')
        
        # Remplit le mot de passe
        password = os.getenv('pp_seller_passwd')
        if not password:
            raise ValueError("pp_seller_passwd introuvable dans l'environnement")
        just_fill(desktop, password)
        
        time.sleep(TimeoutConfig.SHORT_WAIT)
        pyautogui.press('enter')
        
    except Exception as e:
        raise Exception(f"Échec de l'authentification vendeur: {e}")


# Alias de rétrocompatibilité (dépréciés)
def initialize(browser=None, accept_c=True):
    """Déprécié: Utiliser initialize_browser() à la place."""
    print("Attention: initialize() est déprécié. Utiliser initialize_browser()")
    return initialize_browser(accept_c)


def change_mag(browser, mag):
    """Déprécié: Utiliser change_store() à la place."""
    print("Attention: change_mag() est déprécié. Utiliser change_store()")
    return change_store(browser, mag)


def disconnect():
    """Déprécié: Utiliser disconnect_account() à la place."""
    print("Attention: disconnect() est déprécié. Utiliser disconnect_account()")
    # Note: Nécessite le paramètre browser dans la nouvelle version
    raise NotImplementedError("disconnect_account() nécessite le paramètre browser")


def connect(desktop, connect=False, connect_before=False, seller_mode=False):
    """Déprécié: Utiliser authenticate_user() à la place."""
    print("Attention: connect() est déprécié. Utiliser authenticate_user()")
    authenticate_user(
        desktop,
        use_auth0=connect and not connect_before,
        seller_mode=seller_mode,
        already_connected=connect_before
    )

# Sélecteurs CSS centralisés
class WebProductSelectors:
    """Sélecteurs pour les éléments liés aux produits."""
    PRODUCT_REFERENCE = 'css:.main-product .main-informations'
    PRODUCT_NAME = 'css:.product-information .product-name'
    SEARCH_PRODUCT_NAME = 'css:.product-name'
    CART_PRODUCT_NAME = 'css:.text-container .name'
    ADD_TO_CART_BUTTON = 'css:#add_to_cart_add'
    CART_ITEM = 'css:.item'
    CART_ITEM_XPATH = "xpath=//div[contains(@class, 'item') and @data-reference]"
    LOADING_SPINNER = 'css:.lds-ring'


# Configuration des chemins de sortie
OUTPUT_PATHS = {
    'dev': 'recapitulatif_commande.html',
    'test': 'recapitulatif_commande.html',
    'prod': r'C:\Users\Public\Documents\Tests\6-AUTRE\recapitulatif_commande.html'
}


def get_product_code8(browser: Selenium, product: Dict[str, str]) -> str:
    """
    Récupère le code8 (référence produit) depuis la page produit.
    
    Args:
        browser: Instance du navigateur
        product: Dictionnaire contenant l'URL du produit
        
    Returns:
        Code8 (référence) du produit
        
    Raises:
        Exception: Si le code8 ne peut pas être récupéré
    """
    try:
        product_url = f"{os.getenv("pp_web_site")}{product['url']}"
        browser.go_to(product_url)
        
        # Attend que le bouton d'ajout au panier soit visible
        wait(add_cart_from_product_page)
        
        # Récupère l'attribut data-reference
        element = browser.find_element(WebProductSelectors.PRODUCT_REFERENCE)
        code8 = browser.get_element_attribute(element, 'data-reference')
        
        return code8
        
    except Exception as e:
        raise Exception(f"Échec de la récupération du code8 pour {product.get('url', 'URL inconnue')}: {e}")


def verify_product_labels(
    browser: Selenium,
    product: Dict[str, str],
    expected_label: str,
    environment_url: str
) -> None:
    """
    Vérifie que le libellé d'un produit est cohérent sur toutes les pages.
    Vérifie: page produit, résultats de recherche Algolia, et panier.
    
    Args:
        browser: Instance du navigateur
        product: Dictionnaire contenant code8 et URL du produit
        expected_label: Libellé attendu du produit
        environment_url: URL de base de l'environnement
        
    Raises:
        AssertionError: Si un des libellés ne correspond pas
    """
    labels = {}
    
    try:
        # 1. Vérification sur la page produit
        labels['product_page'] = _get_product_page_label(browser, product, environment_url)
        
        # 2. Ajout au panier pour vérifier le libellé
        _add_product_to_cart(browser)
        
        # 3. Vérification dans les résultats de recherche Algolia
        labels['search_algolia'] = _get_search_label(browser, product, environment_url)
        
        # 4. Vérification dans le panier
        labels['cart'] = _get_cart_label(browser, environment_url)
        
        # Assertions de cohérence
        Assert.assert_equals(
            labels['search_algolia'],
            expected_label,
            f"Libellé recherche Algolia: attendu '{expected_label}', obtenu '{labels['search_algolia']}'",
            'check_libelle'
        )
        
        Assert.assert_equals(
            labels['product_page'],
            expected_label,
            f"Libellé page produit: attendu '{expected_label}', obtenu '{labels['product_page']}'",
            'check_libelle'
        )
        
        Assert.assert_equals(
            labels['cart'],
            expected_label,
            f"Libellé panier: attendu '{expected_label}', obtenu '{labels['cart']}'",
            'check_libelle'
        )
        
    except Exception as e:
        raise Exception(f"Échec de la vérification des libellés pour {product.get('code8', 'code8 inconnu')}: {e}")


def _get_product_page_label(browser: Selenium, product: Dict[str, str], env_url: str) -> str:
    """Récupère le libellé depuis la page produit."""
    browser.go_to(f"{env_url}{product['url']}")
    element = browser.find_element(WebProductSelectors.PRODUCT_NAME)
    return browser.get_text(element).splitlines()[0]


def _add_product_to_cart(browser: Selenium) -> None:
    """Ajoute le produit actuel au panier."""
    find_element(browser, WebProductSelectors.ADD_TO_CART_BUTTON)
    wait(add_cart_from_product_page)
    click_image(add_cart_from_product_page)
    wait(popin_add_cart, timeout=TimeoutConfig.LONG_WAIT)


def _get_search_label(browser: Selenium, product: Dict[str, str], env_url: str) -> str:
    """Récupère le libellé depuis les résultats de recherche."""
    browser.go_to(f"{env_url}recherche?query={product['code8']}")
    element = browser.find_element(WebProductSelectors.SEARCH_PRODUCT_NAME)
    return browser.get_text(element)


def _get_cart_label(browser: Selenium, env_url: str) -> str:
    """Récupère le libellé depuis le panier."""
    browser.go_to(f"{os.getenv("pp_web_site")}panier")
    browser.wait_until_element_is_not_visible(WebProductSelectors.LOADING_SPINNER, timeout=TimeoutConfig.LONG_WAIT)
    element = browser.find_element(WebProductSelectors.CART_PRODUCT_NAME)
    return browser.get_text(element).splitlines()[0]


def initialize_web_environment(browser: Selenium, accept_cookies: bool = True) -> None:
    """
    Initialise l'environnement web avec la configuration localStorage.
    
    Args:
        browser: Instance du navigateur
        accept_cookies: Indique si les cookies doivent être acceptés
        
    Note:
        Fonction simplifiée - considérer l'utilisation de initialize_browser() 
        du module web.initialize pour une initialisation complète.
    """
    if accept_cookies:
        try:
            wait(accept_cookies, confidence=0.9)
            click_image(accept_cookies, confidence=0.9)
        except Exception as e:
            print(f"Cookies déjà acceptés ou popup absente: {e}")
    
    # Configuration du localStorage
    localstorage_settings = {
        'isNotificationMinimized': 'true',
        'storeLocatorPopinOpen': 'true',
        'storeLocatorPopinCounter': '3'
    }
    
    for key, value in localstorage_settings.items():
        try:
            update_localstorage(browser, key, value)
        except Exception as e:
            print(f"Attention: Échec localStorage[{key}]: {e}")


def sort_cart_items(browser: Selenium, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Trie les produits selon l'ordre d'affichage dans le panier.
    
    Args:
        browser: Instance du navigateur
        products: Liste de dictionnaires de produits contenant au moins 'code8'
        
    Returns:
        Liste de produits triée selon l'ordre du panier
        
    Raises:
        Exception: Si le tri échoue
    """
    try:
        # Attend que les éléments du panier soient visibles
        browser.wait_until_element_is_visible(WebProductSelectors.CART_ITEM)
        time.sleep(2)  # Délai pour stabilisation du DOM
        
        # Récupère l'ordre des éléments dans le panier
        cart_elements = browser.find_elements(WebProductSelectors.CART_ITEM_XPATH)
        
        cart_order = []
        for element in cart_elements:
            reference = browser.get_element_attribute(element, "data-reference")
            cart_order.append(reference)
        
        # Trie les produits selon l'ordre du panier
        sorted_products = sorted(
            products,
            key=lambda x: cart_order.index(x["code8"]) if x["code8"] in cart_order else len(cart_order)
        )
        
        return sorted_products
        
    except Exception as e:
        raise Exception(f"Échec du tri des articles du panier: {e}")


def generate_order_report(
    orders: List[Tuple[List[Dict[str, Any]], str]],
    suppliers: Optional[List[str]] = None
) -> None:
    """
    Génère un rapport HTML récapitulatif des commandes.
    
    Args:
        orders: Liste de tuples (produits, numéro_commande)
        suppliers: Liste optionnelle des fournisseurs
        
    Note:
        Le chemin de sortie dépend de la variable d'environnement 'env'
    """
    env = os.getenv('env', 'dev').lower()
    output_path = OUTPUT_PATHS.get(env, OUTPUT_PATHS['dev'])
    
    # Tri des commandes par mode de livraison (décroissant)
    sorted_orders = _sort_orders_by_delivery_mode(orders)
    
    # Génération du contenu HTML
    html_content = _build_html_header()
    html_content += _build_orders_section(sorted_orders, suppliers)
    
    if suppliers:
        html_content += _build_suppliers_section(suppliers)
    
    html_content += _build_order_links_section(sorted_orders)
    html_content += "</body></html>"
    
    # Écriture du fichier
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Rapport généré: {output_path}")
    except Exception as e:
        raise Exception(f"Échec de la génération du rapport: {e}")


def _sort_orders_by_delivery_mode(orders: List[Tuple[List[Dict], str]]) -> List[Tuple[List[Dict], str]]:
    """Trie les commandes par mode de livraison."""
    sorted_orders = []
    for products, order_number in orders:
        sorted_products = sorted(products, key=lambda x: x["mode"]["mode"], reverse=True)
        sorted_orders.append((sorted_products, order_number))
    return sorted_orders


def _build_html_header() -> str:
    """Construit l'en-tête HTML du rapport."""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport de commande</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        h1 {{ color: #2c3e50; }}
        h3 {{ color: #34495e; margin-top: 2em; }}
        p {{ margin: 0.5em 0; }}
        ul {{ margin-top: 1em; }}
        .product-detail {{ margin-left: 2em; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Exécution du {datetime.today().strftime("%d/%m/%Y")}</h1>
"""


def _build_orders_section(orders: List[Tuple[List[Dict], str]], include_details: bool) -> str:
    """Construit la section des commandes."""
    html = ""
    
    # Mapping des types de produits
    product_type_labels = {
        "pa": "pièce auto",
        "tire": "pneu",
        "access": "accessoire"
    }
    
    # Mapping des modes de livraison
    delivery_mode_labels = {
        1: "Click And Collect",
        2: "Livraison à domicile",
        3: "Mondial Relay"
    }
    
    for products, order_number in orders:
        html += f"""<h3>Commande {order_number} - {len(products)} produit(s)</h3>"""
        
        if include_details:
            for product in products:
                code8 = product.get("code8", "N/A")
                qty = product.get("qty", 1)
                product_type = product.get("type", "unknown")
                type_label = product_type_labels.get(product_type, "inconnu")
                
                html += f"""<div class="product-detail">
                    <p><strong>Code8:</strong> {code8} | <strong>Quantité:</strong> {qty} | <strong>Type:</strong> {type_label}</p>
"""
                
                # Informations supplémentaires
                if product.get("consigne"):
                    html += """    <p>→ Avec consigne</p>
"""
                if product.get("montage"):
                    html += """    <p>→ Avec service montage</p>
"""
                
                # Mode de livraison
                mode_id = product.get("mode", {}).get("mode")
                mode_label = delivery_mode_labels.get(mode_id, "Mode inconnu")
                html += f"""    <p>→ Livraison: {mode_label}</p>
</div>
"""
    
    return html


def _build_suppliers_section(suppliers: List[str]) -> str:
    """Construit la section des fournisseurs."""
    html = """<br><h2>Commandes fournisseurs</h2><ul>"""
    for supplier in suppliers:
        html += f"<li>{supplier}</li>"
    html += "</ul>"
    return html


def _build_order_links_section(orders: List[Tuple[List[Dict], str]]) -> str:
    """Construit la section des liens vers les commandes."""
    html = """<br/><h2>Liens vers les commandes</h2><ul>"""
    
    base_url = "https://rec-customercare.carter-cash.com/orders/"
    
    for _, order_number in orders:
        html += f"""<li><a href="{base_url}{order_number}" target="_blank">{order_number}</a></li>"""
    
    html += "</ul>"
    return html


def verify_xml_consistency(xml_content: str, order_number: str) -> None:
    """
    Vérifie la cohérence entre le contenu XML et les données de la base de données.
    
    Args:
        xml_content: Contenu du ticket XML à vérifier
        order_number: Numéro de commande
        
    Raises:
        AssertionError: Si une incohérence est détectée
        Exception: Si la vérification échoue
    """
    try:
        # Connexion à la base de données
        web_conn = connect_web_pp()
        
        # Récupération des données
        order_data = get_web_order(web_conn, order_number)
        order_address = get_web_order_adress(web_conn, order_data['id'])
        customer_data = get_web_customer(web_conn, order_data['customer_id'])
        carrier_data = get_web_order_carrier(web_conn, order_data['id'])
        carrier_address = get_web_order_carrier_address(web_conn, carrier_data['id'])
        
        # Parse du XML
        parsed_xml = parse_ticket_vente(xml_content)
        
        # Vérifications
        _verify_order_info(parsed_xml, order_data)
        _verify_customer_info(parsed_xml, customer_data, order_data)
        _verify_delivery_info(parsed_xml, carrier_data, carrier_address)
        _verify_billing_info(parsed_xml, order_address)
        _verify_transaction_info(parsed_xml, order_data)
        
        print(f"Vérification XML réussie pour la commande {order_number}")
        
    except Exception as e:
        raise Exception(f"Échec de la vérification XML pour la commande {order_number}: {e}")


def _verify_order_info(parsed_xml: Dict, order_data: Dict) -> None:
    """Vérifie les informations de commande."""
    Assert.assert_equals(
        parsed_xml['header']["num_ticket"],
        order_data['reference'],
        f"Numéro ticket XML: {parsed_xml['header']['num_ticket']} vs BDD: {order_data['reference']}",
        'verification_xml'
    )


def _verify_customer_info(parsed_xml: Dict, customer_data: Dict, order_data: Dict) -> None:
    """Vérifie les informations client."""
    Assert.assert_equals(
        parsed_xml['header']["nom_client"],
        customer_data['last_name'],
        f"Nom client XML: {parsed_xml['header']['nom_client']} vs BDD: {customer_data['last_name']}",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["prenom_client"],
        customer_data['first_name'],
        f"Prénom client XML: {parsed_xml['header']['prenom_client']} vs BDD: {customer_data['first_name']}",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["tel_client"],
        order_data['phone'],
        f"Téléphone XML: {parsed_xml['header']['tel_client']} vs BDD: {order_data['phone']}",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["mail_client"],
        order_data['email'],
        f"Email XML: {parsed_xml['header']['mail_client']} vs BDD: {order_data['email']}",
        'verification_xml'
    )


def _verify_delivery_info(parsed_xml: Dict, carrier_data: Dict, carrier_address: Dict) -> None:
    """Vérifie les informations de livraison."""
    Assert.assert_equals(
        parsed_xml['header']["mode_livraison"],
        carrier_data['carrier_id'],
        f"Mode livraison XML: {parsed_xml['header']['mode_livraison']} vs BDD: {carrier_data['carrier_id']}",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["adresse_liv_1"],
        carrier_address['address'],
        f"Adresse livraison XML vs BDD",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["adresse_liv_2"],
        carrier_address['additional_address'],
        f"Complément adresse livraison XML vs BDD",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["cp_client"],
        carrier_address['zip_code'],
        f"Code postal livraison XML vs BDD",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["ville_liv"],
        carrier_address['city'],
        f"Ville livraison XML vs BDD",
        'verification_xml'
    )


def _verify_billing_info(parsed_xml: Dict, order_address: Dict) -> None:
    """Vérifie les informations de facturation."""
    Assert.assert_equals(
        parsed_xml['header']["adresse_fac_1"],
        order_address['address'],
        f"Adresse facturation XML vs BDD",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["adresse_fac_2"],
        order_address['additional_address'],
        f"Complément adresse facturation XML vs BDD",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["cp_fac"],
        order_address['zip_code'],
        f"Code postal facturation XML vs BDD",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["ville_fac"],
        order_address['city'],
        f"Ville facturation XML vs BDD",
        'verification_xml'
    )


def _verify_transaction_info(parsed_xml: Dict, order_data: Dict) -> None:
    """Vérifie les informations de transaction."""
    Assert.assert_equals(
        parsed_xml['header']["total_cde"],
        order_data['grant_total_tax_incl'],
        f"Total commande XML: {parsed_xml['header']['total_cde']} vs BDD: {order_data['grant_total_tax_incl']}",
        'verification_xml'
    )
    
    Assert.assert_equals(
        parsed_xml['header']["uuid_transac"],
        order_data['transaction_uuid'],
        f"UUID transaction XML vs BDD",
        'verification_xml'
    )


# Alias de rétrocompatibilité (dépréciés)
def get_web_code8(browser, produit):
    """Déprécié: Utiliser get_product_code8() à la place."""
    print("Attention: get_web_code8() est déprécié. Utiliser get_product_code8()")
    return get_product_code8(browser, produit)


def web_check_label(browser, produit, expected_label, env):
    """Déprécié: Utiliser verify_product_labels() à la place."""
    print("Attention: web_check_label() est déprécié. Utiliser verify_product_labels()")
    return verify_product_labels(browser, produit, expected_label, env)


def init(browser, accept_c):
    """Déprécié: Utiliser initialize_web_environment() à la place."""
    print("Attention: init() est déprécié. Utiliser initialize_web_environment()")
    return initialize_web_environment(browser, accept_c)


def sort_cart(browser, actual):
    """Déprécié: Utiliser sort_cart_items() à la place."""
    print("Attention: sort_cart() est déprécié. Utiliser sort_cart_items()")
    return sort_cart_items(browser, actual)


def write_html(orders, suppliers=None):
    """Déprécié: Utiliser generate_order_report() à la place."""
    print("Attention: write_html() est déprécié. Utiliser generate_order_report()")
    return generate_order_report(orders, suppliers)


def check_xml(content, num_cmd):
    """Déprécié: Utiliser verify_xml_consistency() à la place."""
    print("Attention: check_xml() est déprécié. Utiliser verify_xml_consistency()")
    return verify_xml_consistency(content, num_cmd)