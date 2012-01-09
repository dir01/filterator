from errors import MultipleValuesReturned
from constraints import ConstraintsFactory, CallableConstraint


__all__ = (
    'FilterCommand',
    'ExcludeCommand',
    'OrderCommand',
    'GetCommand',
    'CountCommand',
    'ExistsCommand',
)


class BaseCommand(object):
    def __init__(self, context, iterable, *args, **kwargs):
        self.context = context
        self.args = args
        self.kwargs = kwargs
        self.iterable = iterable

    def execute(self):
        raise NotImplementedError()

    def wrap(self, iterable):
        return self.context.__class__(iterable)


class BaseFilteringCommand(BaseCommand):
    def __init__(self, context, iterable, *args, **kwargs):
        super(BaseFilteringCommand, self).__init__(context, iterable, *args, **kwargs)
        self.constraints = self.generate_constraints_from_args_and_kwargs()

    def generate_constraints_from_args_and_kwargs(self):
        return map(self.convert_callable_to_constraint, self.args) + \
               map(self.convert_tuple_to_constraint, self.kwargs.items())

    def convert_callable_to_constraint(self, callable):
        return CallableConstraint(callable)

    def convert_tuple_to_constraint(self, constraint_tuple):
        name, value = constraint_tuple
        return ConstraintsFactory(name, value).get_constraint()

    def execute(self):
        return self.wrap(
            filter(self.passes_test, self.iterable)
        )

    def passes_test(self, item):
        raise NotImplementedError


class FilterCommand(BaseFilteringCommand):
    def passes_test(self, item):
        for constraint in self.constraints:
            if not constraint.fits(item):
                return False
        return True


class ExcludeCommand(BaseFilteringCommand):
    def passes_test(self, item):
        for constraint in self.constraints:
            if constraint.fits(item):
                return False
        return True


class OrderCommand(BaseCommand):
    def execute(self):
        ordering_strategy = self.get_ordering_strategy()
        return ordering_strategy.get_ordered_iterable()

    def get_ordering_strategy(self):
        return self.build_strategy(self.choose_ordering_strategy_class())

    def choose_ordering_strategy_class(self):
        if self.is_key_sorting_possible():
            return KeyOrderingStrategy
        else:
            return CmpFunctionOrderingStrategy

    def is_key_sorting_possible(self):
        if self.is_all_keys_reversed_or_all_keys_unreversed():
            return True
        return False

    def is_all_keys_reversed_or_all_keys_unreversed(self):
        if self.is_all_keys_start_with_minus():
            return True
        if self.is_all_key_dont_start_with_minus():
            return True
        return False

    def build_strategy(self, strategy_cls):
        return strategy_cls(self.iterable, keys=self.args)

    def is_all_keys_start_with_minus(self):
        for key in self.args:
            if not self.is_starts_with_minus(key):
                return False
        return True

    def is_all_key_dont_start_with_minus(self):
        for key in self.args:
            if self.is_starts_with_minus(key):
                return False
        return True

    def is_starts_with_minus(self, key):
        return key.startswith('-')


class BaseOrderingStrategy(object):
    def __init__(self, iterable, keys):
        self.iterable = iterable
        self.keys = keys

    def get_ordered_iterable(self):
        raise NotImplementedError

    def is_starts_with_minus(self, key):
        return key.startswith('-')

    def strip_minus(self, key):
        return key.strip('-')


class KeyOrderingStrategy(BaseOrderingStrategy):
    def get_ordered_iterable(self):
        return sorted(self.iterable, key=self.get_attributes, reverse=self.is_reversed())

    def is_reversed(self):
        return self.is_all_keys_start_with_minus()

    def get_attributes(self, item):
        return tuple([getattr(item, key) for key in self.get_keys()])

    def get_keys(self):
        return map(self.strip_minus, self.keys)

    def is_all_keys_start_with_minus(self):
        for key in self.keys:
            if not self.is_starts_with_minus(key):
                return False
        return True


class CmpFunctionOrderingStrategy(BaseOrderingStrategy):
    def get_ordered_iterable(self):
        return sorted(self.iterable, cmp=self.cmp_function)

    def cmp_function(self, item, other):
        for key in self.keys:
            reverse = True if self.is_starts_with_minus(key) else False
            if reverse:
                key = self.strip_minus(key)
            result = cmp(getattr(item, key), getattr(other, key))
            if result == 0:
                continue
            return result * (-1 if reverse else 1)
        return 0


class GetCommand(BaseCommand):
    def execute(self):
        if not (self.args or self.kwargs):
            if len(self.iterable) != 1:
                raise MultipleValuesReturned('More than one value returned')
            return self.iterable[0]
        else:
            return self.context.filter(*self.args, **self.kwargs).get()


class CountCommand(BaseCommand):
    def execute(self):
        return len(self.iterable)


class ExistsCommand(BaseCommand):
    def execute(self):
        return bool(self.iterable)
