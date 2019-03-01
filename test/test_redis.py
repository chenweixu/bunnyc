import redis

a = {
    'mess_code': 1201,
    'body': 'nihao',
}


b =  {
    'c': 1,
    'd': 'ddd'
    }

a.update(b)

print(a)

# data = {
#     'mess_code': 1201,
#     'body': 'nihao',
#     'b': [1,2,4,56,6]
# }

# r = redis.Redis(host='127.0.0.1', port=26379, db=0, decode_responses=True)
# r.hmset('a', data)
