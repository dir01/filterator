import operator
import re


class BaseConstraint(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def resolve_value(self, item):
        for attr in self.name.split('__'):
            item = getattr(item, attr)
            if item is None:
                return None
            if hasattr(item, '__call__'):
                return item()
        return item

    def fits(self, item):
        raise NotImplementedError


class ExactConstraint(BaseConstraint):
    def fits(self, item):
        return self.resolve_value(item) == self.value


class CaseInsensitiveExactConstraint(BaseConstraint):
    def fits(self, item):
        return self.resolve_value(item).lower() == self.value.lower()


class StartsWithConstraint(BaseConstraint):
    def fits(self, item):
        return self.resolve_value(item).startswith(self.value)


class CaseInsensitiveStartsWithConstraint(BaseConstraint):
    def fits(self, item):
        return self.resolve_value(item).lower().startswith(self.value.lower())


class EndsWithConstraint(BaseConstraint):
    def fits(self, item):
        return self.resolve_value(item).endswith(self.value)


class CaseInsensitiveEndsWithConstraint(BaseConstraint):
    def fits(self, item):
        return self.resolve_value(item).lower().endswith(self.value.lower())


class RegexConstraint(BaseConstraint):
    def __init__(self, name, value):
        super(RegexConstraint, self).__init__(name, value)
        self.regex = re.compile(self.value)

    def fits(self, item):
        return self.regex.match(self.resolve_value(item))


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


class CallableConstraint(object):
    """
    We actually need this for just one single reason:
    to get constraint-like interface for callable constraints.
    So, this class isn't inherited from base constraint class
    and isn't supported by factory.
    It's separate, different constraint class
    """

    def __init__(self, callable):
        self.callable = callable

    def fits(self, item):
        return self.callable(item)


class ConstraintsFactory(object):
    KEYWORD_SEPARATOR = '__'
    DEFAULT_CONSTRAINT_CLASS = ExactConstraint

    KEYWORD_TO_CONSTRAINT_CLASS_MAP = {
        'exact': ExactConstraint,
        'iexact': CaseInsensitiveExactConstraint,
        'startswith': StartsWithConstraint,
        'istartswith': CaseInsensitiveStartsWithConstraint,
        'endswith': EndsWithConstraint,
        'iendswith': CaseInsensitiveEndsWithConstraint,
        'contains': ContainsConstraint,
        'regex': RegexConstraint,
        'gt': GtConstraint,
        'gte': GteConstraint,
        'lt': LtConstraint,
        'lte': LteConstraint,
        'isnull': IsnullConstraint,
        'count': CountConstraint,
        }

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get_constraint(self):
        prefix, suffix = self.get_name_and_keyword(self.name)
        if suffix and suffix in self.KEYWORD_TO_CONSTRAINT_CLASS_MAP:
            name = prefix
            cls = self.KEYWORD_TO_CONSTRAINT_CLASS_MAP[suffix]
        else:
            name = self.name
            cls = self.DEFAULT_CONSTRAINT_CLASS
        return cls(name, self.value)

    def get_name_and_keyword(self, name):
        if not self.KEYWORD_SEPARATOR in name:
            return name, None
        return name.split(self.KEYWORD_SEPARATOR)
