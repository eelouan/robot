import time
import os
import matplotlib.pyplot as plt
import json
from pathlib import Path

from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

import getpass

class Assert:
    assertions = {
        'success': {},
        'error': {}
    }
    trad: dict = {}
    comments: dict = {}
    error: dict = {}
    ticket_number = []
    intercept = None

    @classmethod
    def write_assert(cls, message, suite='', ok=True):
        state = "success" if ok else "error"
        cls.assertions.setdefault(state, {}).setdefault(suite or "_", []).append(message)

    @classmethod
    def element_should_visible(cls, browser, elem, name="", case="", visible=True):
        try:
            browser.element_should_be_visible(elem) if visible else browser.element_should_not_be_visible(elem)
            ok = True
        except:
            ok = False
        bucket = "success" if ok else "error"
        tpl_key = "good" if ok else "bad"
        case_map = cls.comments.get(case, {}) if isinstance(cls.comments, dict) else {}
        default_tpl = "OK" if ok else f"KO"
        tpl = (case_map.get(tpl_key) or default_tpl).strip()

        try:
            comment = tpl.format(elem=elem, name=name)
        except Exception:
            comment = default_tpl

        message = f"{name} - {comment}" if name else comment
        cls.assertions.setdefault(bucket, {}).setdefault(case or "_", []).append(message)

    @classmethod
    def assert_equals(cls, actual, expected, name="", case=""):
        ok = (actual == expected)
        bucket = "success" if ok else "error"
        tpl_key = "good" if ok else "bad"
        case_map = cls.comments.get(case, {}) if isinstance(cls.comments, dict) else {}
        default_tpl = ""
        tpl = (case_map.get(tpl_key) or default_tpl).strip()

        try:
            comment = tpl.format(actual=actual, expected=expected, name=name)
        except Exception:
            comment = default_tpl

        message = f"{name} - {comment}" if name else comment
        cls.assertions.setdefault(bucket, {}).setdefault(case or "_", []).append(message)

    @classmethod
    def assert_bool(cls, actual, expected, name="", case=""):
        ok = (actual is expected)
        bucket = "success" if ok else "error"
        tpl_key = "good" if ok else "bad"
        case_map = cls.comments.get(case, {}) if isinstance(cls.comments, dict) else {}
        default_tpl = ""
        tpl = (case_map.get(tpl_key) or default_tpl).strip()

        try:
            comment = tpl.format(actual=actual, expected=expected, name=name)
        except Exception:
            comment = default_tpl

        message = f"{name} - {comment}" if name else comment
        cls.assertions.setdefault(bucket, {}).setdefault(case or "_", []).append(message)

    @classmethod
    def assert_text_in_array(cls, text, array, name="", case=""):
        ok = (text in array)
        bucket = "success" if ok else "error"
        tpl_key = "good" if ok else "bad"
        case_map = cls.comments.get(case, {}) if isinstance(cls.comments, dict) else {}
        default_tpl = ""
        tpl = (case_map.get(tpl_key) or default_tpl).strip()

        try:
            comment = tpl.format(text=text, array=array, name=name)
        except Exception:
            comment = default_tpl

        message = f"{name} - {comment}" if name else comment
        cls.assertions.setdefault(bucket, {}).setdefault(case or "_", []).append(message)

    @classmethod
    def get_assert(cls):
        return cls.assertions

    @classmethod
    def reset(cls):
        cls.assertions = {
            'success': {},
            'error': {}
        }

    @classmethod
    def generate(cls, output_path=r"6-AUTRE"):
        if os.getenv('env').lower() == 'dev':
            output_path=f"assertion_report_{datetime.today().strftime("%d-%m-%Y_%H-%M-%S")}.pdf"
        elif os.getenv('env').lower() == 'test':
            output_path=f"assertion_report.pdf"
        else:
            print(output_path)
            output_path=os.path.join(r"C:\Users\Public\Documents\Tests", output_path, f'assertion_report_{datetime.today().strftime("%d-%m-%Y_%H-%M-%S")}.pdf')
        if cls.assertions['success'] or cls.assertions['error']:
            success = sum(len(msgs) for msgs in cls.assertions['success'].values())
            error = sum(len(msgs) for msgs in cls.assertions['error'].values())

            # 1. Générer le camembert
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie(
                [success, error],
                labels=["Succès", "Erreurs"],
                colors=["green", "red"],
                autopct='%1.1f%%',
                startangle=90
            )
            ax.axis('equal')
            pie_path = "assertion_pie_chart.png"
            plt.savefig(pie_path)
            plt.close()

        # 2. Générer le PDF avec reportlab
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        flowables = []

        flowables.append(Paragraph("Rapport d'assertions", styles['Heading1']))
        flowables.append(Paragraph(f"Rapport généré par {getpass.getuser()} le {datetime.today().strftime("%d-%m-%Y %H:%M:%S")}", styles['Heading4']))
        flowables.append(Spacer(1, 0.5 * cm))
        if cls.intercept:
            red_style = ParagraphStyle('RedHeading', parent=styles['Heading2'], textColor=colors.red)
            flowables.append(Paragraph(cls.error[0][cls.intercept], red_style))
        # else:
        #     green_style = ParagraphStyle('RedHeading', parent=styles['Heading2'], textColor=colors.green)
        #     flowables.append(Paragraph('Le test c\'est déroulé sans encombre', green_style))

        if cls.assertions['success'] or cls.assertions['error']:
            flowables.append(RLImage(pie_path, width=10*cm, height=10*cm))
            flowables.append(Spacer(1, 1 * cm))

            flowables.append(Paragraph(f"✅ Succès ({success})", styles['Heading2']))
            for case, comments in cls.assertions['success'].items():
                flowables.append(Paragraph(cls.trad[case], styles['Heading4']))
                success_items = [
                    ListItem(Paragraph(comment, styles['Normal']), bulletColor="green")
                    for comment in comments
                ]
                flowables.append(ListFlowable(success_items, bulletType='bullet'))

            flowables.append(Spacer(1, 1 * cm))
            flowables.append(Paragraph(f"❌ Erreurs ({error})", styles['Heading2']))
            for case, comments in cls.assertions['error'].items():
                flowables.append(Paragraph(cls.trad[case], styles['Heading4']))
                error_items = [
                    ListItem(Paragraph(comment, styles['Normal']), bulletColor="red")
                    for comment in comments
                ]
                flowables.append(ListFlowable(error_items, bulletType='bullet'))

                flowables.append(Spacer(1, 3 * cm))
        if cls.ticket_number:
            flowables.append(Paragraph(f"✅ Ticket OB ({len(cls.ticket_number)})", styles['Heading2']))
            numbers = [
                    ListItem(Paragraph(num, styles['Normal']))
                    for num in cls.ticket_number
                ]
            flowables.append(ListFlowable(numbers, bulletType='bullet'))

        doc.build(flowables)

        # Nettoyage image
        # if not cls.intercept:
            # if os.path.exists(pie_path):
            # os.remove(pie_path)

    @classmethod
    def set_intercept(cls, str):
        cls.intercept = str
        if str != "generic":
            raise Exception

    @classmethod
    def get_intercept(cls):
        return cls.intercept
    
    @classmethod
    def _load_json(cls, path, attr):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Fichier introuvable: {path}")
        with path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON invalide dans {path}: {e}") from e

        setattr(cls, attr, data)

    @classmethod
    def get_comment(cls):
        return cls.comments
    
    @classmethod
    def get_trad(cls):
        return cls.trad
    
    @classmethod
    def set_ob_ticket_number(cls, num):
        cls.ticket_number.append(num)

    @classmethod
    def get_ob_ticket(cls):
        return cls.ticket_number

Assert._load_json(Path(__file__).parent.parent / "json" / "comments.json", "comments")
Assert._load_json(Path(__file__).parent.parent / "json" / "error.json", "error")
Assert._load_json(Path(__file__).parent.parent / "json" / "trad.json", "trad")
