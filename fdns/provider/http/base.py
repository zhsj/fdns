import abc


class HTTPResolver(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    async def resolve(qname, qtype, client_ip):
        """
        Returns:
            (rname, ttl, rtype, data)
        """
        pass
