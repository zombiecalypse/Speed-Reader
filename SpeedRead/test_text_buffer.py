from .text_output_actor import TextBuffer
from pykka.registry import ActorRegistry

import unittest
import time

class TestTextOutput(unittest.TestCase):
    def setUp(self):
        self.received = []
        self.text_buffer = TextBuffer\
            .start(callback = self.received.append, words_per_minute = 10000,
                    words_per_chunk = 2).proxy()

    def tearDown(self):
        ActorRegistry.stop_all()

    def assertReceived(self, msg):
        time.sleep(0.1)
        self.assertIn(msg, self.received)

    def with_text(self, txt):
        self.text_buffer.use_text(txt)
        self.text_buffer.go().get()


    def test_short_text(self):
        self.with_text("Testing this.")
        self.assertReceived('Testing this.')

    def test_single_sentence(self):
        self.with_text("Testing this mess.")
        self.assertReceived('Testing this')
        self.assertReceived('mess.')

    def test_breaks_at_sentence(self):
        self.with_text("Testing this mess. Then get some coffee.")
        self.assertReceived('Testing this')
        self.assertReceived('mess.')
        self.assertReceived('Then get')
        self.assertReceived('some coffee.')
