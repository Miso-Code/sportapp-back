import unittest
from app.wrapper.firebase_wrapper import FirebaseWrapper


class WrapperTest(unittest.TestCase):
    def test_wrapper(self):
        firebase_wrapper = FirebaseWrapper()

        self.assertIsNotNone(firebase_wrapper.messaging)
        self.assertIsNotNone(firebase_wrapper.credentials)
        self.assertIsNotNone(firebase_wrapper.initialize_app)
