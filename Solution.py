import re
import phonenumbers
from functools import total_ordering


messenger = {'chat_id1': {'users_in_chat': {'user_id1': '+79854321234', 'user_id2': '83424562354'},
                          'messsages': [('timestamp1_1', 'text1_1', 'user_id1'),
                                        ('timestamp1_2', 'text1_2', 'user_id2'),
                                        ('timestamp1_3', 'text1_3', 'user_id1')
                                       ]
                         },
             'chat_id2': {'users_in_chat': {'user_id1': '8(985)4321234', 'user_id3': '79162342359'},
                          'messsages': [('timestamp2_1', 'text2_1', 'user_id1'),
                                        ('timestamp2_2', 'text2_2', 'user_id3'),
                                        ('timestamp2_3', 'text2_3', 'user_id1')
                                       ]
                          }
             }


@total_ordering
class MessengerHandler:

    def normalize_phone(self, phone):
        phone = phonenumbers.parse(phone, "RU")
        phone = phonenumbers.format_number(phone,
                                           phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return phone
    
    def __init__(self, messenger):
        self.messenger = messenger
        
        self.unique_users = set()
        for k, v in messenger.items():
            cur_users = v['users_in_chat']
            normalized_phone_num = set(map(self.normalize_phone,
                                           cur_users.values()))
            self.unique_users |= normalized_phone_num

    def __lt__(self, other):
        '''
        Compare messengers by count of unique users
        '''
        return len(self.unique_users) < len(self.unique_users)
    
    def __add__(self, other):
        '''
        Union
        '''
        return self.unique_users | other.unique_users
    
    def __sub__(self, other):
        '''
        Difference
        '''
        return self.unique_users - other.unique_users
    
    def __and__(self, other):
        '''
        Intersection
        '''
        return self.unique_users & other.unique_users
    
    def __eq__(self, other):
        '''
        Check messengers on equality by count of unique users
        '''
        return len(self.unique_users) == len(self.unique_users)        

    def add_user(self, chat_id, *users_id):
        for user_id in users_id:
            if user_id in self.messenger[chat_id]['users_in_chat']:
                print(f'User with id {user_id} is already in this chat!')
                continue
            self.messenger[chat_id]['users_in_chat'].add(user_id)
            print(f'User {user_id} is added to chat {chat_id}')

    def find_regex(self, chat_id: int, regex: str) -> None:
        for m in self.messenger[chat_id]['messages'][::-1]:
            if re.search(regex, m[1]):
                print(f'User: {m[2]}, time: {m[0]}')
                print(m[1] + '\n')

    def show_shared_chats(self, *users_id):
        for chat_id, chat in self.messenger.items():
            if len(set(users_id) & chat[users_in_chat]) == len(users_id):
                print(f'Chat {chat_id} is common for given users')

