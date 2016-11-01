import asyncio
import dnslib
import json
import urllib.parse
import logging

logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

DNS_API = 'https://dns.google.com/resolve?name=%s&type=%s&edns_client_subnet=%s' # noqa
pseudo_edns_client = '202.141.162.124'


class DNSServerProtocol(asyncio.DatagramProtocol):
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
        url = DNS_API % (qname, qtype, pseudo_edns_client)
        data = await self.req(url)
        answers = json.loads(data).get('Answer')
        for answer in answers:
            rtype = dnslib.QTYPE.forward[answer['type']]
            rr = {
                'rname': answer['name'],
                'ttl': answer['TTL'],
                'rtype': answer['type'],
                'rdata': getattr(dnslib, rtype)(answer['data'])
            }
            record.add_answer(dnslib.RR(**rr))
        _LOG.info('Send to '+str(addr))
        self.transport.sendto(record.pack(), addr)

    async def req(self, url):
        url = urllib.parse.urlsplit(url)
        if url.scheme == 'https':
            connect = asyncio.open_connection(url.hostname, 443, ssl=True)
        else:
            connect = asyncio.open_connection(url.hostname, 80)
        reader, writer = await connect
        query = ('GET {path}?{query} HTTP/1.0\r\n'
                 'Host: {hostname}\r\n'
                 '\r\n').format(path=url.path, query=url.query,
                                hostname=url.hostname)
        writer.write(query.encode())
        while True:
            line = await reader.readline()
            if line == b'\r\n':
                break
        data = await reader.readline()
        writer.close()
        return data.decode()


class DNSServer:
    def __init__(self, loop):
        self.loop = loop

    async def start(self):
        _LOG.info("Starting UDP server")
        self.transport, self.proto = await self.loop.create_datagram_endpoint(
            DNSServerProtocol, local_addr=('127.0.0.1', 9999))

    async def stop(self):
        self.transport.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server = DNSServer(loop)
    asyncio.ensure_future(server.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(server.stop())
    loop.close()
