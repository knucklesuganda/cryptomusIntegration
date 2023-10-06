import environs

env = environs.Env()
env.read_env('.env')

BOT_TOKEN = env('BOT_TOKEN')
CRYPTOMUS_API_KEY = env('CRYPTOMUS_API_KEY')
CRYPTOMUS_MERCHANT_ID = env('CRYPTOMUS_MERCHANT_ID')
