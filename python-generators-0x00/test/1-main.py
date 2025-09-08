stream_module = __import__('0-stream_users')
stream_users = stream_module.stream_users  # get the function

from itertools import islice

for user in islice(stream_users(), 6):
    print(user)
