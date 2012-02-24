#!/usr/bin/python

# Filename: test_book_format.py
# Author:   Aaron Karper
# Created:  2012-02-11
# Description:
#           

from .book_format import *
import unittest

class FormatTest(unittest.TestCase):
	def test_small(self):
		text = 'This is a text.'
		structured = Book.create_structured((pattern_word,),text)
		self.assertEquals(1, structured.depth)
		self.assertTrue(structured.has_words())
		self.assertEquals(4, structured.remaining)
		self.assertEquals('This is a'.split(), structured.next_words(3))
		self.assertEquals(1, structured.remaining)
		self.assertTrue(structured.has_words())
		self.assertEquals('text.'.split(), structured.next_words(1))
		self.assertFalse(structured.has_words())
	def test_create(self):
		text = "This is a text. It is full of wonders."
		structured = Book.create_structured((pattern_sentence, pattern_word), text)
		self.assertEquals(2, structured.depth)
		self.assertTrue(structured.current.has_words())
		self.assertEquals((0,0), structured.coord)
		self.assertEquals("This is a".split(), structured.next_words(3))
		self.assertTrue(structured.current.has_words())
		self.assertEquals((0,3), structured.coord)
		self.assertEquals("text.".split(), structured.next_words(3))
		self.assertEquals("It is".split(), structured.next_words(2))
		self.assertEquals("full of wonders.".split(), structured.next_words(5))
		self.assertEquals([], structured.next_words(5))
		self.assertEquals(0,structured.remaining)
	def test_combine_at_start(self):
		texts = ["This is a text.", "It is full of wonders."]
		structured = reduce(Book.combined, 
				map(
					lambda x: Book.create_structured((pattern_sentence, pattern_word), x), 
					texts))
		self.assertEquals(2, structured.depth)
		self.assertTrue(structured.current.has_words())
		self.assertEquals((0,0), structured.coord)
		self.assertEquals("This is a".split(), structured.next_words(3))
		self.assertTrue(structured.current.has_words())
		self.assertEquals((0,3), structured.coord)
		self.assertEquals("text.".split(), structured.next_words(3))
		self.assertEquals("It is".split(), structured.next_words(2))
		self.assertEquals("full of wonders.".split(), structured.next_words(5))

	def test_combine_middle(self):
		texts = ["This is a text.", "It is full of wonders."]
		structured = Book.create_structured((pattern_sentence, pattern_word), texts[0])
		structured2 = Book.create_structured((pattern_sentence, pattern_word), texts[1])
		self.assertEquals("This is a".split(), structured.next_words(3))
		self.assertTrue(structured.current.has_words())
		self.assertEquals((0,3), structured.coord)
		structured = structured.combined(structured2)
		self.assertEquals("text.".split(), structured.next_words(3))
		self.assertEquals("It is".split(), structured.next_words(2))
		self.assertEquals("full of wonders.".split(), structured.next_words(5))

	def test_combine_end(self):
		texts = ["This is a text.", "It is full of wonders."]
		structured = Book.create_structured((pattern_sentence, pattern_word), texts[0])
		structured2 = Book.create_structured((pattern_sentence, pattern_word), texts[1])
		self.assertEquals("This is a".split(), structured.next_words(3))
		self.assertTrue(structured.current.has_words())
		self.assertEquals((0,3), structured.coord)
		self.assertEquals("text.".split(), structured.next_words(3))
		self.assertFalse(structured.has_words())
		structured = structured.combined(structured2)
		self.assertEquals("It is".split(), structured.next_words(2))
		self.assertEquals((1,2), structured.coord)
		self.assertEquals("full of wonders.".split(), structured.next_words(5))
	
	def test_json(self):
		text = "This is a text. It is full of wonders."
		structured = Book.create_structured((pattern_sentence, pattern_word), text)
		json = structured.to_json()
		restruct = Book.from_json(json)
		self.assertEquals(restruct, structured)
		structured.next_words(3)
		self.assertNotEquals(restruct, structured)
		json = structured.to_json()
		restruct = Book.from_json(json)
		self.assertEquals(restruct, structured)

