from random import randrange
from Vkinder.application import VKinder
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from Vkinder import config

vk = vk_api.VkApi(token=config.GROUP_TOKEN)
session = vk.get_api()
longpoll = VkLongPoll(vk)
pairs_found = []


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


def vk_bot():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text
                # экземпляр класса создается сразу при обращении
                seeker = VKinder.VKinder(event.user_id)
                # в заголовке бота написано, что для начала нужно написать приветствие
                if request.lower() == 'hi' and not seeker.check_seeker_id():
                    # если пользователь написал впервые подбираются пары и сохраняются в бд
                    # ... тут нужна проверка, что город и пол != None и возможность их ввести
                    seeker.search()
                    write_msg(event.user_id, f"Hi, {seeker.name}. If you wanna find pair in your city say 'yes'")
                elif request.lower() == 'hi' and seeker.check_seeker_id():
                    # если уже был, продолжается работа с уже созданной бд
                    write_msg(event.user_id, f"Hello, my friend! Glad to see you again! Wanna continue? Say 'yes' ))")
                elif request.lower() == 'yes':
                    pairs = seeker.take_from_bd()
                    pairs_found.append(event.user_id)
                    write_msg(event.user_id, f"Many pairs for you were found. Say 'next' to continue")
                elif (request.lower() == '1' or request.lower() == 'next') and event.user_id in pairs_found:
                    pair_id, pair_name, link, top_photo = next(pairs)
                    attachment = ','.join([f'photo{pair_id}_' + i for i in top_photo.split(',')])
                    message = f"Do you like {pair_name}? {link}"
                    vk.method('messages.send',
                              {'user_id': event.user_id, 'message': message, 'random_id': randrange(10 ** 7),
                               'attachment': attachment})
                    write_msg(event.user_id,
                              '1 - next\n2 - to favorite\n3 - see favorite\n4 - to black list\n5 - exit')
                elif request == '2':
                    seeker.to_favorite(pair_id)
                    write_msg(event.user_id, "Added to favorites")
                    write_msg(event.user_id,
                              '1 - next\n3 - see favorite\n5 - exit')
                elif request == '3':
                    favorites = seeker.view_favorites()
                    write_msg(event.user_id, "Favorites:")
                    for favorite in favorites:
                        write_msg(event.user_id, f"{favorite}")
                    write_msg(event.user_id, '1 - next\n5 - exit')
                elif request == '4':
                    seeker.to_blacklist(pair_id)
                    write_msg(event.user_id, "Added to black list")
                    write_msg(event.user_id,
                              '1 - next\n3 - see favorite\n5 - exit')
                elif request == "bye" or request == '5':
                    write_msg(event.user_id, "Goodbye, see u")
                else:
                    write_msg(event.user_id, "I don't understand you :(")
