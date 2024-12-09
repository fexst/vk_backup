import requests
import json
import configparser
import logging

config = configparser.ConfigParser()
config.read("settings.ini")
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


class VKClient:
    def __init__(self, version='5.199'):
        self.params = {
            'access_token': config["TOKEN"]["TOKEN_VK"],
            'v': version
        }

    def _build_url(self, method):
        base_url = 'https://api.vk.com/method/'
        return f'{base_url}{method}'

    def get_photo(self, user_id, album_id: int):
        url = self._build_url('photos.get')
        params = self.params
        album_ids = ['wall', 'profile', 'saved']
        params.update({
            'owner_id': user_id,
            'album_id': album_ids[album_id],
            'extended': 1,
            'count': 5
        })
        photo = requests.get(f'{url}', params=params)
        best_photo = {}
        dict_size = {'s': 75, 'm': 130, 'x': 604, 'o': 130, 'p': 200,
                     'q': 320, 'r': 510, 'y': 807, 'z': 1000, 'w': 2000}
        logging.info("Initial find best photo")
        try:
            for data in photo.json().get('response').get('items'):
                best_size = 0
                best_size_url = None
                best_type = ''
                for data_1 in data.get('sizes'):
                    if best_size < dict_size.get(data_1.get('type')):
                        best_size = dict_size.get(data_1.get('type'))
                        best_size_url = data_1.get('url')
                        best_type = data_1.get('type')
                if data.get('likes').get('count') not in best_photo:
                    best_photo[data.get('likes').get('count')] = best_size_url
                    with open(f'{data.get('likes').get('count')}.json', 'w') as f:
                        info_photo = [{
                            'file_name': f'{data.get('likes').get('count')}',
                            'size': best_type
                        }]
                        json.dump(info_photo, f, ensure_ascii=False, indent=2)

                else:
                    best_photo[f'{data.get('likes').get('count')}_{data.get('date')}', 'w'] = best_size_url
                    with open(f'{data.get('likes').get('count')}_{data.get('date')}.json', 'w') as f:
                        info_photo = list({
                            'file_name': f'{data.get('likes').get('count')}',
                            'size': best_type
                        })
                        json.dump(info_photo, f, ensure_ascii=False, indent=2)
        except Exception as err:
            logging.error(f": {err}", exc_info=True)
        return best_photo


class Yadi:
    def __init__(self, version='5.199'):
        self.vk = VKClient(version)
        self.authorizaton = config['AUTHORIZATION']['AUTHORIZATION_YADI']

    def backup_photo(self, user_id, album_id):
        url_yadi = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {
            'Authorization': self.authorizaton
        }
        params = {
            'path': "Images",
        }
        logging.info("Create folder")
        try:
            requests.put(url_yadi, params=params, headers=headers)
        except Exception as err:
            logging.error(f"Error: {err}", exc_info=True)

        url_method = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        photos = self.vk.get_photo(user_id, album_id)
        for name, photo in photos.items():
            headers = {
                'Authorization': self.authorizaton
            }
            params = {
                "url": photo,
                "path": f"Images/{name}"
            }
            logging.info(f"Save on Yandex photo with name: {name}")
            try:
                requests.post(url_method, params=params, headers=headers)
            except Exception as err:
                logging.error(f": {err}", exc_info=True)


if __name__ == '__main__':
    yadi = Yadi()
    yadi.backup_photo(2345, 0)
