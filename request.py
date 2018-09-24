import requests

if __name__ == "__main__":
    print(requests.post('http://localhost:5558/', '{"password" : "M48QhNgPA8Woz7Bqs0m2NEf", "cards" : ["UNIVERSAL", "PAYMENT"], "format" : "U > %s/nP > %s"}').text)
