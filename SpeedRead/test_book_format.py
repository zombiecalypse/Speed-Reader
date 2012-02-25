#!/usr/bin/python

# Filename: test_book_format.py
# Author:   Aaron Karper
# Created:  2012-02-11
# Description:
#           

from .book_format import *
import unittest

class TestFlat(unittest.TestCase):
    def setUp(self):
        text = 'This is a text.'
        self.structured = Book.create_structured((pattern_word,),text)

    def test_good_start(self):
        self.assertEquals(1, self.structured.depth)
        self.assertTrue(self.structured.has_words())
        self.assertEquals(4, self.structured.remaining)
        self.assertEquals(0, self.structured.flat_coord)

    def test_gives_text(self):
        self.assertEquals('This is a'.split(), self.structured.next_words(3))
        self.assertEquals(1, self.structured.remaining)
        self.assertTrue(self.structured.has_words())
        self.assertEquals(3, self.structured.flat_coord)

    def test_gives_text_twice(self):
        self.test_gives_text()
        self.assertEquals('text.'.split(), self.structured.next_words(1))
        self.assertFalse(self.structured.has_words())
        self.assertEquals(4, self.structured.flat_coord)

class NormalDepth(unittest.TestCase):
    def setUp(self):
        text = "This is a text. It is full of wonders."
        self.structured = Book.create_structured((pattern_sentence, pattern_word), text)

    def test_start(self):
        self.assertEquals(2, self.structured.depth)
        self.assertTrue(self.structured.current.has_words())
        self.assertEquals((0,0), self.structured.coord)
        self.assertEquals(0, self.structured.flat_coord)

    def test_get_once(self):
        self.assertEquals("This is a".split(), self.structured.next_words(3))
        self.assertTrue(self.structured.current.has_words())
        self.assertEquals((0,3), self.structured.coord)
        self.assertEquals(3, self.structured.flat_coord)

    def test_repeat(self):
        self.assertEquals("This is a".split(), self.structured.next_words(3))
        self.structured.flat_coord = 1
        self.assertEquals("is a".split(), self.structured.next_words(2))

    def test_get_first_sentence(self):
        self.test_get_once()
        self.assertEquals("text.".split(), self.structured.next_words(3))
        self.assertEquals(4, self.structured.flat_coord)

    def test_get_second_sentence(self):
        self.test_get_first_sentence()
        self.assertEquals("It is".split(), self.structured.next_words(2))
        self.assertEquals(6, self.structured.flat_coord)
        self.assertEquals("full of wonders.".split(), self.structured.next_words(5))
        self.assertEquals(9, self.structured.flat_coord)

    def test_runs_dry(self):
        self.test_get_second_sentence()
        self.assertEquals([], self.structured.next_words(5))
        self.assertEquals(0,self.structured.remaining)

class TestCombinationStart(unittest.TestCase):
    def setUp(self):
        texts = ["This is a text.", "It is full of wonders."]
        self.structured = reduce(Book.combined, 
                map(
                    lambda x: Book.create_structured((pattern_sentence, pattern_word), x), 
                    texts))
    def test_start(self):
        self.assertEquals(2, self.structured.depth)
        self.assertTrue(self.structured.current.has_words())
        self.assertEquals((0,0), self.structured.coord)

    def test_get_sentences(self):
        self.assertEquals("This is a".split(), self.structured.next_words(3))
        self.assertTrue(self.structured.current.has_words())
        self.assertEquals((0,3), self.structured.coord)
        self.assertEquals("text.".split(), self.structured.next_words(3))
        self.assertEquals("It is".split(), self.structured.next_words(2))
        self.assertEquals("full of wonders.".split(), self.structured.next_words(5))

    def test_repeat(self):
        self.assertEquals("This is a".split(), self.structured.next_words(3))
        self.assertEquals("text.".split(), self.structured.next_words(3))
        self.assertEquals("It is".split(), self.structured.next_words(2))
        self.structured.flat_coord = 2
        self.assertEquals("a text.".split(), self.structured.next_words(3))
        self.structured.flat_coord = 4
        self.assertEquals(self.structured.flat_coord, 4)
        self.assertEquals("It is".split(), self.structured.next_words(2))

class TestCombinationMiddle(unittest.TestCase):
    def setUp(self):
        texts = ["This is a text.", "It is full of wonders."]
        self.structured = Book.create_structured((pattern_sentence, pattern_word), texts[0])
        self.structured2 = Book.create_structured((pattern_sentence, pattern_word), texts[1])

    def test_get_sentences(self):
        self.assertEquals("This is a".split(), self.structured.next_words(3))
        self.assertTrue(self.structured.current.has_words())
        self.assertEquals((0,3), self.structured.coord)

        self.structured = self.structured.combined(self.structured2)

        self.assertEquals("text.".split(), self.structured.next_words(3))
        self.assertEquals("It is".split(), self.structured.next_words(2))
        self.assertEquals("full of wonders.".split(), self.structured.next_words(5))

class TestCombinationEnd(unittest.TestCase):
    def setUp(self):
        texts = ["This is a text.", "It is full of wonders."]
        self.structured = Book.create_structured((pattern_sentence, pattern_word), texts[0])
        self.structured2 = Book.create_structured((pattern_sentence, pattern_word), texts[1])

    def test_get_sentences(self):
        self.assertEquals("This is a".split(), self.structured.next_words(3))
        self.assertTrue(self.structured.current.has_words())
        self.assertEquals((0,3), self.structured.coord)
        self.assertEquals("text.".split(), self.structured.next_words(3))
        self.assertFalse(self.structured.has_words())
        self.structured = self.structured.combined(self.structured2)
        self.assertEquals("It is".split(), self.structured.next_words(2))
        self.assertEquals((1,2), self.structured.coord)
        self.assertEquals("full of wonders.".split(), self.structured.next_words(5))

class TestJson(unittest.TestCase):
    def setUp(self):
        text = "This is a text. It is full of wonders."
        self.structured = Book.create_structured((pattern_sentence, pattern_word), text)

    def test_convert(self):
        json = self.structured.to_json()
        restruct = Book.from_json(json)
        self.assertEquals(restruct, self.structured)
        self.structured.next_words(3)
        self.assertNotEquals(restruct, self.structured)
        json = self.structured.to_json()
        restruct = Book.from_json(json)
        self.assertEquals(restruct, self.structured)

