import operator
import unittest2
from collections import namedtuple
from errors import MultipleValuesReturned

class BaseConstraint(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def resolve_value(self, item):
        return getattr(item, self.name)

    def fits(self, item):
        raise NotImplementedError


class ExactConstraint(BaseConstraint):
    def fits(self, item):
        return self.resolve_value(item) == self.value


class CaseInsensitiveExactConstraint(BaseConstraint):
    def fits(self, item):
        return self.resolve_value(item).lower() == self.value.lower()


class ContainsConstraint(BaseConstraint):
    def fits(self, item):
        return self.value in self.resolve_value(item)


class BaseComparativeConstraint(BaseConstraint):
    def fits(self, item):
        return self.COMPARATIVE_FUNCTION(self.resolve_value(item), self.value)

    @property
    def COMPARATIVE_FUNCTION(self):
        raise NotImplementedError('Should be implemented in inherited class')


class GtConstraint(BaseComparativeConstraint):
    COMPARATIVE_FUNCTION = operator.gt


class GteConstraint(BaseComparativeConstraint):
    COMPARATIVE_FUNCTION = operator.ge


class LtConstraint(BaseComparativeConstraint):
    COMPARATIVE_FUNCTION = operator.lt


class LteConstraint(BaseComparativeConstraint):
    COMPARATIVE_FUNCTION = operator.le


class IsnullConstraint(BaseComparativeConstraint):
    def fits(self, item):
        return bool(self.resolve_value(item)) == self.value


class CountConstraint(BaseConstraint):
    def fits(self, item):
        return len(self.resolve_value(item)) == self.value


class ConstraintsFactory(object):
    KEYWORD_SEPARATOR = '__'

    def __init__(self, name, value):
        self.name, self.keyword = self.get_name_and_keyword(name)
        self.value = value

    def get_constraint(self):
        ConstraintClass = self.get_constraint_class()
        return ConstraintClass(self.name, self.value)

    def get_constraint_class(self):
        KEYWORD_TO_CONSTRAINT_CLASS_MAP = {
            'exact': ExactConstraint,
            'iexact': CaseInsensitiveExactConstraint,
            'contains': ContainsConstraint,
            'gt': GtConstraint,
            'gte': GteConstraint,
            'lt': LtConstraint,
            'lte': LteConstraint,
            'isnull': IsnullConstraint,
            'count': CountConstraint,
        }
        if not self.keyword in KEYWORD_TO_CONSTRAINT_CLASS_MAP:
            raise NotImplementedError('Keyword "%s" is not yet supported' % self.keyword)
        return KEYWORD_TO_CONSTRAINT_CLASS_MAP[self.keyword]

    def get_name_and_keyword(self, name):
        name_keyword = name.split(self.KEYWORD_SEPARATOR)
        if len(name_keyword) == 1:
            name_keyword.append('exact')
        return name_keyword


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
