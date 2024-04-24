import unittest

from app.exceptions.exceptions import NotFoundError, EntityExistsError, InvalidValueError


class TestExceptions(unittest.TestCase):
    def test_not_found_error(self):
        with self.assertRaises(NotFoundError) as context:
            raise NotFoundError("Entity not found")
        self.assertEqual(str(context.exception), "Entity not found")

    def test_entity_exists_error(self):
        with self.assertRaises(EntityExistsError) as context:
            raise EntityExistsError("Entity already exists")
        self.assertEqual(str(context.exception), "Entity already exists")

    def test_invalid_value_error(self):
        with self.assertRaises(InvalidValueError) as context:
            raise InvalidValueError("Invalid value")
        self.assertEqual(str(context.exception), "Invalid value")
