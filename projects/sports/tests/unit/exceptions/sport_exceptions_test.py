import unittest
from app.exceptions.exceptions import NotFoundError


class TestSportExceptions(unittest.TestCase):
    def test_not_found_error(self):
        with self.assertRaises(NotFoundError) as context:
            raise NotFoundError("Entity not found")
        self.assertEqual(str(context.exception), "Entity not found")
