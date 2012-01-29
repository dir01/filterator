import unittest2
from collections import namedtuple

from errors import MultipleValuesReturned
from filterator import Filterable


class FilteratorTestCase(unittest2.TestCase):
    def setUp(self):
        Person = namedtuple('Person', 'name age sex children vehicle')
        Vehicle = namedtuple('Vehicle', 'type manufacturer')
        self.car = Vehicle('car', 'ford')
        self.bicycle = Vehicle('bicycle', 'nsbikes')
        self.marta = Person('Marta', 2, 'F', [], None)
        self.joe = Person('Joe', 7, 'M', [], None)
        self.alice = Person('Alice', 23, 'F', [self.marta], self.bicycle)
        self.bob = Person('Bob', 31, 'M', [self.marta, self.joe], self.car)
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
        self.assertItemsEqual([self.bob], self.people.filter(sex='M', age__gte=18))

    def test_routinness(self):
        men = self.people.filter(sex='M')
        self.assertItemsEqual([self.joe, self.bob], men)
        mature_men = men.filter(age__gte=18)
        self.assertItemsEqual([self.bob], mature_men)
        self.assertItemsEqual([self.joe, self.bob], men)

    def test_filter_by_string(self):
        self.assertItemsEqual([self.bob], self.people.filter(name='Bob'))

    def test_filter_by_int(self):
        self.assertItemsEqual([self.alice], self.people.filter(age=23))

    def test_filter_iexact(self):
        self.assertItemsEqual([self.bob], self.people.filter(name__iexact='bob'))

    def test_filter_contains(self):
        self.assertItemsEqual([self.joe, self.bob], self.people.filter(name__contains='o'))

    def test_filter_startswith(self):
        self.assertItemsEqual([self.bob], self.people.filter(name__startswith='B'))

    def test_filter_istartswith(self):
        self.assertItemsEqual([self.bob], self.people.filter(name__istartswith='b'))

    def test_filter_endswith(self):
        self.assertItemsEqual([self.bob], self.people.filter(name__endswith='ob'))

    def test_filter_iendswith(self):
        self.assertItemsEqual([self.bob], self.people.filter(name__iendswith='OB'))

    def test_filter_regex(self):
        self.assertItemsEqual([self.alice, self.bob], self.people.filter(name__regex='^[AB].*$'))

    def test_filter_gt(self):
        self.assertItemsEqual([self.bob], self.people.filter(age__gt=23))

    def test_filter_gte(self):
        self.assertItemsEqual([self.alice, self.bob], self.people.filter(age__gte=23))

    def test_filter_lt(self):
        self.assertItemsEqual([self.marta], self.people.filter(age__lt=7))

    def test_filter_lte(self):
        self.assertItemsEqual([self.marta, self.joe], self.people.filter(age__lte=7))

    def test_filter_isnull_False(self):
        self.assertItemsEqual([self.marta, self.joe], self.people.filter(children__isnull=False))

    def test_filter_isnull_True(self):
        self.assertItemsEqual([self.alice, self.bob], self.people.filter(children__isnull=True))

    def test_filter_count(self):
        self.assertItemsEqual([self.alice], self.people.filter(children__count=1))

    def test_filter_by_callable_constraint(self):
        self.assertItemsEqual(
            [self.joe, self.bob],
            self.people.filter(self.is_persons_name_is_3_symbols_long)
        )

    def test_filter_by_multiple_callable_constraints(self):
        self.assertItemsEqual(
            [self.bob],
            self.people.filter(
                self.is_persons_name_is_3_symbols_long,
                lambda p: p.age > 18
            )
        )

    def test_filter_by_callable_constraint_combined_with_regular_constraint(self):
        self.assertItemsEqual(
            [self.bob],
            self.people.filter(
                self.is_persons_name_is_3_symbols_long,
                age__gt=18
            )
        )

    def test_deep(self):
        self.assertItemsEqual([self.alice], self.people.filter(vehicle__type='bicycle'))


class TestExclude(FilteratorTestCase):
    def test_exclude_men(self):
        self.assertItemsEqual([self.marta, self.alice], self.people.exclude(sex='M'))

    def test_exclude_by_multiple_constraints(self):
        self.assertItemsEqual([self.marta], self.people.exclude(sex='M', age=23))

    def test_exclude_by_callable_constraint(self):
        self.assertItemsEqual(
            [self.marta, self.alice],
            self.people.exclude(self.is_persons_name_is_3_symbols_long)
        )

    def test_exclude_by_deep_attr(self):
        self.assertItemsEqual(
            [self.alice, self.joe, self.marta],
            self.people.exclude(vehicle__type='car')
        )


class TestGet(FilteratorTestCase):
    def test_get_one(self):
        self.assertItemsEqual(self.bob, self.people.filter(name='Bob').get())

    def test_get_with_constrains(self):
        self.assertItemsEqual(self.bob, self.people.get(name='Bob'))

    def test_get_with_constrains_that_fit_multiple_items_raises_exception(self):
        with self.assertRaises(MultipleValuesReturned):
            self.people.get(sex='M')

    def test_get_by_callable_constraint(self):
        self.assertItemsEqual(self.bob, self.people.get(lambda p: p.name == 'Bob'))


class TestCount(FilteratorTestCase):
    def test_many(self):
        self.assertEqual(2, self.people.filter(sex='M').count())

    def test_zero(self):
        self.assertEqual(0, self.people.filter(age=200).count())


class TestExists(FilteratorTestCase):
    def test_exists(self):
        self.assertEqual(True, self.people.filter(name='Bob').exists())

    def test_does_not_exists(self):
        self.assertEqual(False, self.people.filter(name='Cris').exists())


class TestOrdering(FilteratorTestCase):
    def setUp(self):
        Creature = namedtuple('Creature', 'name number_of_legs number_of_eyes')
        self.dog = Creature(name='dog', number_of_legs=4, number_of_eyes=2)
        self.spider = Creature(name='spider', number_of_legs=8, number_of_eyes=9000)
        self.human = Creature(name='human', number_of_legs=2, number_of_eyes=2)
        self.creatures = Filterable([self.dog, self.human, self.spider])

    def test_order_by_int(self):
        self.assertItemsEqual([self.human, self.dog, self.spider], self.creatures.order_by('number_of_legs'))

    def test_equal_items_remains_in_original_order(self):
        self.assertItemsEqual([self.dog, self.human, self.spider], self.creatures.order_by('number_of_eyes'))

    def test_order_by_multiple_ints(self):
        self.assertItemsEqual(
            [self.human, self.dog, self.spider],
            self.creatures.order_by('number_of_eyes', 'number_of_legs')
        )

    def test_order_by_reversed_key(self):
       self.assertItemsEqual([self.spider, self.dog, self.human], self.creatures.order_by('-number_of_legs'))

    def test_order_by_multiple_reversed_keys(self):
        self.assertItemsEqual(
            [self.spider, self.dog, self.human],
            self.creatures.order_by('-number_of_eyes', '-number_of_legs')
        )

    def test_order_by_multiple_mixed_reversed_and_unreversed_keys(self):
        self.assertItemsEqual(
            [self.spider, self.human, self.dog],
            self.creatures.order_by('-number_of_eyes', 'number_of_legs')
        )

    def test_order_by_string(self):
        self.assertItemsEqual([self.dog, self.human, self.spider], self.creatures.order_by('name'))

    def test_order_by_string_reversed(self):
        self.assertItemsEqual([self.spider, self.human, self.dog], self.creatures.order_by('-name'))


if __name__ == '__main__':
    unittest2.main()
