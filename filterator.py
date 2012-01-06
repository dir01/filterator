from commands import *


class Filterable(object):
    def __init__(self, iterable):
        self.iterable = iterable

    def __repr__(self):
        return '<Filterable: %s>' % repr(self.iterable)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.iterable == other.iterable
        return self.iterable == other

    def filter(self, *callables, **constraints):
        return self.execute_command(FilterCommand, *callables, **constraints)

    def exclude(self, **constraints):
        return self.execute_command(ExcludeCommand, **constraints)

    def get(self, **constrains):
        return self.execute_command(GetCommand, **constrains)

    def count(self):
        return self.execute_command(CountCommand)

    def execute_command(self, cls, *args, **kwargs):
        return self.build_command(cls, *args, **kwargs).execute()

    def build_command(self, cls, *args, **kwargs):
        return cls(self, self.iterable, *args, **kwargs)
