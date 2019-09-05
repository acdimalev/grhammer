from .parsers import Parser


__all__ = [
    'Grammar',
]


class Grammar:

    def __init__(self, definition):
        self._definition = definition
        builder = GrammarBuilder(self)
        parsers = definition(builder)

        for (term, parser) in dict.items(parsers):
            if not isvalidterm(term):
                raise ValueError("{!r} is an invalid term".format(term))
            setattr(self, term, parser)

        self._terms = tuple(sorted(dict.keys(parsers)))

        # TODO: validate that all builder terms are defined

    def __str__(self):
        return "\n".join(
            "{}: {} ;".format(term, getattr(self, term))
            for term in self._terms
        )


class GrammarBuilder:

    def __init__(self, grammar):
        self._grammar = grammar
        self._terms = set()

    def __getattr__(self, name):
        setattr(self, name, GrammarParser(self._grammar, name))
        self._terms.add(name)
        return getattr(self, name)


class GrammarParser(Parser):

    def __init__(self, grammar, term):
        if not isvalidterm(term):
            raise ValueError("{!r} is an invalid term".format(term))
        self.grammar = grammar
        self.term = term

    def __repr__(self):
        return "GrammarParser({!r}, {!r})".format(self.grammar, self.term)

    def __str__(self):
        return self.term

    def parse(self, document):
        return getattr(self.grammar, self.term).parse(document)

    def generate(self, entropy):
        return getattr(self.grammar, self.term).generate(entropy)


def isvalidterm(term):
    return str.isidentifier(term) and '_' != term[:1]
