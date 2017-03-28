from abc import ABCMeta, abstractmethod

class Source_Interface(object):
    """Trying to make an interface for each source of digest"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_digest(self): raise NotImplementedError
