# -*- coding: utf-8 -*-
# Natural Language Toolkit: Generating from a CFG
#
# Copyright (C) 2001-2017 NLTK Project
# Author: Steven Bird <stevenbird1@gmail.com>
#         Peter Ljunglöf <peter.ljunglof@heatherleaf.se>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT
#
from __future__ import print_function

import itertools
import sys
import random
from nltk.grammar import Nonterminal


def generate(grammar, start=None, depth=None, n=None):
    """
    Generates an iterator of all sentences from a CFG.

    :param grammar: The Grammar used to generate sentences.
    :param start: The Nonterminal from which to start generate sentences.
    :param depth: The maximal depth of the generated tree.
    :param n: The maximum number of sentences to return.
    :return: An iterator of lists of terminal tokens.
    """
    if not start:
        start = grammar.start()
    if depth is None:
        depth = sys.maxsize

    iter = _generate_all(grammar, [start], depth)

    if n:
        iter = itertools.islice(iter, n)

    return iter


def _generate_all(grammar, items, depth):
    if items:
        try:
            for frag1 in _generate_one(grammar, items[0], depth):
                for frag2 in _generate_all(grammar, items[1:], depth):
                    yield frag1 + frag2
        except RuntimeError as _error:
            if _error.message == "maximum recursion depth exceeded":
                # Helpful error message while still showing the recursion stack.
                raise RuntimeError("The grammar has rule(s) that yield infinite recursion!!")
            else:
                raise
    else:
        yield []

def _generate_one(grammar, item, depth):
    if depth > 0:
        if isinstance(item, Nonterminal):
            for prod in grammar.productions(lhs=item):
                for frag in _generate_all(grammar, prod.rhs(), depth-1):
                    yield frag
        else:
            yield [item]

demo_grammar = """
  S -> NP VP
  NP -> Det N
  PP -> P NP
  VP -> 'slept' | 'saw' NP | 'walked' PP
  Det -> 'the' | 'a'
  N -> 'man' | 'park' | 'dog'
  P -> 'in' | 'with'
"""

def random_choice(prods):
    r = random.random()
    sum_ = 0.0
    for p in prods:
        sum_ += p.prob()
        if r < sum_:
            return p
    return lst[-1]


def generate_prob(grammar, n, start=None, depth=None):
    if not start:
        start = grammar.start()
    if not depth:
        depth = sys.maxsize

    for i in xrange(n):
        yield _generate_one_prob(grammar, start, depth)

def _generate_one_prob(grammar, item, depth):
    if depth <= 0:
        raise RuntimeError("The grammar has rule(s) that yield infinite recursion!!")

    sentence = []
    # random choice dependent on probabilities of the production rules
    prod = random_choice(grammar.productions(lhs=item))

    for sym in prod.rhs():
        if isinstance(sym, Nonterminal):
            sentence.extend(_generate_one_prob(grammar, sym, depth-1))
        else:
            sentence.append(sym)

    return sentence

def demo(N=23):
    from nltk.grammar import CFG

    print('Generating the first %d sentences for demo grammar:' % (N,))
    print(demo_grammar)
    grammar = CFG.fromstring(demo_grammar)
    for n, sent in enumerate(generate(grammar, n=N), 1):
        print('%3d. %s' % (n, ' '.join(sent)))


if __name__ == '__main__':
    demo()
