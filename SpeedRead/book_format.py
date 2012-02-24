#!/usr/bin/env python

import re
from functools import partial

from .helpers import *

pattern_word     = re.compile('\s+')
pattern_sentence = re.compile('(?<=[\.!:?])\s|^$', re.MULTILINE)

import json
import logging

logger = logging.getLogger('Book')

class Book(object):
    at = assure('at', logger = logger.debug, type = int)

    def __init__(self, sub_structure, at = 0):
        self._sub = sub_structure
        self.at  = at

    def __len__(self):
        return sum(len(s) for s in self._sub)

    def combined(self, other):
        return Book(sub_structure = self._sub + other._sub, at = self.at)

    def to_json(self):
        return json.dumps(
                dict( at = self.coord,
                    sub = self.to_list()))

    @classmethod
    def from_json(cls, str):
        dict = json.loads(str)
        struct = dict['sub']
        at = dict['at']
        book = cls.from_struct(struct)
        book.coord = at
        return book

    @classmethod
    def from_struct(cls, struct):
        if len(struct) == 0: return Snipplet.null()
        elif isinstance(struct[0], str.__base__):
            return Snipplet(struct)
        else:
            return Book([cls.from_struct(s) for s in struct])

    def __eq__(self, o):
        if not isinstance(o, self.__class__): return False

        return self.at == o.at and self._sub == o._sub

    def to_list(self):
        return [s.to_list() for s in self._sub]

    def normalize(self):
        n = len(self._sub)
        for sub in self._sub:
            sub.normalize()
        for i,sub in enumerate(self._sub):
            if sub.has_words():
                self.at = i
                break
            else:
                self.at = len(self._sub)

    def has_words(self):
        return self.remaining > 0

    @property
    def depth(self):
        return 1+max(e.depth for e in self._sub)

    @property
    def remaining(self):
        ret = len(self._sub) - self.at
        assert ret >= 0, "{} is weirdly not as long as {}".format(self._sub, self.at)
        return ret


    @property
    def current(self):
        if len(self._sub) > self.at:
            return self._sub[self.at]
        else:
            return Snipplet.null()

    def next_words(self, n):
        ret = self.current.next_words(n)
        self.normalize()
        assert all(isinstance(x, str) for x in ret)
        return ret

    @property
    def coord(self):
        return (self.at,) + self.current.coord

    @coord.setter
    def coord(self, o):
        car, cdr = o[0],o[1:]
        self.at = car
        self.current.coord = cdr

    def __repr__(self):
        return "<{} sub={!r} at={}>".format(self.__class__.__name__, self._sub, self.at)

    @classmethod
    def create_structured(cls, regexes, text):
        assert len(regexes) >= 1
        if len(regexes) == 1:
            single_regex = regexes[0]
            return Snipplet(single_regex.split(text))
        else:
            next_regex, rest = regexes[0], regexes[1:]
            return cls(map(partial(cls.create_structured, rest), next_regex.split(text)))
    @classmethod
    def create(cls, text):
        return cls.create_structured((pattern_sentence, pattern_word), text)

class Snipplet(Book):
    "Below this is strings"
    def next_words(self, n):
        n_words = self._sub[self.at:self.at+n]
        self.at += len(n_words) # You'd expect this to be n, but you'd be wrong!
        return n_words

    @property
    def coord(self):
        return (self.at,)

    @coord.setter
    def coord(self, c):
        self.at = c[0]

    @property
    def current(self):
        return self

    @property
    def depth(self):
        return 1

    def normalize(self):
        pass
    @classmethod
    def null(cls):
        return cls([])

    def __len__(self):
        return len(self._sub) - self.at

    def to_list(self):
        return self._sub[:]
