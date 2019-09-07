from . import rng


__all__ = [
    'ParseResult',
    'ParseOk',
    'ParseError',
    'GenerationException',
    'Parser',
    'Literal',
    'Range',
    'Any',
    'OneOf',
    'Optional',
    'Many',
    'Sequence',
    'Less',
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


class GenerationException(Exception):
    pass


class Parser:
    pass


class Literal(Parser):

    def __init__(self, literal):
        self.literal = literal

    def __repr__(self):
        return "Literal({!r})".format(self.literal)

    def __str__(self):
        return repr(self.literal)

    def parse(self, document, grammar):
        (head, tail) = (document[:1], document[1:])
        if self.literal == head:
            return ParseOk(head, tail)
        else:
            return ParseError("Expected {} found {!r}".format(self, head))

    def generate(self, entropy, grammar):
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

    def parse(self, document, grammar):
        (head, tail) = (document[:1], document[1:])
        if self.first <= head <= self.last:
            return ParseOk(head, tail)
        else:
            return ParseError("Expected {} found {!r}".format(self, head))

    def generate(self, entropy, grammar):
        return chr(rng.in_range(entropy, ord(self.first), ord(self.last)))


class Any(Parser):

    def __repr__(self):
        return "Any()"

    def __str__(self):
        return "? any ?"

    def parse(self, document, grammar):
        (head, tail) = (document[:1], document[1:])
        if head:
            return ParseOk(head, tail)
        else:
            return ParseError("Expected any found end of document")

    def generate(self, entropy, grammar):
        return chr(rng.roll(entropy, 0x110000))


class OneOf(Parser):

    def __init__(self, children):
        children = tuple(children)
        assert(children)
        for child in children:
            assert(isinstance(child, Parser))
        self.children = children

    def __repr__(self):
        return "OneOf({!r})".format(list(self.children))

    def __str__(self):
        return "( {} )".format(" | ".join(map(str, self.children)))

    def parse(self, document, grammar):
        for child in self.children:
            result = child.parse(document, grammar)
            if ParseOk == type(result):
                return result
        head = document[:1]
        return ParseError("Expected {} found {!r}".format(self, head))

    def generate(self, entropy, grammar):
        # FIXME: Write a profiling suite.
        n_child = rng.roll(entropy, len(self.children))
        document = self.children[n_child].generate(entropy, grammar)
        if 0 == n_child:
            return document
        parser = OneOf(self.children[:n_child])
        result = parser.parse(document, grammar)
        if ParseError == type(result):
            return document
        return parser.generate(entropy, grammar)


class Optional(Parser):

    def __init__(self, child):
        assert(isinstance(child, Parser))
        self.child = child

    def __repr__(self):
        return "Optional({!r})".format(self.child)

    def __str__(self):
        return "[ {} ]".format(self.child)

    def parse(self, document, grammar):
        result = self.child.parse(document, grammar)
        if ParseOk == type(result):
            return ParseOk([result.matched], result.remaining)
        else:
            return ParseOk([], document)

    def generate(self, entropy, grammar):
        return self.child.generate(entropy, grammar) if rng.maybe(entropy) else ''


class Many(Parser):

    def __init__(self, child):
        assert(isinstance(child, Parser))
        self.child = child

    def __repr__(self):
        return "Many({!r})".format(self.child)

    def __str__(self):
        return "{{ {} }}".format(self.child)

    def parse(self, document, grammar):
        matched = []
        remaining = document
        while True:
            result = self.child.parse(remaining, grammar)
            if ParseError == type(result):
                break
            # FIXME: Implement timeout in property tests
            #   to catch infinite loops.
            # e.g.  `Many(Many(Any()))
            if len(remaining) == len(result.remaining):
                break
            matched += [result.matched]
            remaining = result.remaining
        return ParseOk(matched, remaining)

    def generate(self, entropy, grammar):
        document = ''.join(
            self.child.generate(entropy, grammar)
            for _ in range(rng.scale(entropy))
        )
        result = self.parse(document, grammar)
        if ParseOk != type(result):
            raise GenerationException
        if 0 != len(result.remaining):
            raise GenerationException
        return document


class Sequence(Parser):

    def __init__(self, children):
        children = tuple(children)
        assert(children)
        for child in children:
            assert(isinstance(child, Parser))
        self.children = children

    def __repr__(self):
        return "Sequence({!r})".format(list(self.children))

    def __str__(self):
        return "( {} )".format(", ".join(map(str, self.children)))

    def parse(self, document, grammar):
        matched = []
        remaining = document
        for child in self.children:
            result = child.parse(remaining, grammar)
            if ParseError == type(result):
                return result
            matched += [result.matched]
            remaining = result.remaining
        return ParseOk(matched, remaining)

    def generate(self, entropy, grammar):
        document = ''.join(child.generate(entropy, grammar) for child in self.children)
        result = self.parse(document, grammar)
        if ParseOk != type(result):
            raise GenerationException
        if 0 != len(result.remaining):
            raise GenerationException
        return document


class Less(Parser):

    def __init__(self, exception, rule):
        self.exception = exception
        self.rule = rule

    def __repr__(self):
        return "Less({!r}, {!r})".format(self.exception, self.rule)

    def __str__(self):
        return "{} - {}".format(self.rule, self.exception)

    def parse(self, document, grammar):
        result = self.exception.parse(document, grammar)
        if ParseOk == type(result):
            return ParseError("Found {!r}".format(result.matched))
        return self.rule.parse(document, grammar)

    def generate(self, entropy, grammar):
        document = self.rule.generate(entropy, grammar)
        if ParseOk == type(self.exception.parse(document, grammar)):
            raise GenerationException
        return document
