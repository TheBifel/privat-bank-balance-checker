from http.server import BaseHTTPRequestHandler, HTTPServer

import hashlib
import re
import requests
import json

SIGNATURE = '2c06bca711a3a45a8a3df264f3e85678030c75347b513332621468db9cd2aa6cf50f1b3a7aecf20c5e4246c38d66f2d552b78bf' \
            '11d9a6f087418712212e9d321'

XML_FOR_PAYMENT_CARD = ""
XML_FOR_UNIVERSAL_CARD = ""
CARD_CASES = {}


class Handler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def send(self, code, massage):
        self.send_response(code)
        self.send_header('Content-type', 'text')
        self.end_headers()
        self.wfile.write(massage.encode())
        print("Code: " + str(code) + " massage: " + massage)

    def do_ERROR(self, code, massage):
        self.send(code, "Get out!\n" + massage)

    def do_GET(self):
        self.do_ERROR(400, "Invalid get method")

    def do_POST(self):
        post_body = bytes(self.rfile.read(int(self.headers['content-length']))).decode()
        if post_body == "":
            self.do_ERROR(400, "Empty body")
            return
        try:
            json_from_body = json.loads(post_body)
        except json.decoder.JSONDecodeError:
            self.do_ERROR(417, "Can't load json from post body")
            return

        if "password" not in json_from_body:
            self.do_ERROR(404, "Can't found password")
            return
        if "format" not in json_from_body:
            self.do_ERROR(404, "Format required")
            return
        if "cards" not in json_from_body:
            self.do_ERROR(404, "Can't found cards")
            return

        if hashlib.sha512(str(json_from_body["password"]).encode()).hexdigest() != SIGNATURE:
            self.do_ERROR(401, "Invalid password")
            return

        cards = []
        for card in json_from_body["cards"]:
            xml_for_card = CARD_CASES.get(card.strip())
            if xml_for_card:
                cards.append(self.parse_request_body(xml_for_card))
        if not cards:
            self.do_ERROR(404, "Card searching error")
            return

        try:
            self.send(200, str(json_from_body["format"]).replace("/n", "\n") % tuple(cards))
        except TypeError:
            self.do_ERROR(400, "Formatting error")
            return

    @staticmethod
    def parse_request_body(post_body):
        res = requests.post('https://api.privatbank.ua/p24api/balance', post_body).text
        founded_balance = re.search('<av_balance>(.*?)</av_balance>', res)
        if founded_balance:
            return founded_balance.group(1)
        err = re.search('message ="(.*?)" /', res)
        if err:
            return err.group(1)
        return "Error parsing XML: not well-formed"


def get_signature(password, data):
    return hashlib.sha1(bytes(hashlib.md5(bytes(data + password, 'utf8')).hexdigest(), 'utf8')).hexdigest()


if __name__ == "__main__":
    print("Starting...")
    passwordP = "password from merchant"
    passwordU = "password from merchant"
    idP = "merchant id"
    idU = "merchant id"
    cardP = "card number"
    cardU = "card number"
    dataP = '<oper>cmt</oper><wait>0</wait><test>0</test><payment id=""><prop name="cardnum" value="' + cardP \
            + '"></prop><prop name="country" value="UA"></prop></payment>'
    dataU = '<oper>cmt</oper><wait>0</wait><test>0</test><payment id=""><prop name="cardnum" value="' + cardU \
            + '"></prop><prop name="country" value="UA"></prop></payment>'
    signatureP = get_signature(passwordP, dataP)
    signatureU = get_signature(passwordU, dataU)

    XML_FOR_PAYMENT_CARD = '<?xml version="1.0" encoding="UTF-8"?><request version="1.0"><merchant><id>' + idP + \
                           '</id><signature>' + signatureP + '</signature></merchant><data>' + dataP + '</data></request>'

    XML_FOR_UNIVERSAL_CARD = '<?xml version="1.0" encoding="UTF-8"?><request version="1.0"><merchant><id>' + idU + \
                           '</id><signature>' + signatureU + '</signature></merchant><data>' + dataU + '</data></request>'
    CARD_CASES = {'PAYMENT': XML_FOR_PAYMENT_CARD, 'UNIVERSAL': XML_FOR_UNIVERSAL_CARD}
    print("Started")
    HTTPServer(('', 5558), Handler).serve_forever()
