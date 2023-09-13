"""REST API server for analyzer."""
import json
import logging
import os
from logging.config import fileConfig
from pathlib import Path
from typing import Tuple

from flask import Flask, request, jsonify, Response
from presidio_analyzer.analyzer_response import AnalyzerResponse
from werkzeug.exceptions import HTTPException

from presidio_analyzer.analyzer_engine import AnalyzerEngine
from presidio_analyzer.analyzer_request import AnalyzerRequest
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.predefined_recognizers import EmailRecognizer
from presidio_analyzer.predefined_recognizers import SpacyRecognizer
from presidio_analyzer.predefined_recognizers import IpRecognizer
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer
from presidio_analyzer.predefined_recognizers import IbanRecognizer
from presidio_analyzer.predefined_recognizers import UsSsnRecognizer
from presidio_analyzer.predefined_recognizers import PhoneRecognizer
from presidio_analyzer.predefined_recognizers import UsPassportRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider

DEFAULT_PORT = "3000"

LOGGING_CONF_FILE = "logging.ini"

LANGUAGES_CONFIG_FILE = "./conf/default.yaml"

WELCOME_MESSAGE = r"""
 _______  _______  _______  _______ _________ ______  _________ _______
(  ____ )(  ____ )(  ____ \(  ____ \\__   __/(  __  \ \__   __/(  ___  )
| (    )|| (    )|| (    \/| (    \/   ) (   | (  \  )   ) (   | (   ) |
| (____)|| (____)|| (__    | (_____    | |   | |   ) |   | |   | |   | |
|  _____)|     __)|  __)   (_____  )   | |   | |   | |   | |   | |   | |
| (      | (\ (   | (            ) |   | |   | |   ) |   | |   | |   | |
| )      | ) \ \__| (____/\/\____) |___) (___| (__/  )___) (___| (___) |
|/       |/   \__/(_______/\_______)\_______/(______/ \_______/(_______)
"""


class Server:
    """HTTP Server for calling Presidio Analyzer."""

    def __init__(self):
        fileConfig(Path(Path(__file__).parent, LOGGING_CONF_FILE))


        self.logger = logging.getLogger("presidio-analyzer")
        self.logger.setLevel(os.environ.get("LOG_LEVEL", self.logger.level))
        self.app = Flask(__name__)
        self.logger.info("Starting analyzer engine")

        # 
        ## Create NLP engine based on configuration file
        provider = NlpEngineProvider(conf_file=LANGUAGES_CONFIG_FILE)
        multilingual_nlp_engine = provider.create_engine()
        # 
        ## Setting up English recognizers:
        email_recognizer_en = EmailRecognizer(supported_language="en", context=["email", "mail"])
        spacy_recognizer_en = SpacyRecognizer(supported_language="en")
        ip_recognizer_en = IpRecognizer(supported_language="en")
        credit_card_recognizer_en = CreditCardRecognizer(supported_language="en")
        iban_recognizer_en = IbanRecognizer(supported_language="en")
        us_ssn_recognizer_en = UsSsnRecognizer(supported_language="en")
        phone_recognizer_en = PhoneRecognizer(supported_language="en")
        us_passport_recognizer_en = UsPassportRecognizer(supported_language="en")
                # 
        ## Setting up Spanish recognizers:
        email_recognizer_es = EmailRecognizer(supported_language="es", context=["correo", "electrónico"])
        spacy_recognizer_es = SpacyRecognizer(supported_language="es")
        ip_recognizer_es = IpRecognizer(supported_language="es")
        credit_card_recognizer_es = CreditCardRecognizer(supported_language="es")
        iban_recognizer_es = IbanRecognizer(supported_language="es")
        us_ssn_recognizer_es = UsSsnRecognizer(supported_language="es")
        phone_recognizer_es = PhoneRecognizer(supported_language="es")
        us_passport_recognizer_es = UsPassportRecognizer(supported_language="es")
        
        # 
        ## Setting up French recognizers:
        spacy_recognizer_fr = SpacyRecognizer(supported_language="fr")
        email_recognizer_fr = EmailRecognizer(supported_language="fr", context=["poster", "électronique"])
        ip_recognizer_fr = IpRecognizer(supported_language="fr")
        credit_card_recognizer_fr = CreditCardRecognizer(supported_language="fr")
        iban_recognizer_fr = IbanRecognizer(supported_language="fr")
        us_ssn_recognizer_fr = UsSsnRecognizer(supported_language="fr")
        phone_recognizer_fr = PhoneRecognizer(supported_language="fr")
        us_passport_recognizer_fr = UsPassportRecognizer(supported_language="fr")
        # 
        ## Setting up German recognizers:
        spacy_recognizer_de = SpacyRecognizer(supported_language="de")
        email_recognizer_de = EmailRecognizer(supported_language="de", context=["post", "elektronisch"])
        ip_recognizer_de = IpRecognizer(supported_language="de")
        credit_card_recognizer_de = CreditCardRecognizer(supported_language="de")
        iban_recognizer_de = IbanRecognizer(supported_language="de")
        us_ssn_recognizer_de = UsSsnRecognizer(supported_language="de")
        phone_recognizer_de = PhoneRecognizer(supported_language="de")
        us_passport_recognizer_de = UsPassportRecognizer(supported_language="de")
         
        # Setting up Catalan recognizers:
        spacy_recognizer_ca = SpacyRecognizer(supported_language="ca")
        email_recognizer_ca = EmailRecognizer(supported_language="ca", context=["correu electrònic", "correu"])
        ip_recognizer_ca = IpRecognizer(supported_language="ca")
        credit_card_recognizer_ca = CreditCardRecognizer(supported_language="ca")
        iban_recognizer_ca = IbanRecognizer(supported_language="ca")
        us_ssn_recognizer_ca = UsSsnRecognizer(supported_language="ca")
        phone_recognizer_ca = PhoneRecognizer(supported_language="ca")
        us_passport_recognizer_ca = UsPassportRecognizer(supported_language="ca")
         
        # Setting up Chinese recognizers:
        spacy_recognizer_zh = SpacyRecognizer(supported_language="zh")
        email_recognizer_zh = EmailRecognizer(supported_language="zh", context=["电子邮件", "邮件"])
        ip_recognizer_zh = IpRecognizer(supported_language="zh")
        credit_card_recognizer_zh = CreditCardRecognizer(supported_language="zh")
        iban_recognizer_zh = IbanRecognizer(supported_language="zh")
        us_ssn_recognizer_zh = UsSsnRecognizer(supported_language="zh")
        phone_recognizer_zh = PhoneRecognizer(supported_language="zh")
        us_passport_recognizer_zh = UsPassportRecognizer(supported_language="zh")
         
        # Setting up Croatian recognizers:
        spacy_recognizer_hr = SpacyRecognizer(supported_language="hr")
        email_recognizer_hr = EmailRecognizer(supported_language="hr", context=["elektronička pošta", "pošta"])
        ip_recognizer_hr = IpRecognizer(supported_language="hr")
        credit_card_recognizer_hr = CreditCardRecognizer(supported_language="hr")
        iban_recognizer_hr = IbanRecognizer(supported_language="hr")
        us_ssn_recognizer_hr = UsSsnRecognizer(supported_language="hr")
        phone_recognizer_hr = PhoneRecognizer(supported_language="hr")
        us_passport_recognizer_hr = UsPassportRecognizer(supported_language="hr")
         
        # Setting up Danish recognizers:
        spacy_recognizer_da = SpacyRecognizer(supported_language="da")
        email_recognizer_da = EmailRecognizer(supported_language="da", context=["e-mail", "post"])
        ip_recognizer_da = IpRecognizer(supported_language="da")
        credit_card_recognizer_da = CreditCardRecognizer(supported_language="da")
        iban_recognizer_da = IbanRecognizer(supported_language="da")
        us_ssn_recognizer_da = UsSsnRecognizer(supported_language="da")
        phone_recognizer_da = PhoneRecognizer(supported_language="da")
        us_passport_recognizer_da = UsPassportRecognizer(supported_language="da")
         
        # Setting up Dutch recognizers:
        spacy_recognizer_nl = SpacyRecognizer(supported_language="nl")
        email_recognizer_nl = EmailRecognizer(supported_language="nl", context=["e-mail", "mail"])
        ip_recognizer_nl = IpRecognizer(supported_language="nl")
        credit_card_recognizer_nl = CreditCardRecognizer(supported_language="nl")
        iban_recognizer_nl = IbanRecognizer(supported_language="nl")
        us_ssn_recognizer_nl = UsSsnRecognizer(supported_language="nl")
        phone_recognizer_nl = PhoneRecognizer(supported_language="nl")
        us_passport_recognizer_nl = UsPassportRecognizer(supported_language="nl")
         
        # Setting up Finnish recognizers:
        spacy_recognizer_fi = SpacyRecognizer(supported_language="fi")
        email_recognizer_fi = EmailRecognizer(supported_language="fi", context=["sähköposti", "postia"])
        ip_recognizer_fi = IpRecognizer(supported_language="fi")
        credit_card_recognizer_fi = CreditCardRecognizer(supported_language="fi")
        iban_recognizer_fi = IbanRecognizer(supported_language="fi")
        us_ssn_recognizer_fi = UsSsnRecognizer(supported_language="fi")
        phone_recognizer_fi = PhoneRecognizer(supported_language="fi")
        us_passport_recognizer_fi = UsPassportRecognizer(supported_language="fi")
         
        # Setting up Greek recognizers:
        spacy_recognizer_el = SpacyRecognizer(supported_language="el")
        email_recognizer_el = EmailRecognizer(supported_language="el", context=["ΗΛΕΚΤΡΟΝΙΚΗ ΔΙΕΥΘΥΝΣΗ", "ταχυδρομείο"])
        ip_recognizer_el = IpRecognizer(supported_language="el")
        credit_card_recognizer_el = CreditCardRecognizer(supported_language="el")
        iban_recognizer_el = IbanRecognizer(supported_language="el")
        us_ssn_recognizer_el = UsSsnRecognizer(supported_language="el")
        phone_recognizer_el = PhoneRecognizer(supported_language="el")
        us_passport_recognizer_el = UsPassportRecognizer(supported_language="el")
         
        # Setting up Italian recognizers:
        spacy_recognizer_it = SpacyRecognizer(supported_language="it")
        email_recognizer_it = EmailRecognizer(supported_language="it", context=["e-mail", "posta"])
        ip_recognizer_it = IpRecognizer(supported_language="it")
        credit_card_recognizer_it = CreditCardRecognizer(supported_language="it")
        iban_recognizer_it = IbanRecognizer(supported_language="it")
        us_ssn_recognizer_it = UsSsnRecognizer(supported_language="it")
        phone_recognizer_it = PhoneRecognizer(supported_language="it")
        us_passport_recognizer_it = UsPassportRecognizer(supported_language="it")
         
        # Setting up Japanese recognizers:
        spacy_recognizer_ja = SpacyRecognizer(supported_language="ja")
        email_recognizer_ja = EmailRecognizer(supported_language="ja", context=["Eメール", "郵便"])
        ip_recognizer_ja = IpRecognizer(supported_language="ja")
        credit_card_recognizer_ja = CreditCardRecognizer(supported_language="ja")
        iban_recognizer_ja = IbanRecognizer(supported_language="ja")
        us_ssn_recognizer_ja = UsSsnRecognizer(supported_language="ja")
        phone_recognizer_ja = PhoneRecognizer(supported_language="ja")
        us_passport_recognizer_ja = UsPassportRecognizer(supported_language="ja")
         
        # Setting up Korean recognizers:
        spacy_recognizer_ko = SpacyRecognizer(supported_language="ko")
        email_recognizer_ko = EmailRecognizer(supported_language="ko", context=["이메일", "우편"])
        ip_recognizer_ko = IpRecognizer(supported_language="ko")
        credit_card_recognizer_ko = CreditCardRecognizer(supported_language="ko")
        iban_recognizer_ko = IbanRecognizer(supported_language="ko")
        us_ssn_recognizer_ko = UsSsnRecognizer(supported_language="ko")
        phone_recognizer_ko = PhoneRecognizer(supported_language="ko")
        us_passport_recognizer_ko = UsPassportRecognizer(supported_language="ko")
         
        # Setting up Lithuanian recognizers:
        spacy_recognizer_lt = SpacyRecognizer(supported_language="lt")
        email_recognizer_lt = EmailRecognizer(supported_language="lt", context=["paštu", "Paštas"])
        ip_recognizer_lt = IpRecognizer(supported_language="lt")
        credit_card_recognizer_lt = CreditCardRecognizer(supported_language="lt")
        iban_recognizer_lt = IbanRecognizer(supported_language="lt")
        us_ssn_recognizer_lt = UsSsnRecognizer(supported_language="lt")
        phone_recognizer_lt = PhoneRecognizer(supported_language="lt")
        us_passport_recognizer_lt = UsPassportRecognizer(supported_language="lt")
         
        # Setting up Macedonian recognizers:
        spacy_recognizer_mk = SpacyRecognizer(supported_language="mk")
        email_recognizer_mk = EmailRecognizer(supported_language="mk", context=["е-пошта", "пошта"])
        ip_recognizer_mk = IpRecognizer(supported_language="mk")
        credit_card_recognizer_mk = CreditCardRecognizer(supported_language="mk")
        iban_recognizer_mk = IbanRecognizer(supported_language="mk")
        us_ssn_recognizer_mk = UsSsnRecognizer(supported_language="mk")
        phone_recognizer_mk = PhoneRecognizer(supported_language="mk")
        us_passport_recognizer_mk = UsPassportRecognizer(supported_language="mk")
         
        # Setting up Norwegian recognizers:
        spacy_recognizer_nb = SpacyRecognizer(supported_language="nb")
        email_recognizer_nb = EmailRecognizer(supported_language="nb", context=["e-post", "post"])
        ip_recognizer_nb = IpRecognizer(supported_language="nb")
        credit_card_recognizer_nb = CreditCardRecognizer(supported_language="nb")
        iban_recognizer_nb = IbanRecognizer(supported_language="nb")
        us_ssn_recognizer_nb = UsSsnRecognizer(supported_language="nb")
        phone_recognizer_nb = PhoneRecognizer(supported_language="nb")
        us_passport_recognizer_nb = UsPassportRecognizer(supported_language="nb")
         
        # Setting up Polish recognizers:
        spacy_recognizer_pl = SpacyRecognizer(supported_language="pl")
        email_recognizer_pl = EmailRecognizer(supported_language="pl", context=["e-mail", "Poczta"])
        ip_recognizer_pl = IpRecognizer(supported_language="pl")
        credit_card_recognizer_pl = CreditCardRecognizer(supported_language="pl")
        iban_recognizer_pl = IbanRecognizer(supported_language="pl")
        us_ssn_recognizer_pl = UsSsnRecognizer(supported_language="pl")
        phone_recognizer_pl = PhoneRecognizer(supported_language="pl")
        us_passport_recognizer_pl = UsPassportRecognizer(supported_language="pl")
         
        # Setting up Portuguese recognizers:
        spacy_recognizer_pt = SpacyRecognizer(supported_language="pt")
        email_recognizer_pt = EmailRecognizer(supported_language="pt", context=["e-mail", "correspondência"])
        ip_recognizer_pt = IpRecognizer(supported_language="pt")
        credit_card_recognizer_pt = CreditCardRecognizer(supported_language="pt")
        iban_recognizer_pt = IbanRecognizer(supported_language="pt")
        us_ssn_recognizer_pt = UsSsnRecognizer(supported_language="pt")
        phone_recognizer_pt = PhoneRecognizer(supported_language="pt")
        us_passport_recognizer_pt = UsPassportRecognizer(supported_language="pt")
         
        # Setting up Romanian recognizers:
        spacy_recognizer_ro = SpacyRecognizer(supported_language="ro")
        email_recognizer_ro = EmailRecognizer(supported_language="ro", context=["e-mail", "Poștă"])
        ip_recognizer_ro = IpRecognizer(supported_language="ro")
        credit_card_recognizer_ro = CreditCardRecognizer(supported_language="ro")
        iban_recognizer_ro = IbanRecognizer(supported_language="ro")
        us_ssn_recognizer_ro = UsSsnRecognizer(supported_language="ro")
        phone_recognizer_ro = PhoneRecognizer(supported_language="ro")
        us_passport_recognizer_ro = UsPassportRecognizer(supported_language="ro")
         
        # Setting up Russian recognizers:
        spacy_recognizer_ru = SpacyRecognizer(supported_language="ru")
        email_recognizer_ru = EmailRecognizer(supported_language="ru", context=["электронная почта", "почта"])
        ip_recognizer_ru = IpRecognizer(supported_language="ru")
        credit_card_recognizer_ru = CreditCardRecognizer(supported_language="ru")
        iban_recognizer_ru = IbanRecognizer(supported_language="ru")
        us_ssn_recognizer_ru = UsSsnRecognizer(supported_language="ru")
        phone_recognizer_ru = PhoneRecognizer(supported_language="ru")
        us_passport_recognizer_ru = UsPassportRecognizer(supported_language="ru")
         
        # Setting up Swedish recognizers:
        spacy_recognizer_sv = SpacyRecognizer(supported_language="sv")
        email_recognizer_sv = EmailRecognizer(supported_language="sv", context=["e-post", "post"])
        ip_recognizer_sv = IpRecognizer(supported_language="sv")
        credit_card_recognizer_sv = CreditCardRecognizer(supported_language="sv")
        iban_recognizer_sv = IbanRecognizer(supported_language="sv")
        us_ssn_recognizer_sv = UsSsnRecognizer(supported_language="sv")
        phone_recognizer_sv = PhoneRecognizer(supported_language="sv")
        us_passport_recognizer_sv = UsPassportRecognizer(supported_language="sv")
         
        # Setting up Ukranian recognizers:
        spacy_recognizer_uk = SpacyRecognizer(supported_language="uk")
        email_recognizer_uk = EmailRecognizer(supported_language="uk", context=["електронною поштою", "пошта"])
        ip_recognizer_uk = IpRecognizer(supported_language="uk")
        credit_card_recognizer_uk = CreditCardRecognizer(supported_language="uk")
        iban_recognizer_uk = IbanRecognizer(supported_language="uk")
        us_ssn_recognizer_uk = UsSsnRecognizer(supported_language="uk")
        phone_recognizer_uk = PhoneRecognizer(supported_language="uk")
        us_passport_recognizer_uk = UsPassportRecognizer(supported_language="uk")
        

        registry = RecognizerRegistry()
        # 
        ## Add recognizers to registry
        registry.add_recognizer(email_recognizer_en)
        registry.add_recognizer(spacy_recognizer_en)
        registry.add_recognizer(ip_recognizer_en)
        registry.add_recognizer(credit_card_recognizer_en)
        registry.add_recognizer(iban_recognizer_en)
        registry.add_recognizer(us_ssn_recognizer_en)
        registry.add_recognizer(phone_recognizer_en)
        registry.add_recognizer(us_passport_recognizer_en)

        registry.add_recognizer(email_recognizer_es)
        registry.add_recognizer(spacy_recognizer_es)
        registry.add_recognizer(ip_recognizer_es)
        registry.add_recognizer(credit_card_recognizer_es)
        registry.add_recognizer(iban_recognizer_es)
        registry.add_recognizer(us_ssn_recognizer_es)
        registry.add_recognizer(phone_recognizer_es)
        registry.add_recognizer(us_passport_recognizer_es)

        registry.add_recognizer(email_recognizer_fr)
        registry.add_recognizer(spacy_recognizer_fr)
        registry.add_recognizer(ip_recognizer_fr)
        registry.add_recognizer(credit_card_recognizer_fr)
        registry.add_recognizer(iban_recognizer_fr)
        registry.add_recognizer(us_ssn_recognizer_fr)
        registry.add_recognizer(phone_recognizer_fr)
        registry.add_recognizer(us_passport_recognizer_fr)

        registry.add_recognizer(email_recognizer_de)
        registry.add_recognizer(spacy_recognizer_de)
        registry.add_recognizer(ip_recognizer_de)
        registry.add_recognizer(credit_card_recognizer_de)
        registry.add_recognizer(iban_recognizer_de)
        registry.add_recognizer(us_ssn_recognizer_de)
        registry.add_recognizer(phone_recognizer_de)
        registry.add_recognizer(us_passport_recognizer_de)

        registry.add_recognizer(email_recognizer_ca)
        registry.add_recognizer(spacy_recognizer_ca)
        registry.add_recognizer(ip_recognizer_ca)
        registry.add_recognizer(credit_card_recognizer_ca)
        registry.add_recognizer(iban_recognizer_ca)
        registry.add_recognizer(us_ssn_recognizer_ca)
        registry.add_recognizer(phone_recognizer_ca)
        registry.add_recognizer(us_passport_recognizer_ca)

        registry.add_recognizer(email_recognizer_zh)
        registry.add_recognizer(spacy_recognizer_zh)
        registry.add_recognizer(ip_recognizer_zh)
        registry.add_recognizer(credit_card_recognizer_zh)
        registry.add_recognizer(iban_recognizer_zh)
        registry.add_recognizer(us_ssn_recognizer_zh)
        registry.add_recognizer(phone_recognizer_zh)
        registry.add_recognizer(us_passport_recognizer_zh)

        registry.add_recognizer(email_recognizer_hr)
        registry.add_recognizer(spacy_recognizer_hr)
        registry.add_recognizer(ip_recognizer_hr)
        registry.add_recognizer(credit_card_recognizer_hr)
        registry.add_recognizer(iban_recognizer_hr)
        registry.add_recognizer(us_ssn_recognizer_hr)
        registry.add_recognizer(phone_recognizer_hr)
        registry.add_recognizer(us_passport_recognizer_hr)

        registry.add_recognizer(email_recognizer_da)
        registry.add_recognizer(spacy_recognizer_da)
        registry.add_recognizer(ip_recognizer_da)
        registry.add_recognizer(credit_card_recognizer_da)
        registry.add_recognizer(iban_recognizer_da)
        registry.add_recognizer(us_ssn_recognizer_da)
        registry.add_recognizer(phone_recognizer_da)
        registry.add_recognizer(us_passport_recognizer_da)

        registry.add_recognizer(email_recognizer_nl)
        registry.add_recognizer(spacy_recognizer_nl)
        registry.add_recognizer(ip_recognizer_nl)
        registry.add_recognizer(credit_card_recognizer_nl)
        registry.add_recognizer(iban_recognizer_nl)
        registry.add_recognizer(us_ssn_recognizer_nl)
        registry.add_recognizer(phone_recognizer_nl)
        registry.add_recognizer(us_passport_recognizer_nl)

        registry.add_recognizer(email_recognizer_fi)
        registry.add_recognizer(spacy_recognizer_fi)
        registry.add_recognizer(ip_recognizer_fi)
        registry.add_recognizer(credit_card_recognizer_fi)
        registry.add_recognizer(iban_recognizer_fi)
        registry.add_recognizer(us_ssn_recognizer_fi)
        registry.add_recognizer(phone_recognizer_fi)
        registry.add_recognizer(us_passport_recognizer_fi)

        registry.add_recognizer(email_recognizer_el)
        registry.add_recognizer(spacy_recognizer_el)
        registry.add_recognizer(ip_recognizer_el)
        registry.add_recognizer(credit_card_recognizer_el)
        registry.add_recognizer(iban_recognizer_el)
        registry.add_recognizer(us_ssn_recognizer_el)
        registry.add_recognizer(phone_recognizer_el)
        registry.add_recognizer(us_passport_recognizer_el)

        registry.add_recognizer(email_recognizer_it)
        registry.add_recognizer(spacy_recognizer_it)
        registry.add_recognizer(ip_recognizer_it)
        registry.add_recognizer(credit_card_recognizer_it)
        registry.add_recognizer(iban_recognizer_it)
        registry.add_recognizer(us_ssn_recognizer_it)
        registry.add_recognizer(phone_recognizer_it)
        registry.add_recognizer(us_passport_recognizer_it)

        registry.add_recognizer(email_recognizer_ja)
        registry.add_recognizer(spacy_recognizer_ja)
        registry.add_recognizer(ip_recognizer_ja)
        registry.add_recognizer(credit_card_recognizer_ja)
        registry.add_recognizer(iban_recognizer_ja)
        registry.add_recognizer(us_ssn_recognizer_ja)
        registry.add_recognizer(phone_recognizer_ja)
        registry.add_recognizer(us_passport_recognizer_ja)

        registry.add_recognizer(email_recognizer_ko)
        registry.add_recognizer(spacy_recognizer_ko)
        registry.add_recognizer(ip_recognizer_ko)
        registry.add_recognizer(credit_card_recognizer_ko)
        registry.add_recognizer(iban_recognizer_ko)
        registry.add_recognizer(us_ssn_recognizer_ko)
        registry.add_recognizer(phone_recognizer_ko)
        registry.add_recognizer(us_passport_recognizer_ko)

        registry.add_recognizer(email_recognizer_lt)
        registry.add_recognizer(spacy_recognizer_lt)
        registry.add_recognizer(ip_recognizer_lt)
        registry.add_recognizer(credit_card_recognizer_lt)
        registry.add_recognizer(iban_recognizer_lt)
        registry.add_recognizer(us_ssn_recognizer_lt)
        registry.add_recognizer(phone_recognizer_lt)
        registry.add_recognizer(us_passport_recognizer_lt)

        registry.add_recognizer(email_recognizer_mk)
        registry.add_recognizer(spacy_recognizer_mk)
        registry.add_recognizer(ip_recognizer_mk)
        registry.add_recognizer(credit_card_recognizer_mk)
        registry.add_recognizer(iban_recognizer_mk)
        registry.add_recognizer(us_ssn_recognizer_mk)
        registry.add_recognizer(phone_recognizer_mk)
        registry.add_recognizer(us_passport_recognizer_mk)

        registry.add_recognizer(email_recognizer_nb)
        registry.add_recognizer(spacy_recognizer_nb)
        registry.add_recognizer(ip_recognizer_nb)
        registry.add_recognizer(credit_card_recognizer_nb)
        registry.add_recognizer(iban_recognizer_nb)
        registry.add_recognizer(us_ssn_recognizer_nb)
        registry.add_recognizer(phone_recognizer_nb)
        registry.add_recognizer(us_passport_recognizer_nb)

        registry.add_recognizer(email_recognizer_pl)
        registry.add_recognizer(spacy_recognizer_pl)
        registry.add_recognizer(ip_recognizer_pl)
        registry.add_recognizer(credit_card_recognizer_pl)
        registry.add_recognizer(iban_recognizer_pl)
        registry.add_recognizer(us_ssn_recognizer_pl)
        registry.add_recognizer(phone_recognizer_pl)
        registry.add_recognizer(us_passport_recognizer_pl)

        registry.add_recognizer(email_recognizer_pt)
        registry.add_recognizer(spacy_recognizer_pt)
        registry.add_recognizer(ip_recognizer_pt)
        registry.add_recognizer(credit_card_recognizer_pt)
        registry.add_recognizer(iban_recognizer_pt)
        registry.add_recognizer(us_ssn_recognizer_pt)
        registry.add_recognizer(phone_recognizer_pt)
        registry.add_recognizer(us_passport_recognizer_pt)

        registry.add_recognizer(email_recognizer_ro)
        registry.add_recognizer(spacy_recognizer_ro)
        registry.add_recognizer(ip_recognizer_ro)
        registry.add_recognizer(credit_card_recognizer_ro)
        registry.add_recognizer(iban_recognizer_ro)
        registry.add_recognizer(us_ssn_recognizer_ro)
        registry.add_recognizer(phone_recognizer_ro)
        registry.add_recognizer(us_passport_recognizer_ro)

        registry.add_recognizer(email_recognizer_ru)
        registry.add_recognizer(spacy_recognizer_ru)
        registry.add_recognizer(ip_recognizer_ru)
        registry.add_recognizer(credit_card_recognizer_ru)
        registry.add_recognizer(iban_recognizer_ru)
        registry.add_recognizer(us_ssn_recognizer_ru)
        registry.add_recognizer(phone_recognizer_ru)
        registry.add_recognizer(us_passport_recognizer_ru)

        registry.add_recognizer(email_recognizer_sv)
        registry.add_recognizer(spacy_recognizer_sv)
        registry.add_recognizer(ip_recognizer_sv)
        registry.add_recognizer(credit_card_recognizer_sv)
        registry.add_recognizer(iban_recognizer_sv)
        registry.add_recognizer(us_ssn_recognizer_sv)
        registry.add_recognizer(phone_recognizer_sv)
        registry.add_recognizer(us_passport_recognizer_sv)

        registry.add_recognizer(email_recognizer_uk)
        registry.add_recognizer(spacy_recognizer_uk)
        registry.add_recognizer(ip_recognizer_uk)
        registry.add_recognizer(credit_card_recognizer_uk)
        registry.add_recognizer(iban_recognizer_uk)
        registry.add_recognizer(us_ssn_recognizer_uk)
        registry.add_recognizer(phone_recognizer_uk)
        registry.add_recognizer(us_passport_recognizer_uk)


        self.engine = AnalyzerEngine(registry=registry,nlp_engine=multilingual_nlp_engine, supported_languages=["en", "de", "fr", "es"])


        self.logger.info(WELCOME_MESSAGE)

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result."""
            return "Presidio Analyzer service is up"

        @self.app.route("/analyze", methods=["POST"])
        def analyze() -> Tuple[str, int]:
            """Execute the analyzer function."""
            # Parse the request params
            try:
                req_data = AnalyzerRequest(request.get_json())
                if not req_data.text:
                    raise Exception("No text provided")

                if not req_data.language:
                    raise Exception("No language provided")

                recognizer_result_list = self.engine.analyze(
                    text=req_data.text,
                    language=req_data.language,
                    correlation_id=req_data.correlation_id,
                    score_threshold=req_data.score_threshold,
                    entities=req_data.entities,
                    return_decision_process=req_data.return_decision_process,
                    ad_hoc_recognizers=req_data.ad_hoc_recognizers,
                    context=req_data.context,
                )

                return Response(
                    json.dumps(
                        recognizer_result_list,
                        default=lambda o: o.to_dict(),
                        sort_keys=True,
                    ),
                    content_type="application/json",
                )
            except TypeError as te:
                error_msg = (
                    f"Failed to parse /analyze request "
                    f"for AnalyzerEngine.analyze(). {te.args[0]}"
                )
                self.logger.error(error_msg)
                return jsonify(error=error_msg), 400

            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.analyze(). {e}"
                )
                return jsonify(error=e.args[0]), 500

        @self.app.route("/bulkanalyze", methods=["POST"])
        def bulkAnalyze() -> Tuple[int,Tuple[str, int]]:
            """Execute the analyzer function for multiple inputs."""
            # Parse the request params

            results_list = []
            req_data_list = request.get_json()

            for req_data_obj in req_data_list:
                try:
                    req_data = AnalyzerRequest(req_data_obj)

                    if not req_data.text:
                        raise Exception("No text provided")

                    if not req_data.language:
                        raise Exception("No language provided")

                    recognizer_result_list = self.engine.analyze(
                        text=req_data.text,
                        language=req_data.language,
                        correlation_id=req_data.correlation_id,
                        score_threshold=req_data.score_threshold,
                        entities=req_data.entities,
                        return_decision_process=req_data.return_decision_process,
                        ad_hoc_recognizers=req_data.ad_hoc_recognizers,
                        context=req_data.context,
                    )

                    results_list.append(AnalyzerResponse(req_data_obj['id'],recognizer_result_list))

                except TypeError as te:
                    error_msg = (
                        f"Failed to parse /bulkAnalyze request "
                        f"for AnalyzerEngine.analyze(). {te.args[0]}"
                    )
                    self.logger.error(error_msg)
                    # return jsonify(error=error_msg), 400
                    results_list.append(AnalyzerResponse(req_data_obj['id'],[],error_msg))

                except Exception as e:
                    self.logger.error(
                        f"A fatal error occurred during execution of "
                        f"AnalyzerEngine.analyze(). {e}"
                    )
                    # return jsonify(error=e.args[0]), 500
                    results_list.append(AnalyzerResponse(req_data_obj['id'],[],e.args[0]))
            
            return Response(
                    json.dumps(
                        results_list,
                        default=lambda o: o.to_dict(),
                        sort_keys=True,
                    ),
                    content_type="application/json",
                )

        @self.app.route("/recognizers", methods=["GET"])
        def recognizers() -> Tuple[str, int]:
            """Return a list of supported recognizers."""
            language = request.args.get("language")
            try:
                recognizers_list = self.engine.get_recognizers(language)
                names = [o.name for o in recognizers_list]
                return jsonify(names), 200
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.get_recognizers(). {e}"
                )
                return jsonify(error=e.args[0]), 500

        @self.app.route("/supportedentities", methods=["GET"])
        def supported_entities() -> Tuple[str, int]:
            """Return a list of supported entities."""
            language = request.args.get("language")
            try:
                entities_list = self.engine.get_supported_entities(language)
                return jsonify(entities_list), 200
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.supported_entities(). {e}"
                )
                return jsonify(error=e.args[0]), 500

        @self.app.errorhandler(HTTPException)
        def http_exception(e):
            return jsonify(error=e.description), e.code


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
