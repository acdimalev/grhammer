from .parsers import Parser


__all__ = [
    'Grammar',
    'Term',
]


class Grammar:

    def __init__(self, definition):
        self._definition = definition
        builder = GrammarBuilder()
        parsers = definition(builder)

        for (term, parser) in dict.items(parsers):
            if not isvalidterm(term):
                raise ValueError("{!r} is an invalid term".format(term))
            setattr(self, term, GrammarTerm(self, parser))

        self._terms = tuple(sorted(dict.keys(parsers)))

        # TODO: validate that all builder terms are defined

    def __str__(self):
        return "\n".join(
            "{}: {} ;".format(term, getattr(self, term))
            for term in self._terms
        )


class GrammarTerm:

    def __init__(self, grammar, parser):
        self.grammar = grammar
        self.parser = parser

    def __repr__(self):
        return "GrammarTerm({!r}, {!r})".format(self.grammar, self.parser)

    def __str__(self):
        return str(self.parser)

    def parse(self, document):
        return self.parser.parse(document, self.grammar)

    def generate(self, entropy):
        return self.parser.generate(entropy, self.grammar)


class GrammarBuilder:

    def __init__(self):
        self._terms = set()

    def __getattr__(self, name):
        setattr(self, name, Term(name))
        self._terms.add(name)
        return getattr(self, name)


class Term(Parser):

    def __init__(self, term):
        if not isvalidterm(term):
            raise ValueError("{!r} is an invalid term".format(term))
        self.term = term

    def __repr__(self):
        return "Term({!r}, {!r})".format(self.term)

    def __str__(self):
        return self.term

    def parse(self, document, grammar):
        return getattr(grammar, self.term).parse(document)

    def generate(self, entropy, grammar):
        return getattr(grammar, self.term).generate(entropy)


def isvalidterm(term):
    return str.isidentifier(term) and '_' != term[:1]
