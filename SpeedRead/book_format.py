#!/usr/bin/env python

import re
from functools import partial
from traceback import print_stack

pattern_word     = re.compile('\s+')
pattern_sentence = re.compile('(?<=[\.!:?])\s|^$', re.MULTILINE)

import json

class Book(object):
	def __init__(self, sub_structure, at = 0):
		self._sub = sub_structure
		self._at  = at

	def __len__(self):
		return sum(len(s) for s in self._sub)

	def combined(self, other):
		return Book(sub_structure = self._sub + other._sub, at = self._at)

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

		return self._at == o._at and self._sub == o._sub

	def to_list(self):
		return [s.to_list() for s in self._sub]

	def normalize(self):
		n = len(self._sub)
		for sub in self._sub:
			sub.normalize()
		for i,sub in enumerate(self._sub):
			if sub.has_words():
				self._at = i
				break
			else:
				self._at = len(self._sub)

	def has_words(self):
		return self.remaining > 0

	@property
	def depth(self):
		return 1+max(e.depth for e in self._sub)

	@property
	def remaining(self):
		ret = len(self._sub) - self._at
		assert ret >= 0, "{} is weirdly not as long as {}".format(self._sub, self._at)
		return ret


	@property
	def current(self):
		if len(self._sub) > self._at:
			return self._sub[self._at]
		else:
			return Snipplet.null()

	def next_words(self, n):
		ret = self.current.next_words(n)
		self.normalize()
		assert all(isinstance(x, str) for x in ret)
		return ret

	@property
	def coord(self):
		return (self._at,) + self.current.coord

	@coord.setter
	def coord(self, o):
		car, cdr = o[0],o[1:]
		self._at = car
		self.current.coord = cdr

	def __repr__(self):
		return "<{} sub={!r} at={}>".format(self.__class__.__name__, self._sub, self._at)
	@classmethod
	def create_structured(cls, regexes, text):
		assert len(regexes) >= 1
		if len(regexes) == 1:
			single_regex = regexes[0]
			return Snipplet(single_regex.split(text))
		else:
			next_regex, rest = regexes[0], regexes[1:]
			return cls(map(partial(cls.create_structured, rest), next_regex.split(text)))

class Snipplet(Book):
	"Below this is strings"
	def next_words(self, n):
		n_words = self._sub[self._at:self._at+n]
		self._at += len(n_words) # You'd expect this to be n, but you'd be wrong!
		return n_words

	@property
	def coord(self):
		return (self._at,)

	@coord.setter
	def coord(self, c):
		self._at = c[0]

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
		return len(self._sub) - self._at

	def to_list(self):
		return self._sub[:]
