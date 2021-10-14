from random import randrange
from Vkinder.application import VKinder
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from Vkinder import config

vk = vk_api.VkApi(token=config.GROUP_TOKEN)
session = vk.get_api()
longpoll = VkLongPoll(vk)

profile_created = []
pairs_found = []


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


def VK_bot():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text
                # в заголовке бота написано, что для начала нужно написать приветствие
                if request.lower() == 'hi' and event.user_id not in profile_created:
                    # если пользователь написал впервые, создается экземпляр класса
                    seeker = VKinder.VKinder(event.user_id)
                    profile_created.append(event.user_id)
                    write_msg(event.user_id, f"Start?")
                elif request.lower() == 'hi' and event.user_id in pairs_found:
                    # если уже был, продолжается работа с уже созданной выборкой
                    write_msg(event.user_id, f"Hi, {seeker.name}. Glad to see you again!")
                    write_msg(event.user_id, '1 - next\n4 - see favorite\n6 - exit')
                elif request.lower() == 'hi' and event.user_id in profile_created and event.user_id not in pairs_found:
                    # если экземпляр класса был создан, но еще не инициализирован поиск
                    write_msg(event.user_id, f"Hi, {seeker.name}. Glad to see you again!")
                    write_msg(event.user_id, f"Start?")
                elif request.lower() == 'start' and event.user_id in profile_created:
                    # если пользователь впервые и экземпляр класса уже создан, подбираются пары и сохраняются в бд
                    seeker.search()
                    pairs = seeker.take_from_bd()
                    pairs_found.append(event.user_id)
                    write_msg(event.user_id, f"Many pairs for you were found. Say 'next' to continue")
                elif (request.lower() == '1' or request.lower() == 'next') and event.user_id in pairs_found:
                    # если пары уже найдены, они по одной выдергиваются из бд
                    searched_id, searched_name, searched_link, top_photos = next(pairs)
                    attachment = ','.join([f'photo{searched_id}_' + i for i in top_photos.split(',')])
                    message = f"Do you like {searched_name}? {searched_link}"
                    vk.method('messages.send',
                              {'user_id': event.user_id, 'message': message, 'random_id': randrange(10 ** 7),
                               'attachment': attachment})
                    write_msg(event.user_id,
                              '1 - next\n2 - like\n3 - to favorite\n4 - see favorite\n5 - to black list\n6 - exit')
                elif request == '2':
                    write_msg(event.user_id, "Liked")
                    write_msg(event.user_id,
                              '1 - next\n4 - see favorite\n6 - exit')
                elif request == '3':
                    write_msg(event.user_id, "Added to favorites")
                    write_msg(event.user_id,
                              '1 - next\n4 - see favorite\n6 - exit')
                elif request == '4':
                    write_msg(event.user_id, "Favorites:")
                    write_msg(event.user_id,
                              '1 - next\n4 - see favorite\n6 - exit')
                elif request == '5':
                    write_msg(event.user_id, "Added to black list")
                    write_msg(event.user_id,
                              '1 - next\n4 - see favorite\n6 - exit')
                elif request == "bye" or request == '6':
                    write_msg(event.user_id, "Goodbye, see u")
                else:
                    write_msg(event.user_id, "I don't understand you :(")
