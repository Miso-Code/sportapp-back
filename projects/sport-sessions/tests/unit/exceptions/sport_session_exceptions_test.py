import unittest
from app.exceptions.exceptions import NotFoundError, NotActiveError


class TestSportExceptions(unittest.TestCase):
    def test_not_found_error(self):
        with self.assertRaises(NotFoundError) as context:
            raise NotFoundError("Entity not found")
        self.assertEqual(str(context.exception), "Entity not found")

    def test_not_active_error(self):
        with self.assertRaises(NotActiveError) as context:
            raise NotActiveError("Entity not active")
        self.assertEqual(str(context.exception), "Entity not active")
