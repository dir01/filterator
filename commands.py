from errors import MultipleValuesReturned
from constraints import ConstraintsFactory


__all__ = (
    'FilterCommand',
    'ExcludeCommand',
    'GetCommand',
    'CountCommand',
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
        self.constraints = self.generate_constraints_from_kwargs()

    def generate_constraints_from_kwargs(self):
        return map(self.convert_tuple_to_constraint, self.kwargs.items())

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


class GetCommand(BaseCommand):
    def execute(self):
        if not self.kwargs:
            if len(self.iterable) != 1:
                raise MultipleValuesReturned('More than one value returned')
            return self.iterable[0]
        else:
            return self.context.filter(**self.kwargs).get()


class CountCommand(BaseCommand):
    def execute(self):
        return len(self.iterable)
