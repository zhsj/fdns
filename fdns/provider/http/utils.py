import urllib.parse
import asyncio
import logging
import aiohttp
import async_timeout


_LOG = logging.getLogger()
session = aiohttp.ClientSession()


async def http_get(url):
    with async_timeout.timeout(5):
        async with session.get(url) as resp:
            assert resp.status == 200
            data = await resp.read()
            return data.decode()

async def http_get_old(url):
    url = urllib.parse.urlsplit(url)
    if url.scheme == 'https':
        connect = asyncio.open_connection(url.hostname, 443, ssl=True)
    else:
        connect = asyncio.open_connection(url.hostname, 80)
    reader, writer = await connect
    path = url.path
    if url.path == '':
        path = '/'
    if url.query != '':
        path += '?' + url.query
    query = (
        'GET {path} HTTP/1.0\r\n'
        'Host: {hostname}\r\n'
        '\r\n'
    ).format(path=path, hostname=url.hostname)
    _LOG.debug(query)
    writer.write(query.encode())
    while True:
        line = await reader.readline()
        if line == b'\r\n':
            break
    data = await reader.readline()
    writer.close()
    return data.decode()


if __name__ == '__main__':
    async def test_url():
        data = await http_get('http://example.com')
        print(data)
        data = await http_get('http://example.com')
        print(data)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_url())
