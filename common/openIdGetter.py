import requests

class OpenidGetter:
    def __init__(self, appid, secret):
        self.access_token = self.get_access_token(appid, secret)
        self.next_openid = None

    @staticmethod
    def get_access_token(appid, secret):
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
        response = requests.get(url)
        response_json = response.json()
        return response_json.get('access_token')

    def get_openids(self):
        url = 'https://api.weixin.qq.com/cgi-bin/user/get'
        params = {'access_token': self.access_token}
        if self.next_openid:
            params['next_openid'] = self.next_openid
        response = requests.get(url, params=params)
        data = response.json()
        self.next_openid = data['next_openid']
        return data.get('data', {}).get('openid')
appid = 'wxa31121df217466fd'
secret = '23f9655e97542d4230a1ac9eea819ee7'
getter = OpenidGetter(appid, secret)
openids = getter.get_openids()  # First call
print(openids)
# ... do something with openids ...
more_openids = getter.next_openid # Second call, uses next_openid from first call
print(more_openids)
# ... and so on ...

