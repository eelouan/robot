import time
import os

from RPA.Desktop import Desktop
from PIL import ImageGrab
from dotenv import load_dotenv
from RPA.Images  import Images

from config.img import *
from utils.utils import *

load_dotenv()
images  = Images()

def access_profil(desktop,browser):
    find_element(browser,'.quick-access')
    time.sleep(2)
    find_image(profil_quick_access,0.9)

def personal(desktop,browser):
    find_element(browser,'.link-element')
    time.sleep(1)
    best_match_scale_on_screen_and_click(profil_personal_menu)
    find_element(browser,'#information-container')
    time.sleep(2)

    elem_name = get_element_from_image(profil_personal_firstname_lastname,browser)
    full = browser.get_text(elem_name)
    lines = full.splitlines()
    name_line = lines[-1].strip()
    first, last = name_line.split(" ", 1)
    elem_email = get_element_from_image(profil_personal_email,browser)
    full = browser.get_text(elem_email)
    lines = full.splitlines()
    email = lines[-1].strip()
    elem_phone = get_element_from_image(profil_personal_phone,browser)
    full = browser.get_text(elem_phone)
    lines = full.splitlines()
    phone = lines[-1].strip()

    # Assert
    assert first == os.getenv('firstname'), f"Prénom incorrect : {first!r}"
    assert last  == os.getenv('lastname'),  f"Nom incorrect : {last!r}"
    assert email == os.getenv('mail_tmp'), f"Email incorrect : {email!r}"
    assert phone == os.getenv('phone'), f"Phone incorrect : {phone!r}"

    # Update personal information
    web_click_text(browser, 'Modifier')
    time.sleep(2)
    find_element(browser,'#customer_information')
    select_input_and_fill_for_browser(desktop,profil_personal_update_firstname,os.getenv('bad_firstname'), True)
    select_input_and_fill_for_browser(desktop,profil_personal_update_lastname,os.getenv('bad_lastname'), True)
    select_input_and_fill_for_browser(desktop,profil_personal_update_email,os.getenv('bad_user_mail'), True)
    select_input_and_fill_for_browser(desktop,profil_personal_update_phone,os.getenv('bad_phone'), True)
    time.sleep(1)
    best_match_scale_on_screen_and_click(profil_personal_update_save)

    # Check text from input
    find_element(browser,'#information-container')
    time.sleep(2)
    elem_name = get_element_from_image(profil_personal_firstname_lastname,browser)
    full = browser.get_text(elem_name)
    lines = full.splitlines()
    name_line = lines[-1].strip()
    first, last = name_line.split(" ", 1)
    elem_email = get_element_from_image(profil_personal_email,browser)
    full = browser.get_text(elem_email)
    lines = full.splitlines()
    email = lines[-1].strip()
    elem_phone = get_element_from_image(profil_personal_phone,browser)
    full = browser.get_text(elem_phone)
    lines = full.splitlines()
    phone = lines[-1].strip()

    # Assert
    assert first == os.getenv('bad_firstname'), f"Prénom incorrect : {first!r}"
    assert last  == os.getenv('bad_lastname'),  f"Nom incorrect : {last!r}"
    assert email == os.getenv('bad_user_mail'), f"Email incorrect : {email!r}"
    assert phone == os.getenv('bad_phone'), f"Phone incorrect : {phone!r}"

    find_element(browser,'#information-container')
    web_click_text(browser, 'Modifier')
    find_element(browser,'#customer_information')
    select_input_and_fill_for_browser(desktop,profil_personal_update_firstname,os.getenv('firstname'), True)
    select_input_and_fill_for_browser(desktop,profil_personal_update_lastname,os.getenv('lastname'), True)
    select_input_and_fill_for_browser(desktop,profil_personal_update_email,os.getenv('mail_tmp'), True)
    select_input_and_fill_for_browser(desktop,profil_personal_update_phone,os.getenv('phone'), True)
    best_match_scale_on_screen_and_click(profil_personal_update_save)

    web_click_text(browser, 'Modifier mon mot de passe')
    find_element(browser,'#customer_password')
    select_input_and_fill_for_browser(desktop,profil_personal_update_passwd_mdp,os.getenv('bad_user_passwd'))
    select_input_and_fill_for_browser(desktop,profil_personal_update_passwd_repeat,os.getenv('bad_user_passwd'))
    best_match_scale_on_screen_and_click(profil_personal_update_passwd_save)

    web_click_text(browser, 'Modifier mon mot de passe')
    find_element(browser,'#customer_password')
    select_input_and_fill_for_browser(desktop,profil_personal_update_passwd_mdp,os.getenv('passwd_tmp'))
    select_input_and_fill_for_browser(desktop,profil_personal_update_passwd_repeat,os.getenv('passwd_tmp'))
    best_match_scale_on_screen_and_click(profil_personal_update_passwd_save)

    find_element(browser,'.custom-control')
    best_match_scale_on_screen_and_click(profil_personal_newsletter)
    best_match_scale_on_screen_and_click(profil_personal_prospecting)
    best_match_scale_on_screen_and_click(profil_personal_save)

    find_element(browser,'.custom-control')
    best_match_scale_on_screen_and_click(profil_personal_newsletter)
    best_match_scale_on_screen_and_click(profil_personal_prospecting)
    best_match_scale_on_screen_and_click(profil_personal_save)

def address(desktop,browser):
    find_element(browser,'.link-element')
    best_match_scale_on_screen_and_click(profil_address_menu)
    find_element(browser,'.add-address')
    best_match_scale_on_screen_and_click(profil_address_add)
    find_element(browser,'#address')
    select_input_and_fill_for_browser(desktop,profil_address_add_firstname,os.getenv('bad_firstname'))
    select_input_and_fill_for_browser(desktop,profil_address_add_lastname,os.getenv('bad_lastname'))
    select_input_and_fill_for_browser(desktop,profil_address_add_address,os.getenv('bad_address'))
    best_match_scale_on_screen_and_click(profil_address_add_address_woosmap)
    find_element(browser,'.bt[type="submit"]')
    best_match_scale_on_screen_and_click(profil_address_add_add)

    time.sleep(2)

    if is_existe(google_save_address):
        best_match_scale_on_screen_and_click(google_save_address)
    
    find_element(browser,'.customer-address')
    elem = get_element_from_image(profil_address_badelem,browser)
    full = browser.get_text(elem)
    lines = full.splitlines()

    name_line = lines[0].split(" ", 1)
    firstname_line = name_line[0].strip()
    lastname_line = name_line[-1].strip()
    addr_line = lines[1].strip()
    where_line = lines[2].split(" ", 1)
    cp_line = where_line[0]
    city_line = where_line[1]

    assert firstname_line == os.getenv('bad_firstname'), f"Prénom incorrect : {firstname_line!r}"
    assert lastname_line  == os.getenv('bad_lastname'),  f"Nom incorrect : {lastname_line!r}"
    assert addr_line == os.getenv('bad_address'), f"Address incorrect : {addr_line!r}"
    assert cp_line == os.getenv('bad_cp'), f"cp incorrect : {cp_line!r}"
    assert city_line == os.getenv('bad_city'), f"city incorrect : {city_line!r}"

    elem = get_element_from_image(profil_address_elem,browser)
    full = browser.get_text(elem)
    lines = full.splitlines()

    name_line = lines[0].split(" ", 1)
    firstname_line = name_line[0].strip()
    lastname_line = name_line[-1].strip()
    addr_line = lines[1].strip()
    where_line = lines[2].split(" ", 1)
    cp_line = where_line[0]
    city_line = where_line[1]

    assert firstname_line == os.getenv('firstname'), f"Prénom incorrect : {firstname_line!r}"
    assert lastname_line  == os.getenv('lastname'),  f"Nom incorrect : {lastname_line!r}"
    assert addr_line == os.getenv('address'), f"Address incorrect : {addr_line!r}"
    assert cp_line == os.getenv('cp'), f"cp incorrect : {cp_line!r}"
    assert city_line == os.getenv('city'), f"city incorrect : {city_line!r}"

    find_element(browser,'.address-border')
    time.sleep(1)
    best_match_scale_on_screen_and_click(profil_address_update,1)

    find_element(browser,'#address')
    select_input_and_fill_for_browser(desktop,profil_address_update_firstname,os.getenv('firstname'), True)
    select_input_and_fill_for_browser(desktop,profil_address_update_lastname,os.getenv('lastname'), True)
    select_input_and_fill_for_browser(desktop,profil_address_update_address,os.getenv('address'), True)
    best_match_scale_on_screen_and_click(profil_address_update_address_woosmap)
    find_element(browser,'.bt[type="submit"]')
    best_match_scale_on_screen_and_click(profil_address_update_update)
    time.sleep(2)

    if is_existe(google_save_address):
        best_match_scale_on_screen_and_click(google_save_address)
    find_element(browser,'.address-border')
    best_match_scale_on_screen_and_click(profil_address_delete,1)
    browser.go_to(os.getenv("pp_web_site")+'/compte')


def car(desktop,browser):
    find_element(browser,'.link-element')
    best_match_scale_on_screen_and_click(profil_car_menu)
    find_element(browser,'.cars-blocks-container')
    best_match_scale_on_screen_and_click(profil_car_add)
    find_element(browser,'.license-plate-form-container')
    select_input_and_fill_for_browser(desktop,profil_car_add_licence,os.getenv('licence_plate'))
    best_match_scale_on_screen_and_click(profil_car_add_add,0)
    # pyautogui.moveTo(0, 0)
    find_element(browser,'.cars-blocks-container')
    elem = get_element_from_image(profil_car_elem,browser)
    full = browser.get_text(elem)
    lines = full.splitlines()
    # print(elem.get_attribute('outerHTML'))

    brand = lines[0].strip()
    cylinder = lines[1].strip()
    date = lines[2].strip()
    licence_plate_line = lines[3].split(" ", 1)
    licence_plate = licence_plate_line[0].strip()

    assert brand == os.getenv('brand_licence_plate'), f"Marque incorrect : {brand!r}"
    assert cylinder  == os.getenv('cylinder_licence_plate'),  f"Cylindre incorrect : {cylinder!r}"
    assert date == os.getenv('date_licence_plate'), f"Date du cylindre incorrect : {date!r}"
    assert licence_plate == os.getenv('licence_plate'), f"Plaque d'immatriculation incorrect : {licence_plate!r}"

    best_match_scale_on_screen_and_click(profil_car_add)
    find_element(browser,'.car-selector-form-container')

    best_match_scale_on_screen_and_click(profil_car_add_brand)
    best_match_scale_on_screen_and_click(profil_car_add_brand_brand)

    best_match_scale_on_screen_and_click(profil_car_add_model)
    best_match_scale_on_screen_and_click(profil_car_add_model_model)

    best_match_scale_on_screen_and_click(profil_car_add_cylindrer)
    best_match_scale_on_screen_and_click(profil_car_add_cylinder_cylinder)

    best_match_scale_on_screen_and_click(profil_car_add_add,1)

    find_element(browser,'.cars-blocks-container')

    elem = get_element_from_image(profil_car_elem_selector,browser)
    full = browser.get_text(elem)
    lines = full.splitlines()

    brand = lines[0].strip()
    cylinder = lines[1].strip()
    date = lines[2].strip()

    assert brand == os.getenv('brand_selector'), f"Marque incorrect : {brand!r}"
    assert cylinder  == os.getenv('cylinder_selector'),  f"Cylindre incorrect : {cylinder!r}"
    assert date == os.getenv('date_selector'), f"Date du cylindre incorrect : {date!r}"

    best_match_scale_on_screen_and_click(profil_car_delete,1)