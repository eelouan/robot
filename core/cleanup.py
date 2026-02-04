"""
Fonctions de nettoyage et finalisation communes à toutes les tâches.
"""

import subprocess
import sys
import logging
from utils.Assert import Assert


def cleanup_resources(desktop=None, browser=None):
    """
    Nettoie toutes les ressources (navigateur, desktop, processus).
    
    Args:
        desktop: Instance Desktop (optionnel)
        browser: Instance Browser (optionnel)
    
    Returns:
        list: Liste des erreurs rencontrées
    """
    errors = []
    
    # Fermeture navigateur
    if browser:
        try:
            browser.close_all_browsers()
        except Exception as e:
            errors.append(f"Browser: {e}")
    
    # Fermeture desktop
    if desktop:
        try:
            desktop.close_all_applications()
        except Exception as e:
            errors.append(f"Desktop: {e}")
    
    # Kill processus zombies
    try:
        kill_zombie_processes()
    except Exception as e:
        errors.append(f"Zombie processes: {e}")
    
    # Flush logs
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        logging.shutdown()
    except Exception as e:
        errors.append(f"Logs: {e}")
    
    # Afficher les erreurs
    if errors:
        print(f"\n⚠ {len(errors)} erreur(s) de nettoyage:")
        for err in errors:
            print(f"  - {err}")
    
    return errors


def kill_zombie_processes(timeout=10):
    """
    Tue les processus zombies (chromedriver, chrome, etc.).
    
    Args:
        timeout: Timeout en secondes
    """
    subprocess.run(
        'taskkill /F /T /IM chromedriver.exe /IM chrome.exe /IM node.exe /IM msedge.exe',
        shell=True,
        capture_output=True,
        timeout=timeout
    )


def generate_final_report(report_path=None):
    """
    Génère le rapport final avec fallback.
    
    Args:
        report_path: Chemin personnalisé du rapport (optionnel)
    
    Returns:
        bool: True si le rapport a été généré avec succès
    """
    try:
        if report_path:
            Assert.generate(report_path)
            print(f"✅ Rapport: {report_path}")
        else:
            Assert.generate()
            print("✅ Rapport généré (défaut)")
        return True
    
    except Exception as e:
        print(f"❌ Erreur rapport: {e}")
        
        # Fallback
        if report_path:
            try:
                Assert.generate()
                print("✅ Rapport (défaut après échec)")
                return True
            except:
                pass
        
        return False