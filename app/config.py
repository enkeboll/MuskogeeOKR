import os

BETTERWORKS_TOKEN = os.getenv('BETTERWORKS_TOKEN')
BETTERWORKS_API_URL = 'https://app.betterworks.com/api/beta'

LOOKER_API_URL = 'https://seatgeek.looker.com:19999/api/3.0'
LOOKER_CLIENT_ID = os.getenv('LOOKER_CLIENT_ID')
LOOKER_CLIENT_SECRET = os.getenv('LOOKER_CLIENT_SECRET')
LOOKER_NAMESPACE = 'muskogee'

ONELOGIN_ID = os.getenv('ONELOGOIN_ID')
ONELOGIN_SECRET = os.getenv('ONELOGIN_SECRET')
ONELOGIN_AUTH_URL = 'https://api.us.onelogin.com'
ONELOGIN_API_URL = '{}/api/1'.format(ONELOGIN_AUTH_URL)
ONELOGIN_ALL_USERS_ROLE_ID = 161963
ONELOGIN_BETTERWORKS_NAME = 'BetterWorks'

