import re
import phonenumbers
from functools import total_ordering
from abc import ABC, abstractmethod
from typing import List


class Message:
    def __init__(self, timestamp, from_user, content):
        self.timestamp = timestamp
        self.from_user = from_user
        self.content = content


class MessageContent(ABC):
    def __init__(self, data_path=None, raw_data=None):
        self.data_path = data_path
        self.raw_data = raw_data
        self.data = self.prepare_data()
    
    @abstractmethod
    def prepare_data(self):
        pass


class TextMessageContent(MessageContent):
    def prepare_data(self):
        if self.raw_data:
            return self.raw_data
        else:
            assert True, "You should provide string data for Text message!"


class ImageMessageContent(MessageContent):
    def prepare_data(self):
        if self.data_path:
            with open(self.data_path, 'rb') as f:
                return f.read()
        else:
            assert True, "You should provide path to data for Image message!"


class User:
    def __init__(self, user_id_str, phone_str):
        self.user_id = user_id_str
        self.phone_num = self.normalize_phone(phone_str)
        self.unique_user_id = self.phone_num
        
    def normalize_phone(self, phone):
        phone = phonenumbers.parse(phone, "RU")
        phone = phonenumbers.format_number(phone,
                                           phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return phone


messenger = {'chat_id1': {'users_in_chat': {User('user_id1', '+79854321234'), User('user_id2', '83424562354')},
                          'messsages': [Message('timestamp1_1', 'user_id1', TextMessageContent(raw_data='text1_1')),
                                        Message('timestamp1_2', 'user_id2', TextMessageContent(raw_data='text1_2')),
                                        Message('timestamp1_3', 'user_id1', ImageMessageContent(data_path='path1_3'))
                                       ]
                         },
             'chat_id2': {'users_in_chat': {User('user_id1', '8(985)4321234'), User('user_id3', '79162342359')},
                          'messsages': [Message('timestamp2_1', 'user_id1', TextMessageContent(raw_data='text2_1')),
                                        Message('timestamp2_2', 'user_id3', ImageMessageContent(data_path='path2_2')),
                                        Message('timestamp2_3', 'user_id1', TextMessageContent(raw_data='text2_3'))
                                       ]
                          }
             }


@total_ordering
class MessengerHandler: 
    def __init__(self, messenger):
        self.messenger = messenger
        self.unique_users = _create_unique_users_set()
            
    def _create_unique_users_set():
        unique_users = set()
        for k, v in self.messenger.items():
            cur_users = v['users_in_chat']
            unique_phone_nums = set(map(lambda x: x.unique_user_id, cur_users))
            self.unique_users |= unique_phone_nums    
        return unique_users

    def __lt__(self, other):
        '''
        Compare messengers by count of unique users
        '''
        return len(self.unique_users) < len(self.unique_users)
    
    def __or__(self, other):
        '''
        Union
        '''
        return self.unique_users | other.unique_users
      
    def __and__(self, other):
        '''
        Intersection
        '''
        return self.unique_users & other.unique_users    

    def __sub__(self, other):
        '''
        Difference
        '''
        return self.unique_users - other.unique_users
    
    def __eq__(self, other):
        '''
        Check messengers on equality by count of unique users
        '''
        return len(self.unique_users) == len(self.unique_users)        

    def add_user(self, chat_id: str, *users_to_add: List[User]) -> None:
        for cur_user in users_to_add:
            if cur_user in self.messenger[chat_id]['users_in_chat']:
                print(f'User with id {cur_user.user_id} is already in this chat!')
                continue
            self.messenger[chat_id]['users_in_chat'].add(cur_user)
            print(f'User {cur_user.user_id} is added to chat {chat_id}')

    def find_regex(self, chat_id: str, regex: str) -> None:
        for m in self.messenger[chat_id]['messages'][::-1]:
            if not isinstance(m.content, TextMessageContent):
                continue
            if re.search(regex, m.content.data):
                print(f'User: {m.from_user}, time: {m.timestamp}\n')
                print(m.content.data + '\n')

    def show_shared_chats(self, *users_list: List[User]) -> None:
        for chat_id, chat in self.messenger.items():
            if len(set(users_list) & chat['users_in_chat']) == len(users_list):
                print(f'Chat {chat_id} is common for given users')
