from datetime import datetime

import vk_api

from config import acces_token, user_id
from vk_api.exceptions import ApiError

class VkTools():
    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):
        try: 
            info, = self.api.method('users.get',
                                    {'user_id': user_id,
                                    'fields': 'city,bdate,sex,relation,home_town'
                                    }
                                    )
            
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        user_info = {'name': (info['first_name'] + ' ' + info['last_name']) if info.get('first_name') is not None else None,
                        'id':  info.get('id'),
                        'bdate': info.get('bdate') if info.get('bdate') is not None else None,
                        'home_town': info.get('home_town') if info.get('home_town') is not None else None,
                        'sex': info.get('sex') if info.get('sex') is not None else None,
                        'city': info.get('city')['id'] if info.get('city') is not None else None, 
                        }

        return user_info

    def user_age(self, bdate):
        curent_year = datetime.now().year
        user_year = int(bdate.split('.')[2])
        return curent_year - user_year

    def serch_users(self, params):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        age = self.user_age(params['bdate'])
        age_from = age - 3
        age_to = age + 3

        try: 
            users = self.api.method('users.search',
                                    {'count': 50,
                                    'offset': 0,
                                    'age_from': age_from,
                                    'age_to': age_to,
                                    'sex': sex,
                                    'city': city,
                                    'status': 6,
                                    'is_closed': False
                                    }
                                    )
        except ApiError as e:
            users = {}
            print(f'error = {e}')
        
        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                            }
                           )

        return res

    def get_photos(self, user_id):
        try: 
            photos = self.api.method('photos.get',
                                    {'user_id': user_id,
                                    'album_id': 'profile',
                                    'extended': 1
                                    }
                                    )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')
        
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )

        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(user_id)
    users = bot.serch_users(params, 0)

    print(users)
