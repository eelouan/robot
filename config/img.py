import json
import getpass
import os
import sys
from pathlib import Path


from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

user = getpass.getuser()

if os.getenv('env').lower() == 'dev' or os.getenv('env').lower() == 'test':
    json_path = Path(__file__).parent.parent / "json" / "environement.json"
else:
    json_path = os.path.join(r"C:\Users\Public\Documents\Tests\6-AUTRE", "environement.json")
with open(json_path, "r", encoding="utf-8") as f:
    environement_web = json.load(f)

parsed = urlparse(os.getenv("pp_web_site"))
id = parsed.netloc.split('.')[-1]

print(f'parsed {parsed}, id {id}')

if id == 'com':
    state = 'fr'
else:
    state = id

if user.lower() == "emoreau":
    loc = "local"
else:
    loc = "server"

google_save_address = f"asset/button/google_save_address.png"
accept_position = f"asset/button/accept_position.png"
accept_notification = f"asset/button/accept_notification.png"

### Global Website
accept_cookies = f"asset/button/web/{state}/accept_cookies.png"
notification_popup = f"asset/notification_popup.png" # ?

# MENU
menu_tire = f"asset/link/web/{state}/menu_tire.png"

### Connect Auth0
account = f"asset/input/web/{state}/account.png"
button_disconnect = f"asset/button/web/{state}/disconect.png"
connect_mail = f"asset/input/web/{state}/connect_mail.png"
connect_passwd = f"asset/input/web/{state}/connect_passwd.png"
connect_auth0 = f"asset/input/web/{state}/connect_auth0.png"
is_connect = f"asset/input/web/{state}/is_connect.png"

connect_menu = f"asset/button/web/{state}/connect.png"
connect_log = f"asset/button/web/{state}/connect_log.png"
connect_account = f"asset/button/web/{state}/connect_account.png"
isConnect = f"asset/button/web/{state}/isConnect.png"
connect_connect = f"asset/button/web/{state}/connect_connect.png"

### Cart
panier = f"asset/button/web/{state}/panier.png"

### PROFIL
profil_quick_access = f"asset/input/web/{state}/profil_quick_access.png"

## Profil address
profil_address_menu = f"asset/link/web/{state}/profil_address_menu.png"
profil_address_quick = f"asset/link/web/{state}/profil_address_quick.png"
profil_address_add = f"asset/button/web/{state}/profil_address_add.png"
profil_address_badelem = f"asset/input/web/{state}/profil_address_badelem.png"
profil_address_elem = f"asset/input/web/{state}/profil_address_elem.png"

profil_address_delete = f"asset/button/web/{state}/profil_address_delete.png"
profil_address_update = f"asset/button/web/{state}/profil_address_update.png"

# Add
profil_address_add_firstname = f"asset/input/web/{state}/profil_address_add_firstname.png"
profil_address_add_lastname = f"asset/input/web/{state}/profil_address_add_lastname.png"
profil_address_add_address = f"asset/input/web/{state}/profil_address_add_address.png"
profil_address_add_address_woosmap = f"asset/input/web/{state}/profil_address_add_address_woosmap.png"
profil_address_add_cp = f"asset/input/web/{state}/profil_address_add_cp.png"
profil_address_add_city = f"asset/input/web/{state}/profil_address_add_city.png"

profil_address_add_add = f"asset/button/web/{state}/profil_address_add_add.png"

# Update
profil_address_update_firstname = f"asset/input/web/{state}/profil_address_update_firstname.png"
profil_address_update_lastname = f"asset/input/web/{state}/profil_address_update_lastname.png"
profil_address_update_address = f"asset/input/web/{state}/profil_address_update_address.png"
profil_address_update_address_woosmap = f"asset/input/web/{state}/profil_address_update_address_woosmap.png"

profil_address_update_update = f"asset/button/web/{state}/profil_address_update_update.png"

## Profil car
profil_car_menu = f"asset/link/web/{state}/profil_car_menu.png"
profil_car_quick = f"asset/link/web/{state}/profil_car_quick.png"
profil_car_delete = f"asset/link/web/{state}/profil_car_delete.png"
profil_car_update = f"asset/link/web/{state}/profil_car_update.png"

profil_car_elem = f"asset/input/web/{state}/profil_car_elem.png"
profil_car_elem_selector = f"asset/input/web/{state}/profil_car_elem_selector.png"

profil_car_add = f"asset/button/web/{state}/profil_car_add.png"

# Add
profil_car_add_licence = f"asset/input/web/{state}/profil_car_add_licence.png"
profil_car_add_brand = f"asset/input/web/{state}/profil_car_add_brand.png"
profil_car_add_model = f"asset/input/web/{state}/profil_car_add_model.png"
profil_car_add_cylindrer = f"asset/input/web/{state}/profil_car_add_cylindrer.png"
profil_car_add_brand_brand = f"asset/input/web/{state}/profil_car_add_brand_brand.png"
profil_car_add_model_model = f"asset/input/web/{state}/profil_car_add_model_model.png"
profil_car_add_cylinder_cylinder = f"asset/input/web/{state}/profil_car_add_cylinder_cylinder.png"

profil_car_add_add = f"asset/button/web/{state}/profil_car_add_add.png"

## Profil personal information
profil_personal_firstname_lastname = f"asset/input/web/{state}/profil_personal_firstname_lastname.png"
profil_personal_email = f"asset/input/web/{state}/profil_personal_email.png"
profil_personal_phone = f"asset/input/web/{state}/profil_personal_phone.png"
profil_personal_newsletter = f"asset/input/web/{state}/profil_personal_newsletter.png"
profil_personal_prospecting = f"asset/input/web/{state}/profil_personal_prospecting.png"

profil_personal_menu = f"asset/link/web/{state}/profil_personal_menu.png"
profil_personal_quick = f"asset/link/web/{state}/profil_address_quick.png"

profil_personal_update = f"asset/button/web/{state}/profil_personal_update.png"
profil_personal_update_passwd = f"asset/button/web/{state}/profil_personal_update_passwd.png"
profil_personal_save = f"asset/button/web/{state}/profil_personal_save.png"

# Update
profil_personal_update_firstname = f"asset/input/web/{state}/profil_personal_update_firstname.png"
profil_personal_update_lastname = f"asset/input/web/{state}/profil_personal_update_lastname.png"
profil_personal_update_phone = f"asset/input/web/{state}/profil_personal_update_phone.png"
profil_personal_update_email = f"asset/input/web/{state}/profil_personal_update_email.png"
profil_personal_update_passwd_mdp = f"asset/input/web/{state}/profil_personal_update_passwd_mdp.png"
profil_personal_update_passwd_repeat = f"asset/input/web/{state}/profil_personal_update_passwd_repeat.png"
profil_personal_update_passwd_save = f"asset/button/web/{state}/profil_personal_update_passwd_save.png"

profil_personal_update_save = f"asset/button/web/{state}/profil_personal_update_save.png"

nav_pa = f"asset/input/web/{state}/nav_pa.png"
store = f"asset/link/web/{state}/store.png"
store_woosmap = f"asset/link/web/{state}/store_woosmap.png"
store_select = f"asset/input/web/{state}/store_select.png"
store_validate = f"asset/button/web/{state}/store_validate.png"
store_close_popin = f"asset/button/web/{state}/store_close_popin.png"
cart = f"asset/link/web/{state}/cart.png"
nav_pneu = f"asset/button/web/{state}/nav_pneu.png"
nav_accessory = f"asset/input/web/{state}/nav_accessory.png"
nav_voir_tout = f"asset/input/web/{state}/nav_voir_tout.png"

category_frein = f"asset/button/web/{state}/category_frein.png"
category_huile = f"asset/button/web/{state}/category_huile.png"
freinage = f"asset/input/web/{state}/freinage.png"
huile = f"asset/input/web/{state}/huile.png"
cat_plaquette_frein = f"asset/button/web/{state}/cat_plaquette_frein.png"
cat_huile_moteur = f"asset/button/web/{state}/cat_huile_moteur.png"
category_demarrage_charge = f"asset/button/web/{state}/category_demarrage_charge.png"
cat_alternateur = f"asset/button/web/{state}/cat_alternateur.png"
add_cart_from_product_page = f"asset/button/web/{state}/add_cart_from_product_page.png"

listing_see_cart = f"asset/button/web/{state}/listing_see_cart.png"
listing_add_cart = f"asset/button/web/{state}/listing_add_cart.png"
popin_add_cart = f"asset/input/web/{state}/popin_add_cart.png"
cart_approve = f"asset/button/web/{state}/cart_approve.png"
cart_no_account = f"asset/button/web/{state}/cart_no_account.png"
cart_1_approve = f"asset/button/web/{state}/cart_1_approve.png"
cart_no_livraison = f"asset/button/web/{state}/cart_no_livraison.png"
cart_livraison = f"asset/button/web/{state}/cart_livraison.png"
cart_mr = f"asset/button/web/{state}/cart_mr.png"
cart_domicile = f"asset/button/web/{state}/cart_domicile.png"
popin_mr = f"asset/input/web/{state}/popin_mr.png"
woosmap_mr = f"asset/input/web/{state}/woosmap_mr.png"
default_mr = f"asset/input/web/{state}/default_mr.png"
pay_card_test = f"asset/button/web/{state}/pay_card_test.png"
pay_card_card = f"asset/button/web/{state}/pay_card_card.png"
pay_approve = f"asset/button/web/{state}/pay_approve.png"
test_card = f"asset/input/web/{state}/test_card.png"
product_page_add_cart = f"asset/button/web/{state}/product_page_add_cart.png"
firstname_factu = f"asset/input/web/{state}/firstname_factu.png"
valid_factu = f"asset/button/web/{state}/valid_factu.png"
suivi_email = f"asset/input/web/{state}/suivi_email.png"
add_address_liv = f"asset/button/web/{state}/add_address_liv.png"
firstname_liv = f"asset/input/web/{state}/firstname_liv.png"

# -----------------------------------------ATHENA------------------------------------------------

logo_connect = "asset/input/athena/logo_connect.png"
athena_connect = "asset/input/athena/athena_connect.png"
athena_passwd = "asset/input/athena/athena_passwd.png"
athena_menu_lateral = "asset/input/athena/athena_menu_lateral.png" 
athena_connect_connect = "asset/button/athena/athena_connect_connect.png"
athena_cmd = "asset/button/athena/athena_cmd.png"
athena_cmd_cde = "asset/button/athena/athena_cmd_cde.png"
athena_menu_lateral_cmd = "asset/input/athena/athena_menu_lateral_cmd"
athena_articles = "asset/button/athena/athena_articles.png"
athena_arlicles_list = "asset/button/athena/athena_arlicles_list.png"
athena_menu_lateral_articles = "asset/input/athena/athena_menu_lateral_articles.png"
athena_actions = "asset/input/athena/athena_actions.png"
athena_articles_list_visu = "asset/input/athena/athena_articles_list_visu.png"
athena_reponse_unique = "asset/input/athena/athena_reponse_unique.png"
athena_select_article = "asset/input/athena/athena_select_article.png"
athena_search_article = "asset/button/athena/athena_search_article.png"
athena_fiche_article = "asset/button/athena/athena_fiche_article.png"
athena_popin_voir_article = "asset/input/athena/athena_popin_voir_article.png"   
athena_libelle_web = "asset/input/athena/athena_libelle_web.png"
athena_search_article_visu = "asset/input/athena/athena_search_article_visu.png"
athena_accueil = "asset/input/athena/athena_accueil.png"
athena_to_order = "asset/input/athena/to_order.png"
customer_order = "asset/input/athena/customer_order.png"
ticket_number = "asset/input/athena/ticket_number.png"
code_intern = "asset/input/athena/code_intern.png"
transfer_yakaedi = "asset/button/athena/transfer_yakaedi.png"
athena_ok = "asset/button/athena/ok.png"
is_load = "asset/input/athena/is_load.png"
select_all = "asset/input/athena/select_all.png"
filter_purchase_order = "asset/button/athena/filter_purchase_order.png"
button_continue = "asset/button/athena/button_continue.png"
ticket_cdc = "asset/input/athena/ticket_cdc.png"
select = "asset/input/athena/select.png"
check = "asset/input/athena/check.png"
athena_close = "asset/button/athena/athena_close.png"
search_article_load = "asset/input/athena/search_article_load.png"
raz = "asset/button/athena/raz.png"


certificate_warning = f"asset/{loc}/certificate_warning.png"
certificate = f"asset/{loc}/certificate.png"

# -----------------------------------------VTOM------------------------------------------------

jobs = f"asset/{loc}/button/vtom/jobs.png"
vtom_connect_visu = f"asset/input/vtom/vtom_connect.png"
# env = f"asset/button/vtom/env.png"
start = f"asset/{loc}/input/vtom/start.png" # started
regex = f"asset/input/vtom/regex.png" # regex
regex_equals = f"asset/{loc}/input/vtom/regex_equals.png" # regex equal
popin_filter_job = f"asset/{loc}/input/vtom/popin_filter_job.png" # regex equal

suivi_env = f"asset/link/vtom/suivi_env.png"
vtom_copy_board = f"asset/button/vtom/vtom_copy_board.png"

filter = f"asset/{loc}/link/vtom/filter.png" # bouton de filtre
input_env = f"asset/{loc}/input/vtom/env.png" # input de choix d'env à filtrer

adjust = f"asset/button/vtom/adjust.png" # bouton de redimentionnement de la page de traitement ou flux
menu_action = f"asset/input/vtom/menu_action.png" # menu d'action
force_execute = f"asset/{loc}/button/vtom/force_execute.png" # forcer l'execution
force_execute_2 = f"asset/{loc}/button/vtom/force_execute_2.png" # confimé forcer l'execution
execute_end = f"asset/{loc}/input/vtom/execute_end.png" # label de fin d'execution du flux exit 0
execute_in_process = f"asset/{loc}/input/vtom/execute_in_process.png" # label en cour d'execution du flux

# WMS_JOUR
wms_jour = f"asset/link/vtom/wms_jour.png" # label
wms_jour_env = f"asset/link/vtom/wms_jour/env.png" # label env
env_wms_jour = f"asset/input/vtom/env_wms_jour.png" # label env

envoi_commande = f"asset/button/vtom/wms_jour/envoi_commande.png" # traitement
env_envoi_commande = f"asset/input/vtom/wms_jour/env_envoi_commande.png" # label env
envoi_commande_ego_lad = f"asset/button/vtom/wms_jour/envoi_commande_ego_lad.png" # flux
envoi_commande_integration = f"asset/button/vtom/wms_jour/envoi_commande_integration.png" # flux

preparation = f"asset/button/vtom/wms_jour/preparation.png" # traitement
env_preparation = f"asset/input/vtom/wms_jour/env_preparation.png" # label env
preparation_1 = f"asset/button/vtom/wms_jour/preparation_1.png" # flux
preparation_2 = f"asset/button/vtom/wms_jour/preparation_2.png" # flux
preparation_3 = f"asset/button/vtom/wms_jour/preparation_3.png" # flux

traitement_cmd_epo = f"asset/button/vtom/wms_jour/traitement_cmd_epo.png" # traitement
env_traitement_epo = f"asset/input/vtom/wms_jour/env_traitement_epo.png" # label env
traitement_cmd_epo_1 = f"asset/button/vtom/wms_jour/traitement_cmd_epo_1.png" # flux
traitement_cmd_epo_2= f"asset/button/vtom/wms_jour/traitement_cmd_epo_2.png" # flux
traitement_cmd_epo_3= f"asset/button/vtom/wms_jour/traitement_cmd_epo_3.png" # flux

traitement_cmd_shi = f"asset/button/vtom/wms_jour/traitement_cmd_shi.png" # traitement
env_traitement_shi = f"asset/input/vtom/wms_jour/env_traitement_shi.png" # label env
traitement_cmd_shi_1 = f"asset/button/vtom/wms_jour/traitement_cmd_shi_1.png" # flux
traitement_cmd_shi_2 = f"asset/button/vtom/wms_jour/traitement_cmd_shi_2.png" # flux
traitement_cmd_shi_3 = f"asset/button/vtom/wms_jour/traitement_cmd_shi_3.png" # flux

traitement_cmd_rbr = f"asset/button/vtom/wms_jour/traitement_cmd_rbr.png" # traitement
env_traitement_rbr = f"asset/input/vtom/wms_jour/env_traitement_rbr.png" # label env
traitement_cmd_rbr_1 = f"asset/button/vtom/wms_jour/traitement_cmd_rbr_1.png" # flux
traitement_cmd_rbr_2 = f"asset/button/vtom/wms_jour/traitement_cmd_rbr_2.png" # flux
traitement_cmd_rbr_3 = f"asset/button/vtom/wms_jour/traitement_cmd_rbr_3.png" # flux
traitement_cmd_rbr_4 = f"asset/button/vtom/wms_jour/traitement_cmd_rbr_4.png" # flux

reception_cmd = f"asset/button/vtom/wms_jour/reception_cmd.png" # traitement
env_reception_cmd = f"asset/input/vtom/wms_jour/env_reception_cmd.png" # label env
reception_cmd_1 = f"asset/button/vtom/wms_jour/reception_cmd_1.png" # flux
reception_cmd_2 = f"asset/button/vtom/wms_jour/reception_cmd_2.png" # flux

# WEB
vtom_web = f"asset/link/vtom/web.png" # label
web_env = f"asset/link/vtom/web/{state}/env.png" # label env

suivi = f"asset/button/vtom/suivi.png"
env_web = f"asset/input/vtom/env_web.png"
traitement = f"asset/{loc}/input/vtom/traitement.png"
count_traitement = f"asset/{loc}/input/vtom/count_traitement.png"

recup_ticket = f"asset/button/vtom/web/{state}/recup_ticket.png" # traitement
env_recup_ticket = f"asset/input/vtom/web/{state}/env_recup_ticket.png" # label env
recup_ticket_1 = f"asset/button/vtom/web/{state}/recup_ticket_1.png" # flux
recup_ticket_2 = f"asset/button/vtom/web/{state}/recup_ticket_2.png" # flux
recup_ticket_3 = f"asset/button/vtom/web/{state}/recup_ticket_3.png" # flux
recup_ticket_4 = f"asset/button/vtom/web/{state}/recup_ticket_4.png" # flux

# -----------------------------------------EGO------------------------------------------------

bo = f"asset/button/ego/bo.png"
user_bo = f"asset/input/ego/user_bo.png"
load_lobby = f"asset/input/ego/load_lobby.png"
out = f"asset/button/ego/out.png"
input_ordre_a_preparer = f"asset/link/ego/ordre_a_preparer.png"
create_ordre = f"asset/button/ego/create_ordre.png"
link_create_ordre = f"asset/link/ego/create_ordre.png"
filter_num = f"asset/link/ego/filter_num.png"
ego_ok = f"asset/button/ego/ok.png"
choix_reservation = f"asset/input/ego/choix_reservation.png"
popin_filter = f"asset/input/ego/popin_filter.png"
plage = f"asset/button/ego/plage.png"
all_ordre = f"asset/button/ego/all_ordre.png"
popin_information = f"asset/input/ego/popin_information.png"
qualif = f"asset/button/ego/qualif.png"
popin_mode = f"asset/input/ego/popin_mode.png"
qualif1 = f"asset/input/ego/qualif1.png"
ordre_vide = f"asset/input/ego/ordre_vide.png"
ego_close = f"asset/button/ego/ego_close.png"
ok_with_close = f"asset/button/ego/ok_with_close.png"
ok_cut = f"asset/button/ego/ok_cut.png"
ok_large = f"asset/button/ego/ok_large.png"
ok_qualif = f"asset/button/ego/ok_qualif.png"
qualif_vide = f"asset/input/ego/qualif_vide.png"
link_valid = f"asset/link/ego/link_valid.png"
valid = f"asset/input/ego/valid.png"
valid_prepare = f"asset/button/ego/valid_prepare.png"
valid_woop = f"asset/input/ego/valid_woop.png"
valid_valid = f"asset/button/ego/valid_valid.png"
close_qualif = f"asset/button/ego/close_qualif.png"
valid_woop_single = f"asset/input/ego/valid_woop_single.png"
valid_vide = f"asset/input/ego/valid_vide.png"
close_prepare = f"asset/button/ego/close_prepare.png"
close = f"asset/button/ego/close_os.png"
title_os = f"asset/input/ego/os.png"
link_colisage = f"asset/link/ego/link_colisage.png"
colisage = f"asset/input/ego/colisage.png"
consult_colisage = f"asset/input/ego/consult_colisage.png"
colisage_number = f"asset/input/ego/colisage_number.png"
title_valid = f"asset/input/ego/title_valid.png"
update_colisage = f"asset/button/ego/update_colisage.png"
see_colisage = f"asset/input/ego/see_colisage.png"
ego_oui = f"asset/button/ego/oui.png"
attente_prepare = f"asset/input/ego/attente_prepare.png"
information_ok = f"asset/button/ego/information_ok.png"

enter = f"asset/button/ego/in.png"
simple_receip = f"asset/link/ego/simple_receip.png"
receive_purchase_order = f"asset/input/ego/receive_purchase_order.png"
number_delivery_note = f"asset/input/ego/number_delivery_note.png"
bulk_reception = f"asset/button/ego/bulk_reception.png"
article = f"asset/input/ego/article.png"
all_quantity = f"asset/input/ego/all_quantity.png"
char = f"asset/input/ego/char.png"
compartiment = f"asset/input/ego/compartiment.png"
reception_ok = f"asset/button/ego/reception_ok.png"
close_reception = f"asset/button/ego/close_reception.png"
enclose = f"asset/button/ego/enclose.png"
enclose_ok = f"asset/button/ego/enclose_ok.png"
reception_arrow_select = f"asset/input/ego/reception_arrow_select.png"
addressing_char = f"asset/link/ego/addressing_char.png"
addressing_mission = f"asset/link/ego/addressing_mission.png"
address_char = f"asset/button/ego/address_char.png"
addressing_char_char = f"asset/input/ego/addressing_char_char.png"
arrow_addressing_char = f"asset/input/ego/arrow_addressing_char.png"
auto_address = f"asset/button/ego/auto_address.png"
check_all_address = f"asset/button/ego/check_all_address.png"
auto_address_empty = f"asset/input/ego/auto_address_empty.png"
auto_address_title = f"asset/input/ego/auto_address_title.png"
address_title = f"asset/input/ego/address_title.png"
cret1 = f"asset/input/ego/cret1.png"
check_all_mission = f"asset/button/ego/check_all_mission.png"
valid_addressing = f"asset/button/ego/valid_addressing.png"
mission_empty = f"asset/input/ego/mission_empty.png"
mission_address_title = f"asset/input/ego/mission_address_title.png"
logoff = f"asset/button/ego/logoff.png"
bad_char = f"asset/input/ego/bad_char.png"
ok_bad_reception = f"asset/button/ego/ok_bad_reception.png"
unite = f"asset/input/ego/unite.png"
crmult1 = f"asset/input/ego/crmult1.png"
order_list = f"asset/input/ego/order_list.png"


pda = f"asset/button/ego/pda.png"
pda_connected = f"asset/input/ego/pda_connected.png"
pda_expe_cmd = f"asset/input/ego/pda_expe_cmd.png"
pda_lobby = f"asset/input/ego/pda_lobby.png"
pda_menu_expe = f"asset/input/ego/pda_menu_expe.png"
cargo = f"asset/input/ego/creation_changement_declaratif/cargo.png"
carrier_dpd = f"asset/input/ego/creation_changement_declaratif/carrier_dpd.png"
carrier_tnt = f"asset/input/ego/creation_changement_declaratif/carrier_tnt.png"
carrier_mr = f"asset/input/ego/creation_changement_declaratif/carrier_mr.png"
carrier_informations = f"asset/input/ego/creation_changement_declaratif/carrier_informations.png"
show_carrier = f"asset/input/ego/creation_changement_declaratif/show_carrier.png"
show_store = f"asset/input/ego/creation_changement_declaratif/show_store.png"
print_cargo = f"asset/input/ego/creation_changement_declaratif/print_cargo.png"
take_done = f"asset/input/ego/creation_changement_declaratif/take_done.png"
take_support = f"asset/input/ego/creation_changement_declaratif/take_support.png"
title = f"asset/input/ego/creation_changement_declaratif/title.png"
cb_support = f"asset/input/ego/creation_changement_declaratif/cb_support.png"
pda_quit = f"asset/button/ego/pda_quit.png"

# -----------------------------------------WOOP------------------------------------------------

woop = {
    'first_connect' : f"asset/button/woop/first_connect.png",
    'lobby_search' : f"asset/input/woop/lobby_search.png",
    'passwd' : f"asset/input/woop/passwd.png",
    'user' : f"asset/input/woop/user.png",
    'lobby' : f"asset/input/woop/lobby.png",
    'connect' : f"asset/input/woop/connect.png",
    'action' : f"asset/button/woop/action.png",
    'update' : f"asset/button/woop/update.png",
    'select_action' : f"asset/input/woop/select_action.png",
    'action_select_open' : f"asset/input/woop/action_select_open.png",
    'register_action' : f"asset/button/woop/register_action.png",
    'search' : f"asset/input/woop/search.png",
    'error_return_sender' : f"asset/input/woop/status/error_return_sender.png",
    'delivery_failure-customer_absent' : f"asset/input/woop/status/delivery_failure-customer_absent.png",
}


# -----------------------------------------OB------------------------------------------------

ob = {
    "user_connect_adm" : f"asset/button/ob/user_connect_adm.png",
    "user_connect_sell" : f"asset/button/ob/user_connect_sell.png",
    "user" : f"asset/input/ob/user.png",
    "online_connect" : f"asset/input/ob/online_connect.png",
    "logo" : f"asset/input/ob/logo.png",
    "web_pos" : f"asset/button/ob/web_pos.png",
    "ok" : f"asset/button/ob/ok.png",
    "continue" : f"asset/button/ob/continue.png",
    "login_error" : f"asset/input/ob/login_error.png",
    "cash_register_close" : f"asset/input/ob/cash_register_close.png",
    "count_register" : f"asset/button/ob/count_register.png",
    "close_next" : f"asset/button/ob/close_next.png",
    "hardware_manager" : f"asset/input/ob/hardware_manager.png",
    "approval" : f"asset/input/ob/approval.png",
    "total_amount" : f"asset/input/ob/total_amount.png",
    "count_register" : f"asset/button/ob/count_register.png",
    "total_amount" : f"asset/input/ob/total_amount.png",
    "open" : f"asset/input/ob/open.png",
    "ok_open" : f"asset/button/ob/ok_open.png",
    "family" : f"asset/button/ob/family.png",
    "category" : f"asset/button/ob/category.png",
    "best_seller" : f"asset/button/ob/best_seller.png",
    "total" : f"asset/button/ob/total.png",
    "finish" : f"asset/button/ob/finish.png",
    "delete_all" : f"asset/button/ob/delete_all.png",
    "continue_after_pay" : f"asset/button/ob/continue_after_pay.png",
    "bring_tire" : f"asset/input/ob/bring_tire.png",
    "printer" : f"asset/input/ob/printer.png",
    "print_page" : f"asset/input/ob/print_page.png",
    "voucher" : f"asset/input/ob/voucher.png",
    "same_voucher" : f"asset/input/ob/same_voucher.png",
    "valid" : f"asset/button/ob/valid.png",
    "save_print_output" : f"asset/input/ob/save_print_output.png",
}


# -----------------------------------------APPLI------------------------------------------------

appli = {
    "athena": r"\\genosis-rec\ATHENA\Athena.UI.exe",
    "hardware_manager": r"C:\Users\Public\Documents\OB\HardwareManager\bin\start.bat"
}
