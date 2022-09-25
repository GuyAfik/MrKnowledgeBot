from mr_knowledge_bot.bot.telegram.telegram_click.permission.chat import _PrivateChat, _GroupChat, _SuperGroupChat
from mr_knowledge_bot.bot.telegram.telegram_click.permission.user import _GroupCreator, _GroupAdmin, _UserId, _UserName, _Nobody, _Anybody

PRIVATE_CHAT = _PrivateChat()
NORMAL_GROUP_CHAT = _GroupChat()
SUPER_GROUP_CHAT = _SuperGroupChat()
GROUP_CHAT = NORMAL_GROUP_CHAT | SUPER_GROUP_CHAT

ANYBODY = _Anybody()
NOBODY = _Nobody()
USER_ID = _UserId
USER_NAME = _UserName
GROUP_CREATOR = (_GroupCreator() & GROUP_CHAT)
GROUP_ADMIN = (_GroupAdmin() & GROUP_CHAT)