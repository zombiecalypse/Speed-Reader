#!/usr/bin/python

# Filename: text_output_actor.py
# Author:   Aaron Karper
# Created:  2012-01-07
# Description:
#           

import time, datetime, threading, re
import itertools

from multiprocessing import Value as SharedValue

from pykka.actor import ThreadingActor

pattern_sentence = re.compile('(?<=[\.!:?])\s|^$', re.MULTILINE)
pattern_word     = re.compile('\s+')

class Constant:
	def __init__(self, c):
		self.c = c
	def get(self):
		return self.c
EMPTY_STRING = Constant("")

class SentenceBuffer(object):
	def __init__(self):
		self._fill = 0
		self._text = []
	@property
	def fill(self):
		return self._fill

	def get_next_words(self, n):
		"returns n words or fewer if the paragraph is ending"
		assert n > 0
		if self.fill == 0: return []

		paragraph, rest = self._text[0], self._text[1:]
		if paragraph:
			words, self._text[0] = paragraph[:n], paragraph[n:]
			self._fill -= len(words)
			assert self._fill >= 0
			return words
		else:
			self._text = rest
			return self.get_next_words(n)
	def add_text(self, text):
		new = map(pattern_word.split, pattern_sentence.split(text))
		self._text += new
		self._fill += len([word for sentence in new for word in sentence])

class Timer(ThreadingActor):
	def call(self, callback, t = 1.1):
		"Calls the callback t seconds from now"
		time.sleep(t)
		callback()

class TextBuffer(ThreadingActor):
	BUFFERED_CHUNKS = 10
	def __init__(self, text_producer, callback, words_per_minute = 300, words_per_chunk = 1):
		ThreadingActor.__init__(self)
		self._words_per_minute = words_per_minute
		self._words_per_chunk = words_per_chunk
		self._text = SentenceBuffer()
		self._timer = Timer.start().proxy()
		self.text_producer = text_producer
		self.callback = callback
		self.request_new_text()

	@property
	def timeout(self):
		return datetime.timedelta(minutes = 1) * self._words_per_chunk / self._words_per_minute
	
	def set_word_speed(self, wpm, wpc):
		self._words_per_minute = int(wpm)
		self._words_per_chunk = int(wpc)
	
	def request_new_text(self):
		fillup_needed = self._words_per_chunk * self.BUFFERED_CHUNKS - self._text.fill
		if fillup_needed > 0:
			return self.text_producer.text(fillup_needed)
		else:
			return EMPTY_STRING
	
	def pause(self):
		self._paused = True
	
	def go(self):
		self._paused = False
		self._timer.call(callback = self.send_new_text, t= self.timeout.total_seconds()).get()

	def has_text(self):
		return self._text.fill > 0

	def drop_text(self):
		self._text = SentenceBuffer()
	
	def replace_input(self, producer):
		self.drop_text()
		self.text_producer = producer

	def send_new_text(self): 
		new_text = self.request_new_text()
		ret = ""
		if self.has_text():
			ret += " ".join(self._text.get_next_words(self._words_per_chunk))
		if not self._paused:
			self._timer.call(self.send_new_text, self.timeout.total_seconds())
			self.callback(ret)
		self.add_text(new_text.get())
	
	def add_text(self, txt):
		self._text.add_text(txt)

class TextGenerator(ThreadingActor):
	def text(self, min_n_words):
		raise NotImplementedError()

class ConstTextGenerator(TextGenerator):
	def __init__(self, txt):
		TextGenerator.__init__(self)
		self._text = itertools.cycle(txt.split())
	def text(self, n):
		return " ".join([self._text.next() for i in range(n)])

class FileTextGenerator(TextGenerator):
	def __init__(self, filename):
		TextGenerator.__init__(self)
		self.file_lines = open(filename).xreadlines()
	def text(self, n):
		got = 0
		lines = []
		while got < n:
			try:
				line = self.file_lines.next()
				word_count = len(line.split())
				lines.append(line)
				got += word_count
			except StopIteration:
				break
		return "".join(lines)