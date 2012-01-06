from errors import MultipleValuesReturned
from constraints import ConstraintsFactory


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
        self.constraints = self.convert_constraints_dict_to_constraints(self.kwargs)

    def convert_constraints_dict_to_constraints(self, constraints_dict):
        return map(self.convert_tuple_to_constraint, constraints_dict.items())

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



class Filterable(object):
    def __init__(self, iterable):
        self.iterable = iterable

    def __repr__(self):
        return '<Filterable: %s>' % repr(self.iterable)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.iterable == other.iterable
        return self.iterable == other

    def filter(self, **constraints):
        return self.build_command(FilterCommand, **constraints).execute()

    def exclude(self, **constraints):
        return self.build_command(ExcludeCommand, **constraints).execute()

    def get(self, **constrains):
        return self.build_command(GetCommand, **constrains).execute()

    def count(self):
        return len(self.iterable)

    def build_command(self, cls, *args, **kwargs):
        return cls(self, self.iterable, *args, **kwargs)
