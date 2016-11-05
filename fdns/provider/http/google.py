import json
import asyncio
from .base import HTTPResolver
from .utils import http_get


class HTTPGoogleResolver(HTTPResolver):
    def __init__(self):
        self.end_point = ("https://dns.google.com/resolve?name={qname}&"
                          "type={qtype}&edns_client_subnet={client_ip}")

    async def resolve(self, qname, qtype, client_ip):
        url = self.end_point.format(
            qname=qname, qtype=qtype, client_ip=client_ip
        )
        data = await http_get(url)
        result = json.loads(data)
        return [(ans['name'], ans['TTL'], ans['type'], ans['data'])
                for ans in result['Answer']]


if __name__ == '__main__':
    async def test_dns():
        data = await HTTPGoogleResolver().resolve('www.cloudflare.com',
                                                  28, '1.1.1.1')
        print(data)
        data = await HTTPGoogleResolver().resolve('www.google.com',
                                                  1, '1.1.1.1')
        print(data)
        data = await HTTPGoogleResolver().resolve('www.baidu.com',
                                                  1, '1.1.1.1')
        print(data)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_dns())
