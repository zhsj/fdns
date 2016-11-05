import asyncio
from .base import HTTPResolver
from .utils import http_get
from dnslib import QTYPE


class HTTP114Resolver(HTTPResolver):
    def __init__(self):
        self.end_point = ("http://114.114.114.114/d?dn={qname}&"
                          "ip={client_ip}&ttl=y&type={qtype}")

    async def resolve(self, qname, qtype, client_ip):
        if qtype not in (1, 28):
            raise Exception("Not Supported Query Type")
        url = self.end_point.format(
            qname=qname, qtype=QTYPE[qtype], client_ip=client_ip
        )
        data = await http_get(url)
        if len(data) < 1:
            return None

        def gen_rr(ans):
            d, ttl = ans.split(',', 1)
            return (qname, ttl, qtype, d)

        return [gen_rr(ans) for ans in data.split(';')]


if __name__ == '__main__':
    async def test_dns():
        data = await HTTP114Resolver().resolve('www.cloudflare.com',
                                               28, '1.1.1.1')
        print(data)
        data = await HTTP114Resolver().resolve('www.114dns.com',
                                               1, '1.1.1.1')
        print(data)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_dns())
