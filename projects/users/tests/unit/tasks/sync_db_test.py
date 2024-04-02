import unittest
from unittest.mock import MagicMock, patch

import faker
from app.tasks import sync_db
from app.utils.user_cache import UserCache
from app.config.settings import Config
from tests.utils.users_util import generate_random_user_create_data


async def modified_sleep(seconds):
    Config.SYNC_USERS = False


fake = faker.Faker()


class TestSyncDb(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        UserCache.users = []
        UserCache.users_with_errors_by_email_map = {}
        UserCache.users_success_by_email_map = {}
        Config.TOTAL_USERS_BY_RUN = 0
        Config.SYNC_USERS = True
        self.mock_db = MagicMock()
        self.user_1 = generate_random_user_create_data(fake)
        self.user_2 = generate_random_user_create_data(fake)
        self.user_3 = generate_random_user_create_data(fake)

    @patch("app.services.users.UsersService.create_users")
    async def test_sync_users(self, mock_create_users):
        UserCache.users = [self.user_1, self.user_2, self.user_3]

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = []
        mock_create_users.return_value = None
        Config.TOTAL_USERS_BY_RUN = 2
        await sync_db.sync_users(self.mock_db, modified_sleep)

        self.assertEqual(mock_create_users.call_count, 1)
        self.assertEqual(self.mock_db.query.call_count, 1)
        self.assertEqual(mock_query.filter.call_count, 1)
        self.assertEqual(mock_filter.all.call_count, 1)
        self.assertEqual(len(UserCache.users), 1)
        self.assertEqual(UserCache.users[0], self.user_3)
        self.assertEqual(len(UserCache.users_success_by_email_map), 2)
        self.assertEqual(len(UserCache.users_with_errors_by_email_map), 0)

    @patch("app.services.users.UsersService.create_users")
    async def test_sync_users_with_repeated_email(self, mock_create_users):
        UserCache.users = [self.user_1, self.user_2, self.user_3]

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = [self.user_1, self.user_2]
        mock_create_users.return_value = None
        Config.TOTAL_USERS_BY_RUN = 3
        await sync_db.sync_users(self.mock_db, modified_sleep)

        self.assertEqual(mock_create_users.call_count, 1)
        self.assertEqual(self.mock_db.query.call_count, 1)
        self.assertEqual(mock_query.filter.call_count, 1)
        self.assertEqual(mock_filter.all.call_count, 1)
        self.assertEqual(len(UserCache.users), 0)
        self.assertEqual(len(UserCache.users_success_by_email_map), 1)
        self.assertEqual(len(UserCache.users_with_errors_by_email_map), 2)

    async def test_sync_users_empty_users(self):
        await sync_db.sync_users(self.mock_db, modified_sleep)
