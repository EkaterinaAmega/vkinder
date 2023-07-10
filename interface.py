# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import database_add_user, database_check_user

class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if self.params == None:
                    self.params = self.api.get_profile_info(event.user_id)

                if command == 'привет':
                    self.message_send(
                        event.user_id, f'Здравствуйте {self.params["name"]}')
                elif command == 'поиск':
                    self.message_send(event.user_id, 'Начинаем искать..')
                    active = self.search_active_user(event)

                    if active != None:
                        self.output_finded_profile(event, active)
                        database_add_user(event.user_id, active['id'])
                    else:
                        self.message_send(event.user_id, 'Закончился поиск, дождитесь новых пользователей..')
                elif command == 'пока':
                    self.message_send(event.user_id, 'До скорых встреч :)')
                else:
                    self.message_send(event.user_id, 'Команда не найдена')

    def search_active_user(self, event):
         users = self.api.serch_users(self.params)

         for user in users:
            if database_check_user(event.user_id, user['id']) != True:
                return user
         
    def output_finded_profile(self, event, active):
        photos_user = self.api.get_photos(active['id'])

        attachment = ''
        for num, photo in enumerate(photos_user):
            attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
            if num == 2:
                break
                            
        self.message_send(event.user_id,
                            f'Найден {active["name"]} / Ссылка: vk.com/id{active["id"]}',
                            attachment=attachment)

if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
