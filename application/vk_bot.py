from random import randrange
from Vkinder.application import vkinder, config
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api

vk = vk_api.VkApi(token=config.GROUP_TOKEN)
session = vk.get_api()
longpoll = VkLongPoll(vk)
pairs_found = []
users_extend_info = dict()


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


def vk_bot():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                # в боте указано, что для начала работы нужно написать 'hi'
                request = event.text
                if event.user_id in users_extend_info:
                    if users_extend_info[event.user_id] == 'city':
                        seeker.city = event.text
                        del users_extend_info[event.user_id]
                        seeker.search()
                        write_msg(event.user_id, f"Great, if you wanna find pair in your city say 'yes'")
                    # elif users_extend_info[event.user_id] == 'age':
                    #     seeker.age = event.text
                    #     del users_extend_info[event.user_id]
                    #     write_msg(event.user_id, f"Great, if you wanna find pair in your city say 'yes'")
                elif request.lower() == 'hi':
                    seeker = vkinder.VKinder(event.user_id)
                    # если записи в бд еще не созданы
                    if not seeker.check_seeker_id():
                        if seeker.city is None:
                            users_extend_info[event.user_id] = 'city'
                            write_msg(event.user_id, f"Hi, {seeker.name}. Where are you from?")
                        # elif seeker.age is None:
                        #     users_extend_info[event.user_id] = 'age'
                        #     write_msg(event.user_id, f"Hi, {seeker.name}. How old are you?")
                        else:
                            seeker.search()
                            write_msg(event.user_id,
                                      f"Hi, {seeker.name}. If you wanna find pair in your city say 'yes'")
                    else:
                        # если уже был, продолжается работа с уже созданной бд
                        write_msg(event.user_id,
                                  f"Hello, my friend! Glad to see you again! Wanna continue? Say 'yes' ))")

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
