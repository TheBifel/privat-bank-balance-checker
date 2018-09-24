# PrivatBank balance checker
This is simple server and client aplications for checking your balance in PrivatBank

# Some explaining:
# 1)
If you want jast send request to PrivatBank (without server and client) use this code:

  ``` python
  def get_signature(password, data):
    return hashlib.sha1(bytes(hashlib.md5(bytes(data + password, 'utf8')).hexdigest(), 'utf8')).hexdigest()

def parse_request_body(post_body):
    res = requests.post('https://api.privatbank.ua/p24api/balance', post_body).text
    founded_balance = re.search('<av_balance>(.*?)</av_balance>', res)
    if founded_balance:
        return founded_balance.group(1)
    err = re.search('message ="(.*?)" /', res)
    if err:
        return err.group(1)
    return "Error parsing XML: not well-formed"

if __name__ == "__main__":
    password = "password from merchant"
    id = "merchant id"
    card = "card number"
    data = '<oper>cmt</oper><wait>0</wait><test>0</test><payment id=""><prop name="cardnum" value="' + card \
            + '"></prop><prop name="country" value="UA"></prop></payment>'
    signature = get_signature(password, data)

    body = '<?xml version="1.0" encoding="UTF-8"?><request version="1.0"><merchant><id>' + id + \
                           '</id><signature>' + signature + '</signature></merchant><data>' + data + '</data></request>'
    print(parse_request_body(body)
  ```
# 2)
We sending password in this request
  ``` json
{"password":"M48QhNgPA8Woz7Bqs0m2NEf", "cards":["UNIVERSAL", "PAYMENT"], "format":"U > %s/nP > %s"}
```
and we checking if hash of this password equals to our signature
  ``` python
  def do_POST(self):
    ...
    if hashlib.sha512(str(json_from_body["password"]).encode()).hexdigest() != SIGNATURE:
        self.do_ERROR(401, "Invalid password")
        return
    ...
  ```
  ``` python
  SIGNATURE = '2c06bca711a3a45a8a3df264f3e85678030c75347b513332621468db9cd2aa6cf50f1b3a7aecf20c5e4246c38d66f2d552b78bf11d9a6f087418712212e9d321'
  ```
  
  It's for secure of your data from somebody.
  PS: Signature not for this password.
