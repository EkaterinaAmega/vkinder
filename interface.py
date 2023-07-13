# импорты
import vk_api
import time

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import database_add_user, database_check_user


class BotInterface:
    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None

    def message_send(self, user_id, message, attachment=None):
        self.interface.method(
            "messages.send",
            {
                "user_id": user_id,
                "message": message,
                "attachment": attachment,
                "random_id": get_random_id(),
            },
        )

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if self.params is None:
                    self.params = self.api.get_profile_info(event.user_id)

                if command == "привет":
                    self.message_send(
                        event.user_id, f'Здравствуйте {self.params["name"]}'
                    )
                elif command == "поиск":
                    if self.params is None:
                        self.message_send(
                            event.user_id, "Параметры вашего профиля не заданы"
                        )
                        return

                    check_user_city = self.check_user_city(event, longpoll, self.params)
                    if check_user_city is False:
                        self.message_send(
                            event.user_id, "Параметры вашего профиля не заданы"
                        )
                        return

                    check_user_age = self.check_user_age(event, longpoll, self.params)
                    if check_user_age is False:
                        self.message_send(
                            event.user_id, "Параметры вашего профиля не заданы"
                        )
                        return

                    self.message_send(event.user_id, "Начинаем искать..")
                    active = self.search_active_user(event)

                    if active is not None:
                        self.output_finded_profile(event, active)
                        database_add_user(event.user_id, active["id"])
                    else:
                        self.message_send(
                            event.user_id,
                            "Закончился поиск, дождитесь новых пользователей",
                        )
                elif command == "пока":
                    self.message_send(event.user_id, "До скорых встреч :)")
                else:
                    self.message_send(event.user_id, "Команда не найдена")

    def search_active_user(self, event):
        users = self.api.search_users(self.params)

        for user in users:
            if database_check_user(event.user_id, user["id"]) is not True:
                return user

    def output_finded_profile(self, event, active):
        photos_user = self.api.get_photos(active["id"])

        attachment = ""
        for num, photo in enumerate(photos_user):
            attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
            if num == 2:
                break

        self.message_send(
            event.user_id,
            f'Найден {active["name"]} / Ссылка: vk.com/id{active["id"]}',
            attachment=attachment,
        )

    def check_user_city(self, event, longpoll, params):
        if params["city"] == "":
            self.message_send(event.user_id, f"Введите город:", None)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    city_id = self.api.get_city_id_by_name(event.text)

                    if city_id is False:
                        return False

                    params["city"] = city_id
                    return True
        return True

    def check_user_age(self, event, longpoll, params):
        try:
            time.strptime(params["bdate"], "%d.%m.%Y")
        except ValueError:
            self.message_send(
                event.user_id, f"Введите дату рождения (Формат: 22.22.2023):", None
            )
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    try:
                        time.strptime(event.text, "%d.%m.%Y")
                        params["bdate"] = event.text
                        return True
                    except ValueError:
                        self.message_send(
                            event.user_id, f"Не корректная дата рождения!"
                        )
                        return False
        return True


if __name__ == "__main__":
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
