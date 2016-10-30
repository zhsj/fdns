from urllib import request
from .base import HTTPResolver


class DNSPodResolver(HTTPResolver):
    def __init__(self):
        self.end_point = ("http://119.29.29.29/d?dn={qname}&"
                          "ip={client_ip}&ttl=1")

    def resolve(self, qname, qtype, client_ip):
        if qtype not in ('A',):
            raise Exception("Not Supported Query Type")
        req = request.urlopen(self.end_point.format(qname=qname,
                                                    client_ip=client_ip))
        result = req.read().decode().split(',')
        if len(result) != 2:
            return None
        ttl = result[1]
        for ans in result[0].split(';'):
            yield (1, ttl, ans)


if __name__ == '__main__':
    print(list(DNSPodResolver().resolve('www.cloudflare.com', 'A', '1.1.1.1')))
    print(list(DNSPodResolver().resolve('www.dnspod.com', 'A', '1.1.1.1')))
