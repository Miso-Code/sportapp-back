import asyncio
import unittest
from unittest import mock
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from projects.users.app.models.schemas.schema import UserAdditionalInformation, UserCreate
from projects.users.app.tasks import sync_db
from projects.users.app.utils.user_cache import UserCache
from projects.users.app.config.settings import Config
from projects.users.app.models.users import UserIdentificationType, Gender


class TestSyncDb(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        UserCache.users = []
        UserCache.users_with_errors_by_email_map = {}
        UserCache.users_success_by_email_map = {}
        Config.TOTAL_USERS_BY_RUN = 2
        Config.SYNC_USERS = True

    @patch("sqlalchemy.create_engine")
    @patch("sqlalchemy.orm.sessionmaker")
    async def test_sync_users_empty_users(self, create_engine_mock, session_local_mock):
        create_engine_mock.return_value = MagicMock()
        session_local_mock.return_value = MagicMock()
        await sync_db.sync_users()
        # async def modified_sleep():
        #     Config.SYNC_USERS = False
        #
        # create_engine_mock.return_value = MagicMock(), MagicMock()
        # declarative_base_mock.return_value = MagicMock()
        # sleep_mock.side_effect = modified_sleep
        #
        # await sync_db.sync_users()
        # self.assertEqual(session_local_mock.call_count, 1)
