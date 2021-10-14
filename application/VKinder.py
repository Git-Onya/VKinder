from datetime import date
import vk_api
from Vkinder import config
import csv

# здесь я использую свой токен от приложения ВК, т.к. используемые классом методы не работают с токеном сообщества
# по заданию этот токен нужно получить у пользователя, мне не понятно как и где. Не в окне же чата с ботом он его вводит?
# так же нужно уточнить город и возраст, если они не указаны в профиле. тот же вопрос: где и как? ))
# пробовала спрашивать ботом сразу после создания экземпляра класса vkider путем создания вложенных longpoll.listen,
# но так не работает.


# это нужно вписать в инит класса или оставить здесь?
session = vk_api.VkApi(token=config.USER_TOKEN)


class VKinder:
    def __init__(self, seeker_id):
        self.seeker_id = seeker_id
        data = session.method('users.get', {'user_ids': self.seeker_id, 'fields': 'sex, bdate, city'})
        today = date.today()
        self.name = data[0]['first_name']
        self.sex = data[0]['sex']
        try:
            self.city = data[0]['city']['title']
        except KeyError:
            self.city = None
        try:
            self.age = int(today.year - int(data[0]['bdate'].split('.')[-1]))
        except KeyError:
            self.age = None
        # создается файл бд с заголовком
        with open(f'application/bd/{self.seeker_id}.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            headers = ['pair_id', 'pair_name', 'link', 'photos']
            writer.writerow(headers)

    def set_city(self, value):
        self.city = value

    def search(self):
        sex = [1, 2]
        sex.remove(self.sex)
        pairs = session.method('users.search',
                               {'count': 10, 'sex': sex, 'hometown': self.city, 'status': 6,
                                'age_from': self.age - 2,
                                'age_to': self.age + 2, 'has_photo': 1, 'v': '5.131'})['items']

        # если аккаунт не закрыт для пользователя, в бд добавляются id, имя, ссылка и id фоток
        for pair in pairs:
            try:
                searched_name = f'{pair["first_name"]} {pair["last_name"]}'
                searched_id = pair["id"]
                searched_link = f'https://vk.com/id{searched_id}'
                top_photos = self.photos_get(searched_id)
                self.to_bd(searched_id, searched_name, searched_link, top_photos)
            except vk_api.exceptions.ApiError:
                continue

    def photos_get(self, pair_id):
        """метод возвращает строку из идентификаторов медиавложения"""
        photos = session.method('photos.get', {'owner_id': pair_id, 'album_id': 'profile', 'extended': 1})[
            'items']
        count = 0
        photos_list = []
        for photo in sorted(photos, key=lambda x: x['likes']['count'], reverse=True):
            if count < 3:
                photos_list.append(photo['id'])
                count += 1
            else:
                break
        return ','.join([str(i) for i in photos_list])

    def to_bd(self, *args):
        """вместо бд в Postgres пока использую csv"""
        with open(f'application/bd/{self.seeker_id}.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(args)

    def take_from_bd(self):
        with open(f'application/bd/{self.seeker_id}.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                yield row['pair_id'], row['pair_name'], row['link'], row['photos']

    def to_blacklist(self):
        pass

    def to_favorite(self):
        pass

    def get_favorite(self):
        pass

    def like_photo(self):
        pass


# if __name__ == '__main__':
    # my_id = 'id4094327'
    # test = VKinder(my_id)
    # test.search()
    # a = test.take_from_bd()
    # print(next(a))
    # print(next(a))
    # print(next(a))
