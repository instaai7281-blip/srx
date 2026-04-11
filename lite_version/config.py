# Lite Version Config
from os import getenv

API_ID = int(getenv("API_ID", "27317669"))
API_HASH = getenv("API_HASH", "11b88c331c5d44fde57cf91de1a2156b")
BOT_TOKEN = getenv("BOT_TOKEN", "7939263258:AAHCZgg2Uy3I-U8ZTuZS85BtEYVh9DGh5d4")
OWNER_ID = list(map(int, getenv("OWNER_ID", "6947378236").split()))
MONGO_DB = getenv("MONGO_DB", "mongodb+srv://beanonymoushacker09:q9gxQwIZDCmVOycI@cluster0.ej0gk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
LOG_GROUP = getenv("LOG_GROUP", "-1002896498332")
CHANNEL_ID = int(getenv("CHANNEL_ID", "-1002267643770"))
STRING = getenv("STRING", None)
# Default limits for Lite version
FREEMIUM_LIMIT = int(getenv("FREEMIUM_LIMIT", "100"))
PREMIUM_LIMIT = int(getenv("PREMIUM_LIMIT", "5000"))
