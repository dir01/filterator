import unittest2
from collections import namedtuple
from decimal import Decimal


class Filterable(object):
    def __init__(self, iterable):
        self.iterable = iterable

    def __repr__(self):
        return '<Filterable: %s>' % repr(self.iterable)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.iterable == other.iterable
        return self.iterable == other

    def get(self, **constrains):
        if not constrains:
            assert len(self.iterable) == 1
            return self.iterable[0]
        else:
            return self.filter(**constrains).get()

    def filter(self, **constrains):
        return self.wrap(
            filter(self.get_filtering_function(constrains), self.iterable)
        )

    def get_filtering_function(self, constrains):
        def filtering_function(item):
            for name, value in constrains.iteritems():
                if getattr(item, name) != value:
                    return False
            return True
        return filtering_function

    def wrap(self, iterable):
        return self.__class__(iterable)


class FilteratorTestCase(unittest2.TestCase):
    def setUp(self):
        Person = namedtuple('Person', 'name age sex children')
        self.marta = Person('Marta', 2, 'F', [])
        self.joe = Person('Joe', 7, 'M', [])
        self.alice = Person('Alice', 23, 'F', [self.marta])
        self.bob = Person('Bob', 31, 'M', [self.marta, self.joe])
        self.people = Filterable([
            self.marta,
            self.joe,
            self.alice,
            self.bob,
        ])


class TestFilter(FilteratorTestCase):
    def test_filter_by_string(self):
        self.assertEqual([self.bob], self.people.filter(name='Bob'))

    def test_filter_by_int(self):
        self.assertEqual([self.alice], self.people.filter(age=23))


class TestGet(FilteratorTestCase):
    def test_get_one(self):
        self.assertEqual(self.bob, self.people.filter(name='Bob').get())

    def test_get_with_constrains(self):
        self.assertEqual(self.bob, self.people.get(name='Bob'))



if __name__ == '__main__':
    unittest2.main()
