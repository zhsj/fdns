import json
from urllib import request
from .base import HTTPResolver


class GoogleResolver(HTTPResolver):
    def __init__(self):
        self.end_point = ("https://dns.google.com/resolve?name={qname}&"
                          "type={qtype}&edns_client_subnet={client_ip}")

    def resolve(self, qname, qtype, client_ip):
        req = request.urlopen(self.end_point.format(qname=qname, qtype=qtype,
                                                    client_ip=client_ip))
        result = json.loads(req.read().decode())
        for ans in result['Answer']:
            yield (ans['type'], ans['TTL'], ans['data'])


if __name__ == '__main__':
    print(list(GoogleResolver().resolve('www.cloudflare.com', 'A', '1.1.1.1')))
    print(list(GoogleResolver().resolve('www.google.com', 'A', '1.1.1.1')))
