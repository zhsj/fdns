from urllib import request
from .base import HTTPResolver


class DNS114Resolver(HTTPResolver):
    def __init__(self):
        self.end_point = ("http://114.114.114.114/d?dn={qname}&"
                          "ip={client_ip}&ttl=y&type={qtype}")

    def resolve(self, qname, qtype, client_ip):
        if qtype not in ('A', 'AAAA'):
            raise Exception("Not Supported Query Type")
        req = request.urlopen(self.end_point.format(qname=qname, qtype=qtype,
                                                    client_ip=client_ip))
        result = req.read().decode()
        if len(result) < 1:
            return None
        for ans in result.split(';'):
            _ans = ans.split(',')
            yield (1, _ans[1], _ans[0])


if __name__ == '__main__':
    print(list(DNS114Resolver().resolve('www.cloudflare.com', 'A', '1.1.1.1')))
    print(list(DNS114Resolver().resolve('www.114dns.com', 'A', '1.1.1.1')))
