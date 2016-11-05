import asyncio
import dnslib
import logging
from .provider.http.google import HTTPGoogleResolver

logging.basicConfig(level=logging.DEBUG)
_LOG = logging.getLogger(__name__)

pseudo_edns_client = '202.141.162.124'


class DNSServerProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.resolver = HTTPGoogleResolver()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        _LOG.info('Received from '+str(addr))
        asyncio.ensure_future(self.handle(data, addr))

    async def handle(self, data, addr):
        record = dnslib.DNSRecord.parse(data)
        question = record.questions[0]
        qname = str(question.qname)
        qtype = question.qtype
        ans = await self.resolver.resolve(qname, qtype, pseudo_edns_client)
        for rr in ans:
            zone_format = "{rname} {ttl} IN {rtype_name} {rdata}"
            _rr = {
                'rname': rr[0],
                'ttl': rr[1],
                'rtype_name': dnslib.QTYPE.forward[rr[2]],
                'rdata': rr[3]
            }
            zone = zone_format.format(**_rr)
            _LOG.debug(zone)
            record.add_answer(*dnslib.RR.fromZone(zone))
        _LOG.info('Send to '+str(addr))
        self.transport.sendto(record.pack(), addr)


class DNSServer:
    def __init__(self, loop):
        self.loop = loop

    async def start(self):
        _LOG.info("Starting UDP server")
        self.transport, self.proto = await self.loop.create_datagram_endpoint(
            DNSServerProtocol, local_addr=('127.0.0.1', 9999))


def main():
    async def stop(self):
        self.transport.close()

    loop = asyncio.get_event_loop()
    server = DNSServer(loop)
    asyncio.ensure_future(server.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(server.stop())
    loop.close()

if __name__ == '__main__':
    main()
