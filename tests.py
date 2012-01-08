import unittest2
from collections import namedtuple

from errors import MultipleValuesReturned
from filterator import Filterable

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

    def is_persons_name_is_3_symbols_long(self, person):
        return len(person.name) == 3


class TestFilter(FilteratorTestCase):
    def test_multiple_constraints(self):
        self.assertEqual([self.bob], self.people.filter(sex='M', age__gte=18))

    def test_routinness(self):
        men = self.people.filter(sex='M')
        self.assertEqual([self.joe, self.bob], men)
        mature_men = men.filter(age__gte=18)
        self.assertEqual([self.bob], mature_men)
        self.assertEqual([self.joe, self.bob], men)

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

    def test_filter_by_callable_constraint(self):
        self.assertEqual(
            [self.joe, self.bob],
            self.people.filter(self.is_persons_name_is_3_symbols_long)
        )

    def test_filter_by_multiple_callable_constraints(self):
        self.assertEqual(
            [self.bob],
            self.people.filter(
                self.is_persons_name_is_3_symbols_long,
                lambda p: p.age > 18
            )
        )

    def test_filter_by_callable_constraint_combined_with_regular_constraint(self):
        self.assertEqual(
            [self.bob],
            self.people.filter(
                self.is_persons_name_is_3_symbols_long,
                age__gt=18
            )
        )


class TestExclude(FilteratorTestCase):
    def test_exclude_men(self):
        self.assertEqual([self.marta, self.alice], self.people.exclude(sex='M'))

    def test_exclude_by_multiple_constraints(self):
        self.assertEqual([self.marta], self.people.exclude(sex='M', age=23))

    def test_exclude_by_callable_constraint(self):
        self.assertEqual(
            [self.marta, self.alice],
            self.people.exclude(self.is_persons_name_is_3_symbols_long)
        )


class TestGet(FilteratorTestCase):
    def test_get_one(self):
        self.assertEqual(self.bob, self.people.filter(name='Bob').get())

    def test_get_with_constrains(self):
        self.assertEqual(self.bob, self.people.get(name='Bob'))

    def test_get_with_constrains_that_fit_multiple_items_raises_exception(self):
        with self.assertRaises(MultipleValuesReturned):
            self.people.get(sex='M')

    def test_get_by_callable_constraint(self):
        self.assertEqual(self.bob, self.people.get(lambda p: p.name == 'Bob'))


class TestCount(FilteratorTestCase):
    def test_many(self):
        self.assertEqual(2, self.people.filter(sex='M').count())

    def test_zero(self):
        self.assertEqual(0, self.people.filter(age=200).count())


class TestOrdering(FilteratorTestCase):
    def setUp(self):
        Creature = namedtuple('Creature', 'name number_of_legs number_of_eyes')
        self.dog = Creature(name='dog', number_of_legs=4, number_of_eyes=2)
        self.spider = Creature(name='spider', number_of_legs=8, number_of_eyes=9000)
        self.human = Creature(name='human', number_of_legs=2, number_of_eyes=2)
        self.creatures = Filterable([self.dog, self.human, self.spider])

    def test_order_by_int(self):
        self.assertEqual([self.human, self.dog, self.spider], self.creatures.order_by('number_of_legs'))

    def test_equal_items_remains_in_original_order(self):
        self.assertEqual([self.dog, self.human, self.spider], self.creatures.order_by('number_of_eyes'))

    def test_order_by_multiple_ints(self):
        self.assertEqual(
            [self.human, self.dog, self.spider],
            self.creatures.order_by('number_of_eyes', 'number_of_legs')
        )

    def test_order_by_reversed_key(self):
       self.assertEqual([self.spider, self.dog, self.human], self.creatures.order_by('-number_of_legs'))

    def test_order_by_multiple_reversed_keys(self):
        self.assertEqual(
            [self.spider, self.dog, self.human],
            self.creatures.order_by('-number_of_eyes', '-number_of_legs')
        )


if __name__ == '__main__':
    unittest2.main()
