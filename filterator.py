import unittest2
from collections import namedtuple
from errors import MultipleValuesReturned
from constraints import ConstraintsFactory


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
            if len(self.iterable) != 1:
                raise MultipleValuesReturned('More tran one value returned')
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
                constraint = ConstraintsFactory(name, value).get_constraint()
                return constraint.fits(item)
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

    def test_filter_iexact(self):
        self.assertEqual([self.bob], self.people.filter(name__iexact='bob'))

    def test_filter_contains(self):
        self.assertEqual([self.joe, self.bob], self.people.filter(name__contains='o'))

    def test_filter_gt(self):
        self.assertEqual([self.bob], self.people.filter(age__gt=23))

    def test_filter_gte(self):
        self.assertEqual([self.alice, self.bob], self.people.filter(age__gte=23))

    def test_filter_lt(self):
        self.assertEqual([self.marta], self.people.filter(age__lt=7))

    def test_filter_lte(self):
        self.assertEqual([self.marta, self.joe], self.people.filter(age__lte=7))

    def test_filter_isnull_False(self):
        self.assertEqual([self.marta, self.joe], self.people.filter(children__isnull=False))

    def test_filter_isnull_True(self):
        self.assertEqual([self.alice, self.bob], self.people.filter(children__isnull=True))

    def test_filter_count(self):
        self.assertEqual([self.alice], self.people.filter(children__count=1))


class TestGet(FilteratorTestCase):
    def test_get_one(self):
        self.assertEqual(self.bob, self.people.filter(name='Bob').get())

    def test_get_with_constrains(self):
        self.assertEqual(self.bob, self.people.get(name='Bob'))

    def test_get_with_constrains_that_fit_multiple_items_raises_exception(self):
        with self.assertRaises(MultipleValuesReturned):
            self.people.get(sex='M')


if __name__ == '__main__':
    unittest2.main()
