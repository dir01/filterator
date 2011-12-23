import unittest2
from collections import namedtuple
from decimal import Decimal


Planet = namedtuple('Planet', 'name aphelion perihelion mass satellites')


class FilteratorTestCase(unittest2.TestCase):
    def setUp(self):
        self.mercury = Planet(name='Mercury',
            aphelion=69816900, perihelion=46001200, mass=Decimal('3.3E+23'),
            satellites=[]
        )
        self.venus = Planet(name='Venus',
            aphelion=108942109, perihelion=107476259, mass=Decimal('4.8E+24'),
            satellites=[]
        )
        self.earth = Planet(name='Earth',
            aphelion=1152098232, perihelion=147098290, mass=Decimal('5.9E+24'),
            satellites=['Moon']
        )
        self.mars = Planet(name='Mars',
            aphelion=249209300, perihelion=206669000, mass=Decimal('6.4E+23'),
            satellites=['Phobos', 'Deimos']
        )
        self.jupiter = Planet(name='Jupiter',
            aphelion=816520800, perihelion=740573600, mass=Decimal('1.8E+27'),
            satellites=['Io', 'Europa', 'Ganymede', 'Callisto']
        )
        self.saturn = Planet(name='Saturn',
            aphelion=1513325783, perihelion=1353572956, mass=Decimal('5.6E+26'),
            satellites=['Mimas', 'Enceladus', 'Tethys', 'Dione', 'Rhea', 'Titan', 'Iapetus']
        )
        self.uranus = Planet(name='Uranus',
            aphelion=3004419704, perihelion=2748938461, mass=Decimal('8.6E+25'),
            satellites=['Puck', 'Miranda', 'Ariel', 'Umbriel', 'Titania', 'Oberon']
        )
        self.neptune = Planet(name='Neptune',
            aphelion=4553946490, perihelion=4452940833, mass=Decimal('1.0E+26'),
            satellites=['Naiad', 'Thalassa','Despina', 'Galatea', 'Larissa', 'Proteus']
        )
        self.planets = [
            self.mercury,
            self.venus,
            self.earth,
            self.mars,
            self.jupiter,
            self.saturn,
            self.uranus,
            self.neptune
        ]


class TestFilter(FilteratorTestCase):
    def test(self):
        pass


if __name__ == '__main__':
    unittest2.main()