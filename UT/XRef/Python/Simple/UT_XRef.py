# e = External
# a = alias
import mo1
from mo2 import c1 as c1a
import ns1.mo2 as mo2a
from si1 import Singleton as S1

s1 = S1()


# Functions
def f0(p0):
    mo1.m( p0, p2=None )


# Classes
class c1( object ):
    def __init__(self, p0='c0 called'):
        self._p0 = p0
        s1.m1()

    def save(self):
        return self._p0


class c2( c1a ):
    # Class methods
    def m1(self, p1, p2) -> (str, bool):
        v1, v2 = c2.m1( p1, p2 )
        c = c1()
        print(c.save())
        mo2a.m( p2 )
        return v1, v2
