import requests

class OpenidGetter:
    _instance = None  # Class attribute acting as the singleton instance

    def __new__(cls, *args, **kwargs):
        # If an instance of OpenidGetter already exists, return it
        if cls._instance is not None:
            return cls._instance
        # Otherwise, create a new OpenidGetter instance and assign it to the class attribute
        cls._instance = super(OpenidGetter, cls).__new__(cls)
        return cls._instance
    def __init__(self, appid, secret):
        self.access_token = self.get_access_token(appid, secret)
        self.next_openid = None
        self.is_first=True

    @staticmethod
    def get_access_token(appid, secret):
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
        response = requests.get(url)
        print(response.status_code)
        response_json = response.json()
        return response_json.get('access_token')

    #def get_openids(self):
    #    url = 'https://api.weixin.qq.com/cgi-bin/user/get'
    #    params = {'access_token': self.access_token}
    #    if self.next_openid:
    #        params['next_openid'] = self.next_openid
    #    print(params)
    #    response = requests.get(url, params=params)
    #    data = response.json()
    #    self.next_openid = data['next_openid']
    #    return data.get('data', {}).get('openid')
    def get_openids(self):
        url = 'https://api.weixin.qq.com/cgi-bin/user/get'
        params = {'access_token': self.access_token}
        if self.next_openid:
            params['next_openid'] = self.next_openid
        response = requests.get(url, params=params)
        if response.status_code==  200:
            self.is_first=False if self.is_first else self.is_first
            data = response.json()
            self.next_openid = data['next_openid'] if data['next_openid'] else self.next_openid
            return data.get('data', {}).get('openid')
appid = 'wxa31121df217466fd'
secret = '23f9655e97542d4230a1ac9eea819ee7'
getter = OpenidGetter(appid, secret)
#print("="*20,"第一次","="*20)
openids = getter.get_openids()  # First call
print(openids)
openids = getter.get_openids()  # First call
print(openids)
# ... do something with openids ...
more_openids = getter.next_openid # Second call, uses next_openid from first call
print("+++",more_openids)
# ... and so on ...
