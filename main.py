import json
import requests
from urllib.parse import urlencode
from datetime import datetime
from yaupload import Yandex


class User:
    def __init__(self, vk_id, token):
        self.id = vk_id
        self.token = token
        self.photo_list = []

    def get_profile_photos(self, album_id="profile"):
        profile_photos_info_list = []
        downloaded_files = []
        url = f"https://api.vk.com/method/photos.get"
        parameters = {
            "owner_id": self.id,
            "album_id": album_id,
            "extended": 1,
            "photo_sizes": 1,
            "count": 5,
            "access_token": self.token,
            "v": 5.122
        }
        url_requests = "?".join((url, urlencode(parameters)))
        resp = requests.get(url_requests)
        self.photo_list = resp.json()["response"]["items"]
        for photo in self.photo_list:
            profile_photos_info_list.append(
                {
                    "url": photo["sizes"][-1]["url"],
                    "likes": photo["likes"]["count"],
                    "size_type": photo["sizes"][-1]["type"],
                    "data": datetime.fromtimestamp(photo["date"]).strftime(
                        '%Y-%m-%d %H:%M:%S').replace("-", "_").split()[0]
                }
            )
            downloaded_files.append({"file_name": f'{photo["likes"]["count"]}.jpg',
                                     "size": photo["sizes"][-1]["type"]})
        with open("downloaded_photos.json", "a") as file:
            json.dump(downloaded_files, file)
        return profile_photos_info_list

    def get_albums_list(self):
        albums_photos_info_list = []
        url = f"https://api.vk.com/method/photos.getAlbums"
        parameters = {
            "owner_id": self.id,
            "count": 10,
            "access_token": self.token,
            "v": 5.122
        }
        url_requests = "?".join((url, urlencode(parameters)))
        response = requests.get(url_requests)

        try:
            for album in response.json()["response"]["items"]:
                albums_photos_info_list.append({"album_id": album["id"], "title": album["title"]})
            return albums_photos_info_list
        except KeyError:
            print('Альбомы пользователя заблокированы\nБудут загружены фотографии из профиля')
            return albums_photos_info_list


def user_initial():
    global index
    vk_id = int(input("Введите vk id - "))
    ya_path = input("Введите название папки для сохнаниения в яндекс диск - ")
    VK_TOKEN = input("Введите Ваш TOKEN Вконтакте - ")
    Ya_disk_TOKEN = input("Введите Ваш TOKEN Я.Диск - ")
    u = User(vk_id, VK_TOKEN)
    y = Yandex(Ya_disk_TOKEN)
    y.make_folder(ya_path)
    if not u.get_albums_list():
        y.upload_photos(ya_path, u.get_profile_photos())
    else:
        print('Выберите альбом для загрузки фото')
        for index, album in enumerate(u.get_albums_list()):
            print(f'{index} - {album["title"]}')
        try:
            index = int(input('Введите номер альбома - '))
            y.upload_photos(ya_path, u.get_profile_photos(u.get_albums_list()[index]["album_id"]))
        except ValueError or IndexError:
            print('Вы ввели несуществующий номер альбома, или букву. Попробуйте еще раз')
            print('Выберите альбом для загрузки фото')
            for index, album in enumerate(u.get_albums_list()):
                print(f'{index} - {album["title"]}')
            try:
                index = int(input('Введите номер альбома - '))
                y.upload_photos(ya_path, u.get_profile_photos(u.get_albums_list()[index]["album_id"]))
            except ValueError or IndexError:
                print('Вы снова ввели неверные данные. До свидания!')


user_initial()
