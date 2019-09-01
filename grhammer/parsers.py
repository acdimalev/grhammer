from . import rng


__all__ = [
    'ParseResult',
    'ParseOk',
    'ParseError',
    'Parser',
    'Literal',
    'Range',
    'Any',
]

class ParseResult:
    pass


class ParseOk(ParseResult):

    def __init__(self, matched, remaining):
        self.matched = matched
        self.remaining = remaining

    def __repr__(self):
        return "ParseOk({!r}, {!r})".format(self.matched, self.remaining)

    def __iter__(self):
        return iter([self.matched, self.remaining])


class ParseError(ParseResult):

    def __init__(self, reason):
        self.reason = reason

    def __repr__(self):
        return "ParseError({!r})".format(self.reason)

    def __iter__(self):
        return iter([self.reason])


class Parser:
    pass


class Literal(Parser):

    def __init__(self, literal):
        self.literal = literal

    def __repr__(self):
        return "Literal({!r})".format(self.literal)

    def __str__(self):
        return repr(self.literal)

    def parse(self, document):
        (head, tail) = (document[:1], document[1:])
        if self.literal == head:
            return ParseOk(head, tail)
        else:
            return ParseError("Expected {} found {!r}".format(self, head))

    def generate(self, entropy):
        return self.literal


class Range(Parser):

    def __init__(self, first, last):
        assert(first <= last)
        self.first = first
        self.last = last

    def __repr__(self):
        return "Range({!r}, {!r})".format(self.first, self.last)

    def __str__(self):
        return "{!r}..{!r}".format(self.first, self.last)

    def parse(self, document):
        (head, tail) = (document[:1], document[1:])
        if self.first <= head <= self.last:
            return ParseOk(head, tail)
        else:
            return ParseError("Expected {} found {!r}".format(self, head))

    def generate(self, entropy):
        return chr(rng.in_range(entropy, ord(self.first), ord(self.last)))


class Any(Parser):

    def __repr__(self):
        return "Any()"

    def parse(self, document):
        (head, tail) = (document[:1], document[1:])
        if head:
            return ParseOk(head, tail)
        else:
            return ParseError("Expected any found end of document")

    def generate(self, entropy):
        return chr(rng.roll(entropy, 0x110000))


class OneOf(Parser):

    def __init__(self, children):
        children = tuple(children)
        for child in children:
            assert(isinstance(child, Parser))
        self.children = children

    def __repr__(self):
        return "OneOf({!r})".format(list(self.children))

    def __str__(self):
        return "( {} )".format(" | ".join(map(str, self.children)))

    def parser(self, document):
        for child in self.children:
            result = child.parse(document)
            if ParseOk == type(result):
                return result
        head = document[:1]
        return ParseError("Expected {} found {!r}".format(self, head))

    def generate(self, entropy):
        # FIXME: this ignores the ordering of the disjunction
        # this should get flagged in a proper test
        return rng.one_of(entropy, self.children).generate()
