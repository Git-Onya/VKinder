from datetime import date
import vk_api
from Vkinder.application import config
from sqlalchemy.orm import sessionmaker
from Vkinder.application.create_bd import Pair, Bonds, engine

vk = vk_api.VkApi(token=config.USER_TOKEN)
Session = sessionmaker(bind=engine)
CONN = engine.connect()


class VKinder:
    def __init__(self, seeker_id):
        self.seeker_id = seeker_id
        data = vk.method('users.get', {'user_ids': self.seeker_id, 'fields': 'sex, bdate, city'})
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

    def set_city(self, value):
        self.city = value

    def search(self):
        sex = [1, 2]
        sex.remove(self.sex)
        pairs = vk.method('users.search',
                          {'count': 10, 'sex': sex, 'hometown': self.city, 'status': 6,
                           'age_from': self.age - 2,
                           'age_to': self.age + 2, 'has_photo': 1, 'v': '5.131'})['items']
        # если аккаунт не закрыт для пользователя, в бд добавляются id, имя, ссылка и id фоток
        for pair in pairs:
            try:
                pair_id = pair["id"]
                pair_name = f'{pair["first_name"]} {pair["last_name"]}'
                link = f'https://vk.com/id{pair_id}'
                top_photo = self.photos_get(pair_id)
                self.to_bd(pair_id, pair_name, link, top_photo)
            except vk_api.exceptions.ApiError:
                continue

    @staticmethod
    def photos_get(pair_id):
        """метод возвращает строку из идентификаторов медиавложения"""
        photos = vk.method('photos.get', {'owner_id': pair_id, 'album_id': 'profile', 'extended': 1})[
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

    def to_bd(self, pair_id, pair_name, link, top_photo):
        s = Session()
        s.add(Bonds(seeker_id=self.seeker_id, pair_id=pair_id, favorite=False, blacklist=False))
        s.add(Pair(pair_id=pair_id, pair_name=pair_name, link=link, top_photo=top_photo))
        s.commit()

    def check_seeker_id(self):
        return CONN.execute(
            f"""select seeker_id from bonds where seeker_id = {self.seeker_id}""").fetchone() is not None

    def take_from_bd(self):
        pairs = CONN.execute(f"""
            select p.pair_id, p.pair_name, p.link, p.top_photo from pair p
            join bonds b on b.pair_id = p.pair_id
            where b.blacklist  = False and b.seeker_id = {self.seeker_id}
            """)
        for pair in pairs:
            yield pair[0], pair[1], pair[2], pair[3]

    @staticmethod
    def to_blacklist(pair_id):
        s = Session()
        s.query(Bonds).filter_by(pair_id=pair_id).one().blacklist = True
        s.commit()

    @staticmethod
    def to_favorite(pair_id):
        s = Session()
        s.query(Bonds).filter_by(pair_id=pair_id).one().favorite = True
        s.commit()

    def view_favorites(self):
        favorites = CONN.execute(f"""
            select p.pair_name, p.link from pair p
            join bonds b on b.pair_id = p.pair_id
            where b.favorite  = True and b.seeker_id = {self.seeker_id}
            """)
        return favorites
