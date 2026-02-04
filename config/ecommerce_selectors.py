
"""Sélecteurs centralisés pour le Ecommerce."""

class EcommerceSelectors:
    """
    Tous les sélecteurs XPath/CSS pour le Ecommerce.
    
    Avantages :
    - 1 seul endroit à modifier si l'UI change
    - Auto-complétion dans l'IDE
    - Facile à tester
    """
    
    # Page
    LOGIN_PAGE = "xpath=//body[contains(@class, 'login')]"

    # LOGIN
    ADD_ACCOUNT = "xpath=//a[contains(@href, '/oauth/redirect')]"

    # LOADING
    SPINNER = 'css:.lds-ring'