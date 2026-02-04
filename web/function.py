import time
import os
import pytesseract
import pyautogui
import cv2
import numpy as np

from RPA.Desktop import Desktop
from PIL import ImageGrab
from dotenv import load_dotenv
from RPA.Images  import Images

from config.img import environement_web

from utils.utils import *
from utils.connect_db import *
from utils.Assert import *
from utils.request import *
from web.connect import *
from web.create import *

def get_web_code8(browser, produit):
    browser.go_to(f"{os.getenv("pp_web_site")}{produit['url']}")
    wait(add_cart_from_product_page)
    code8 = browser.find_element('css:.main-product .main-informations').get_attribute('data-reference')
    return code8

def web_check_label(browser, produit, expected_label, env):
    label = {}
    browser.go_to(f"{env}{produit['url']}")

    elem = '.product-information .product-name'
    str_product_page = browser.get_text(browser.find_element(f"css:{elem}")).splitlines()[0]
    find_element(browser,'css:#add_to_cart_add')
    wait(add_cart_from_product_page)
    click_image(add_cart_from_product_page)
    wait(popin_add_cart, timeout=15)
    browser.go_to(f"{env}recherche?query={produit["code8"]}")

    elem = '.product-name'
    str_search_algolia = browser.get_text(browser.find_element(f'css:{elem}'))

    browser.go_to(f"{os.getenv("pp_web_site")}panier")
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=15)

    elem = '.text-container .name'
    str_cart = browser.get_text(browser.find_element(f'css:{elem}')).splitlines()[0]

    # # print(f'str_search_algolia : {str_search_algolia}')
    # # print(f'str_product_page : {str_product_page}')
    # # print(f'str_cart : {str_cart}')

    Assert.assert_equals(str_search_algolia, expected_label, f"Nom du produit dans la barre de recherche algolia est {expected_label}", 'check_libelle')
    Assert.assert_equals(str_product_page, expected_label, f"Nom du produit sur la page produit est {expected_label}", 'check_libelle')
    Assert.assert_equals(str_cart, expected_label, f"Nom du produit dans le panier est {expected_label}", 'check_libelle')

def init(browser, accept_c):
    if accept_c:
        wait(accept_cookies, confidence=0.9)
        click_image(accept_cookies, confidence=0.9)

    update_localstorage(browser, 'isNotificationMinimized', 'true')
    update_localstorage(browser, 'storeLocatorPopinOpen', 'true')
    update_localstorage(browser, 'storeLocatorPopinCounter', '3')
        

def sort_cart(browser, actual):
    expected = []
    browser.wait_until_element_is_visible('css:.item')
    time.sleep(2)
    elements = browser.find_elements("xpath=//div[contains(@class, 'item') and @data-reference]")

    expected = []
    for element in elements:
        value = browser.get_element_attribute(element, "data-reference")
        expected.append(value)


    actual_sorted = sorted(
        actual,
        key=lambda x: expected.index(x["code8"])
    )
    return actual_sorted


def write_html(orders, suppliers=None):
    list_cmd = []
    if os.getenv('env').lower() == 'dev':
        output_path = os.path.join(r"recapitulatif_commande.html")
    elif os.getenv('env').lower() == 'test':
        output_path = os.path.join(r"recapitulatif_commande.html")
    else:
        output_path = os.path.join(r"C:\Users\Public\Documents\Tests\6-AUTRE\recapitulatif_commande.html")
    html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Rapport de commande</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #2c3e50; }}
                p {{ margin: 0.5em 0; }}
                ul {{ margin-top: 1em; }}
            </style>
        </head>
        <body>
            <h1>Execution du {datetime.today().strftime("%d/%m/%Y")}</h1>
    """



    for i in range(len(orders)):
        produitss, code = orders[i]
        produitss_sorted = sorted(produitss, key=lambda x: x["mode"]["mode"], reverse=True)
        orders[i] = (produitss_sorted, code)


    for produitss, cmd in orders:
        html += f"""<h3>La commande {cmd} contient {len(produitss)} produitss :</h3>"""
        if suppliers:
            for produits in produitss:
                code8 = produits["code8"]
                modes = produits["mode"]
                dispo = produits["dispo"]
                montage = produits["montage"]
                type = produits["type"]
                type_label = {
                    "pa": "pièce auto",
                    "tire": "pneu",
                    "access": "accessoire"
                }.get(type, "inconnu")
                consigne = produits["consigne"]
                qty = produits["qty"]
                # cmd = order[1]
                html += f"""<br/><p>Le code 8 : {code8} avec un quantitée de {qty} de la famille de {type_label}</p>"""
                if consigne:
                    html += f"""<p>Avec une consigne attaché au produits</p>"""
                if montage:
                    html += f"""<p>Avec service montage</p>"""
                match modes["mode"]:
                    case 1: 
                        html += f"""<p>livraison Click And Collect</p>\n\n"""
                    case 2:
                        html += f"""<p>livraison à domicile</p>\n\n"""
                    case 3:
                        html += f"""<p>livraison Mondial relay</p>\n\n"""
        list_cmd.append(cmd)
        # f.write("\n")
    if suppliers:
        html += """<br><h2>Toutes les commandes fournisseurs :</h2><ul>"""
        for supplier in suppliers:
            html += f"""<li>{supplier}</li>"""
        html += """</ul>"""
    html += """<br/><h2>Toutes les commandes :</h2><ul>"""
    for cmd in list_cmd:
        html += f"""<li><a href="https://rec-customercare.carter-cash.com/orders/{cmd}">{cmd}</a></li>"""

    html += """</ul></body></html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

def check_xml(content, num_cmd):
    web_conn = connect_web_pp()
    order_sql = get_web_order(web_conn, num_cmd)
    # order_sql = get_web_order(web_conn, num_cmd)
    order_address = get_web_order_adress(web_conn, order_sql['id'])
    customer_sql = get_web_customer(web_conn, order_sql['customer_id'])
    order_carrier_sql = get_web_order_carrier(web_conn, order_sql['id'])
    order_carrier_address_sql = get_web_order_carrier_address(web_conn, order_carrier_sql['id'])
    parsed = parse_ticket_vente(content)
    Assert.assert_equals(parsed['header']["num_ticket"], order_sql['reference'], f"le numero de ticket dans le ticket xml est {parsed['header']['num_ticket']} et la BDD du site web est {order_sql['reference']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["nom_client"], customer_sql['last_name'], f"Le nom du client dans le ticket xml est {parsed['header']['nom_client']} et la BDD du site web est {customer_sql['last_name']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["prenom_client"], customer_sql['first_name'], f"Le prénom du client dans le ticket xml est {parsed['header']['prenom_client']} et la BDD du site web est", 'verification_xml')

    # factu
    # Assert.assert_equals(parsed['header']["NomCLient"], address['lastname'], f"Le prénom du client dans le ticket xml est {parsed['header']['NomCLient']} et la BDD du site web est {address['lastname']}", 'verification_xml')
    # Assert.assert_equals(parsed['header']["PrenomClient"], address['firstname'], f"Le nom du client dans le ticket xml est {parsed['header']['PrenomClient']} et la BDD du site web est {address['firstname']}", 'verification_xml')

    Assert.assert_equals(parsed['header']["tel_client"], order_sql['phone'], f"Le numéro de téléphone du client dans le ticket xml est {parsed['header']['tel_client']} et la BDD du site web est {order_sql['phone']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["mail_client"], order_sql['email'], f"Le mail du client dans le ticket xml est {parsed['header']['mail_client']} et la BDD du site web est {order_sql['email']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["mode_livraison"], order_carrier_sql['carrier_id'], f"Le mode de livraison de la commande dans le ticket xml est {parsed['header']['mode_livraison']} et la BDD du site web est {order_carrier_sql['carrier_id']}", 'verification_xml')

    Assert.assert_equals(parsed['header']["adresse_liv_1"], order_carrier_address_sql['address'], f"L'adresse de livraison de la commande dans le ticket xml est {parsed['header']['adresse_liv_1']} et la BDD du site web est {order_carrier_address_sql['address']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["adresse_liv_2"], order_carrier_address_sql['additional_address'], f"L'adresse de livraison complémentaire de la commande dans le ticket xml est {parsed['header']['adresse_liv_2']} et la BDD du site web est {order_carrier_address_sql['additional_address']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["cp_client"], order_carrier_address_sql['zip_code'], f"Le code postale de l'adresse de livraison de la commande dans le ticket xml est {parsed['header']['cp_client']} et la BDD du site web est {order_carrier_address_sql['zip_code']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["ville_liv"], order_carrier_address_sql['city'], f"La ville de livraison de la commande dans le ticket xml est {parsed['header']['ville_liv']} et la BDD du site web est {order_carrier_address_sql['city']}", 'verification_xml')

    Assert.assert_equals(parsed['header']["adresse_fac_1"], order_address['address'], f"L'adresse de livraison de la commande dans le ticket xml est {parsed['header']['adresse_fac_1']} et la BDD du site web est {order_address['address']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["adresse_fac_2"], order_address['additional_address'], f"L'adresse de livraison complémentaire de la commande dans le ticket xml est {parsed['header']['adresse_fac_2']} et la BDD du site web est {order_address['additional_address']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["cp_fac"], order_address['zip_code'], f"Le code postale de l'adresse de livraison de la commande dans le ticket xml est {parsed['header']['cp_fac']} et la BDD du site web est {order_address['zip_code']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["ville_fac"], order_address['city'], f"Le total d'achat de la commande dans le ticket xml est {parsed['header']['ville_fac']} et la BDD du site web est {order_address['city']}", 'verification_xml')


    Assert.assert_equals(parsed['header']["total_cde"], order_sql['grant_total_tax_incl'], f"Le total d'achat de la commande dans le ticket xml est {parsed['header']['total_cde']} et la BDD du site web est {order_sql['grant_total_tax_incl']}", 'verification_xml')
    Assert.assert_equals(parsed['header']["uuid_transac"], order_sql['transaction_uuid'], f"L'uuid de transaction de la commande dans le ticket xml est {parsed['header']['uuid_transac']} et la BDD du site web est {order_sql['transaction_uuid']}", 'verification_xml')
    # print(parsed['header']["num_ticket"], parsed['header']["total_cde"])
    # for l in parsed["lines"]:
    #     print(l["num_ligne_ticket"], l["code_interne_article"], l["qte"], l["prix_vente_ttc"])