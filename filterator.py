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
