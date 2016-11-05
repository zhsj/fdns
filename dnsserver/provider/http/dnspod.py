import asyncio
from .base import HTTPResolver
from .utils import http_get


class HTTPDNSPodResolver(HTTPResolver):
    def __init__(self):
        self.end_point = ("http://119.29.29.29/d?dn={qname}&"
                          "ip={client_ip}&ttl=1")

    async def resolve(self, qname, qtype, client_ip):
        if qtype not in (1,):
            raise Exception("Not Supported Query Type")
        url = self.end_point.format(
            qname=qname, client_ip=client_ip
        )
        data = await http_get(url)
        result = data.split(',')
        if len(result) != 2:
            return None
        ttl = result[1]
        return [(qname, ttl, 1, ans) for ans in result[0].split(';')]


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    async def test_dns():
        data = await HTTPDNSPodResolver().resolve('www.cloudflare.com',
                                                  1, '1.1.1.1')
        print(data)
        data = await HTTPDNSPodResolver().resolve('www.dnspod.com',
                                                  1, '1.1.1.1')
        print(data)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_dns())
