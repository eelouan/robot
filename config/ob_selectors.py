"""Sélecteurs centralisés pour OpenBravo."""

class OpenBravoSelectors:
    """
    Tous les sélecteurs XPath/CSS pour OpenBravo.
    
    Avantages :
    - 1 seul endroit à modifier si l'UI change
    - Auto-complétion dans l'IDE
    - Facile à tester
    """
    
    # Boutons
    BUTTON_CUSTOMER = "xpath=//button[contains(@id, 'bpbutton')]"
    BUTTON_SUBMIT = "xpath=//button[contains(@id, 'newcustomersave')]"
    BUTTON_CANCEL = "xpath=//button[contains(@id, 'cancelEdit')]"
    BUTTON_UPDATE_CUSTOMER = "xpath=//*[contains(@id, 'listBpsSelectorLine_btnContextMenu')]"
    BUTTON_UPDATE = "xpath=//*[contains(@id, 'bPEditContextMenuItem')]"
    BUTTON_START_PAY = (
        "xpath=//button[contains(@id,'exactbutton') "
        "and contains(., 'TOTAL') "
        "and not(contains(@style, 'display:none'))]"
    )
    BUTTON_OPEN_PAY = "xpath=//button[contains(@id,'donebutton') and contains(., 'Ouvrir')]"
    BUTTON_FINISH_PAY = "xpath=//button[contains(@id,'donebutton') and contains(., 'Terminé')]"
    BUTTON_CONTINUE_AFTER_PAY = "terminal_containerWindow_pointOfSale_obsmail_getEmailAddressModal_emailAddressModal__btnSendEmail"
    BUTTON_PAYMENT_CASH = "xpath=//button[contains(@id,'keyboard_toolbarcontainer_toolbarPayment') and contains(., 'Espèces')]"
    BUTTON_PAYMENT_CB = "xpath=//button[contains(@id,'keyboard_toolbarcontainer_toolbarPayment') and contains(., 'CB')]"
    BUTTON_PAYMENT = "xpath=//button[.//div[normalize-space(text())='Paiement']]"
    BUTTON_PRINTER = (
            "xpath=//*[contains(@id,'getEmailAddressModal')]"
            "[.//*[contains(@id,'labelPrint')]]"
            "//*[contains(@id,'checkPrint')]"
        )
    BUTTON_START_PAY_EXACT = "xpath=//button[@id='terminal_containerWindow_pointOfSale_multiColumn_rightPanel_toolbarpane_payment_paymentTabContent_exactbutton']"
    BUTTON_CREATE_ORDER = "xpath=//button[contains(@id, 'abaReceiptToolbar1_actionButton')]"
    BUTTON_NEW = "xpath=//button[contains(@id, 'buttonNew')]"
    BUTTON_MULTI_ORDER = "xpath=//*[contains(@id, 'doneMultiOrdersButton')]"
    BUTTON_SEARCH = "css:#terminal_containerWindow_pointOfSale_multiColumn_rightPanel_toolbarpane_searchCharacteristic_searchCharacteristicTabContent_searchProductCharacteristicHeader_productSearchButton"
    BUTTON_MENU = "xpath=//button[contains(@id, 'mainMenu_menuHolder_mainMenuButton')]"
    BUTTON_BRING_WHEEL = "xpath=//button[contains(@id, '_ccfldsDoesBringWheel')]"
    BUTTON_REMAINING_PAY = (
        "xpath=//button[contains(@id,'paymentTabContent_exactbutton') "
        "and contains(., 'Restant à payer')]"
    )
    BUTTON_NEW = "xpath=//button[contains(@id, 'buttonNew')]"
    BUTTON_FACTURE = "xpath=//button[contains(@id, 'bottomRightScanAba1_actionButton') and contains(., 'Facturer')]"
    BUTTON_SCANNER = "xpath=//button[contains(@id,'toolbarBtnScan') and contains(., 'SCANNER')]"
    BUTTON_DELETE_PAYMENT = "xpath=//button[contains(@id, 'removePayment')]"
    BUTTON_SCAN_ZERO = "xpath=//button[contains(@id, 'bottomRightScanKeyboard_keyboardkey0')]"
    BUTTON_MINUS = "xpath=//button[contains(@id, 'bottomRightScanKeyboard_removeqty')]"
    BUTTON_DELETE_TICKET = "xpath=//button[contains(@id,'buttonDelete')]"
    BUTTON_MODAL_OK = "xpath=//button[contains(@id, 'dynamicConfirmationPopup_footer_confirmationPopup_btnOK')]"
    BUTTON_OVERPAYMENT_OK = "xpath=//*[contains(@id, 'confirmationPopup_btnOK')]"

    BUTTON_UPDATE_ADDRESS = "xpath=//*[contains(@id, 'listBpsLocLine_btnContextMenu')]"
    BUTTON_UPDATE_ADDRESS_MENU = "xpath=//*[contains(@id, 'bPLocEditContextMenuItem')]"
    BUTTON_SUBMIT_ADDRESS = "xpath=//button[contains(@id, 'newcustomeraddrsave')]"
    BUTTON_UPDATE_DETAIL = "xpath=//*[contains(@id, 'editticketcustomeraddr')]"
    BUTTON_CLOSE_ADDRESS = "xpath=//*[contains(@id, 'editCustomerFooter_close')]"
    BUTTON_ADDRESS = "xpath=//button[contains(@id, 'bplocbutton')]"
    BUTTON_CUSTOMER = "xpath=//button[contains(@id, 'bpbutton')]"
    BUTTON_UPDATE_CUSTOMER = "xpath=//*[contains(@id, 'listBpsSelectorLine_btnContextMenu')]"
    BUTTON_UPDATE = "xpath=//*[contains(@id, 'bPEditContextMenuItem')]"
    BUTTON_SUBMIT_CUSTOMER = "xpath=//button[contains(@id, 'newcustomersave')]"
    BUTTON_CLOSE2 = "xpath=//button[contains(@id, 'close2')]"
    BUTTON_CLOSE_MODAL = "xpath=//button[contains(@id, 'modalDialogButton')]"
    BUTTON_PREPARE_SELECTED = "xpath=//button[contains(@id,'buttonPrepareSelected')]"
    BUTTON_CANCEL_PRINT = "xpath=//button[contains(@id, 'confirmationPopup_btnAnnuler')]"
    BUTTON_CANCEL_MODAL = "xpath=//button[contains(@id, 'btnAnnuler')]"


    # Modales
    MODAL_CUSTOMER = "xpath=//*[contains(@id, 'modalcustomer')]"
    MODAL_DYNAMIC = "xpath=//*[contains(@id, 'dynamicConfirmationPopup')]"
    MODAL_RETURN = "xpath=//*[contains(@id, 'modalVerifiedReturns')]"
    MODAL_REASON = "xpath=//*[contains(@id, 'ModalReturnReason')]"
    MODAL_RETURN_APPROVAL = "xpath=//button[contains(@id,'approval-panel')]"
    MODAL_RECEIPT = "xpath=//*[contains(@id, 'modalReceiptSelector')]"
    MODAL_DELETE_TICKET = "xpath=//div[contains(@id, 'modalConfirmReceiptDelete')]"
    MODAL_ADDRESS = "xpath=//*[contains(@id, 'modalcustomeraddress')]"
    MODAL_CUSTOMER = "xpath=//*[contains(@id, 'modalcustomer')]"
    MODAL_ORDER_SELECTOR = "xpath=//*[contains(@id,'ModalOrderSelector')]"
    MODAL_DYNAMIC_BODY = "xpath=//*[contains(@id,dynamicConfirmationPopup_body_control)]"
    BUTTON_MODAL_DELETE = "xpath=//button[contains(@id,'btnModalApplyDelete')]"
    
    # Formulaire client
    INPUT_EMAIL = "xpath=//input[contains(@id, 'customerEmail')]"
    
    # Alertes
    ALERT_QUEUE = "xpath=//div[contains(@id, 'terminal_alertQueue')]"
    MESSAGE_SCRIM = "xpath=//div[contains(@class, 'obUiFormElement-messageArea-scrim')]"
    ALERT_NO_MIX_RETURN_SALE = (
        "xpath=//div[contains(@class,'obUiTerminal-alertContainer-alertQueue') "
        "and contains(., 'Il est impossible de combiner retour et vente sur le même ticket')]"
    )

    # Input
    INPUT_CUSTOMER = "xpath//input[contains(@id, 'entityFilterText')]"

    # Autre
    LINE1_PRODUCT = "xpath=//li[contains(@id, 'terminal_containerWindow_pointOfSale_multiColumn_leftPanel_receiptview_orderview_listOrderLines_tbody_control')]"
    SCRIM = "xpath=//div[contains(@class,'onyx-scrim-transparent')]"
    NAV_MENU_RETURN_WITHOUT_TICKET = f"xpath=//div[contains(@id,'menuReturn2')]"
    LINE1_CHECK = "xpath=//*[contains(@id, 'line1_checkboxButtonReturn')]"
    ALL_LINES = "xpath=//*[contains(@id, 'checkboxButtonAll')]"
    TOTAL_RECEIPT = "css:#terminal_containerWindow_pointOfSale_multiColumn_leftPanel_receiptview_orderview_totalReceiptLine_totalgross"
    KEYPAD_ZERO = "terminal_containerWindow_pointOfSale_multiColumn_rightPanel_rightBottomPanel_keyboard_keypadcontainer_keypadBasic_keypadBtn0_button_components"
    PAYMENT_LINE_AMOUNT = "css:.obObposPointOfSaleUiRenderPaymentLine-container1-container1-container1-amount"
    LINE_RECEIPT = "xpath=//*[contains(@id, 'receiptSelectorRenderLine')]"
    SELECT_PRODUCT_STATE = f"xpath=//select[contains(@id,'coreElementContainer_list')]"
    FORM_LOGIN = f"xpath=//select[contains(@id,'login_form')]"

    @staticmethod
    def customer_by_name(first_name: str) -> str:
        """
        Génère un sélecteur pour trouver un client par prénom.
        
        Args:
            first_name: Prénom (sera échappé automatiquement)
        
        Returns:
            str: XPath sécurisé
        """
        # Échapper les caractères spéciaux
        safe_name = first_name.replace("'", "\\'").replace('"', '\\"')
        
        return (
            f"xpath=//*[contains(@id, 'listBpsSelectorLine_identifier')"
            f" and contains(normalize-space(text()), '{safe_name}')]"
        )
    
    @staticmethod
    def line_ticket(ticket: str) -> str:
        """
        Génère un sélecteur pour trouver un ticket.
        
        Args:
            ticket: Numéro du ticket
        
        Returns:
            str: XPath sécurisé
        """
        
        return f"xpath=//*[contains(@id, 'receiptSelectorRenderLine') and contains(.,'{ticket}')]"
    
    @staticmethod
    def nav_menu(name_menu: str) -> str:
        """
        Génère un sélecteur pour trouver le menu correspondent.
        
        Args:
            ticket: Nom du menu
        
        Returns:
            str: XPath sécurisé
        """
        
        return f"xpath://div[contains(@id,'{name_menu}')]"
    
    @staticmethod
    def payment_method_button(method: str) -> str:
        """Génère le sélecteur pour un bouton de méthode de paiement."""
        return (
            f"xpath=//button[contains(@id,'keyboard_toolbarcontainer_toolbarPayment') "
            f"and contains(., '{method}')]"
        )
    
    @staticmethod
    def address_by_value(address):
        """Sélecteur pour une adresse par valeur."""
        return f"xpath=//*[contains(@id, 'listBpsLocLin') and contains(.,'{address}')]"
    
    @staticmethod
    def order_checkbox(order_number):
        """Sélecteur pour cocher une commande web par numéro."""
        return (
            f"xpath=//*[contains(@id,'order')]"
            f"[.//*[contains(@id,'documentNo') and contains(normalize-space(.), '{order_number}')]]"
            f"//div[contains(@id,'listOrdersLine_iconOrder')]"
        )