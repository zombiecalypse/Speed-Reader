#!/usr/bin/python

# Filename: text_output_actor.py
# Author:   Aaron Karper
# Created:  2012-01-07
# Description:
#           

import time, re
import itertools
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('Text Actors')

from .helpers import *
from .helpers import _
from .book_format import Book

from pykka.actor import ThreadingActor


class _Constant:
	def __init__(self, c):
		self.c = c
	def get(self):
		return self.c

EMPTY_STRING = _Constant("")

class TextBuffer(ThreadingActor):
    BUFFERED_CHUNKS  = 10
    TICK_TIME        = timedelta(milliseconds = 50)

    words_per_minute = accessor('words_per_minute', logger.debug, int)
    words_per_chunk  = accessor('words_per_chunk' , logger.debug, int)
    book             = accessor('book'            , logger.debug, isa(Book))

    def __init__(self, callback, finished = lambda : None,  text = "", words_per_minute = 300, words_per_chunk = 1):
        ThreadingActor.__init__(self)
        self.words_per_minute = words_per_minute
        self.words_per_chunk = words_per_chunk
        self.book = Book.create(text)
        self.callback = assure(str)(callback)
        self.finished = finished

    @property
    def timeout(self):
        return timedelta(minutes = 1) * self.words_per_chunk / self.words_per_minute

    def set_word_speed(self, wpm, wpc):
        self.words_per_minute = wpm
        self.words_per_chunk = wpc
        self.pause()

    def pause(self):
        self._paused = True

    def go(self):
        self._paused = False
        self.after(self.timeout, self.as_message.send_new_text)

    def after(self, t, callback):
        if t <= timedelta(seconds=0): return callback()

        time.sleep(self.TICK_TIME.total_seconds())
        self.as_message.after(t-self.TICK_TIME, callback)

    def has_text(self):
        return self.book.remaining > 0

    def drop_text(self):
        self.book = Book.create('')

    def use_text(self, text):
        self.book = Book.create(text)

    def send_new_text(self): 
        ret = ""
        if self.has_text():
            ret += " ".join(self.book.next_words(self.words_per_chunk))
        else:
            self._paused = True
        if not self._paused:
            self.callback(ret)
            self.after(self.timeout, self.as_message.send_new_text)
        else:
            self.finished()

    def add_text(self, txt):
        if txt:
            self.book = self.book.combined(Book.create(txt))

