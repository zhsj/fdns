import abc


class HTTPResolver(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def resolve(qname, qtype, client_ip):
        pass
