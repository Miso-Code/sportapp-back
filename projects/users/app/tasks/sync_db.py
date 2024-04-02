from ..config.db import session_local
from ..config.settings import Config
from ..models.users import User
from ..services.users import UsersService
from ..utils.user_cache import UserCache
from ..utils.utils import sleep


async def sync_users():
    db = session_local()
    while Config.SYNC_USERS:
        if UserCache.users:
            process_users = UserCache.users[: Config.TOTAL_USERS_BY_RUN]
            repeated_users = db.query(User).filter(User.email.in_([user.email for user in process_users])).all()
            for i, user in enumerate(repeated_users):
                del process_users[i]
                UserCache.users_with_errors_by_email_map[user.email] = user

            UsersService(db).create_users(process_users)
            UserCache.users = UserCache.users[Config.TOTAL_USERS_BY_RUN :]
            UserCache.users_success_by_email_map.update({user.email: user for user in process_users})
        await sleep(1)
