import os
from urllib.parse import urlencode
import requests


class Yandex:

    def __init__(self, token: str):
        self.headers = {"Authorization": token}

    def make_folder(self, folder_name: str):
        # создаем папку для бэкапа
        url = f"https://cloud-api.yandex.net/v1/disk/resources?path=%2F{folder_name}"
        response = requests.put(url, headers=self.headers)
        if response.status_code == 201:
            print(f'Папка {folder_name} успешно создана')
        elif response.status_code == 409:
            print(f'Папка {folder_name} уже существует')
        else:
            print('!Что-то пошло не так!')
        return print(response.status_code)

    def upload_photos(self, path: str, list_of_photos: list):
        check_url = f"https://cloud-api.yandex.net/v1/disk/resources"
        put_url = f"https://cloud-api.yandex.net/v1/disk/resources/upload"
        # загрузка json файла
        upload_json_get_url = f"https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {"path": f'/{path}/downloaded.json'}
        upload_json_put_response = requests.get("?".join((upload_json_get_url,
                                                          urlencode(params))), headers=self.headers)
        with open("downloaded_photos.json", "rb") as file:
            requests.put(upload_json_put_response.json()["href"], files={"file": file})
        print(f"downloaded_photos.json успешно загружен")
        os.remove("downloaded_photos.json")
        print(f"downloaded_photos.json удален")
        for files in list_of_photos:
            # проверка наличия файла в папке
            params = {"path": f'/{path}/{files["likes"]}'}
            check_response = requests.get("?".join((check_url, urlencode(params))), headers=self.headers)
            if check_response.status_code == 404:   # такого файла еще нет
                params = {
                    "url": files["url"],
                    "path": f'/{path}/{files["likes"]}'
                }
                requests.post("?".join((put_url, urlencode(params))), headers=self.headers)
                print(f'Файл {files["likes"]} успешно загружен')
            elif check_response.status_code == 200:   # файл с таким именем уже есть, к имени добавить дату
                params = {
                    "url": files["url"],
                    "path": f'/{path}/{files["likes"]}_{files["data"]}'
                }
                requests.post("?".join((put_url, urlencode(params))), headers=self.headers)
                print(f'Файл {files["likes"]}_{files["data"]} успешно загружен')
            else:
                print("Что-то пошло не так")
