import asyncio
import dnslib
import json
from urllib import request

DNS_API = 'https://dns.google.com/resolve?name=%s&type=%s&edns_client_subnet=%s' # noqa
pseudo_edns_client = '202.141.162.124'


class DNSServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print('Received from ', str(addr))
        record = dnslib.DNSRecord.parse(data)
        question = record.questions[0]
        qname = str(question.qname)
        qtype = question.qtype
        req = request.urlopen(DNS_API % (qname, qtype, pseudo_edns_client))
        answers = json.loads(req.read().decode()).get('Answer')
        for answer in answers:
            rtype = dnslib.QTYPE.forward[answer['type']]
            rr = {
                'rname': answer['name'],
                'ttl': answer['TTL'],
                'rtype': answer['type'],
                'rdata': getattr(dnslib, rtype)(answer['data'])
            }
            record.add_answer(dnslib.RR(**rr))
        print('Send to ', str(addr))
        self.transport.sendto(record.pack(), addr)

loop = asyncio.get_event_loop()
print("Starting UDP server")
# One protocol instance will be created to serve all client requests
listen = loop.create_datagram_endpoint(
    DNSServerProtocol, local_addr=('127.0.0.1', 9999))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
