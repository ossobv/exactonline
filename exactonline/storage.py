import json

def string(value):
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return str(value)

class ExactOnlineConfig():
    """
    The configuration class.

    The getters all assert that a native-string type is returned (unless
    a different type is explicitly mentioned). This way the callers
    won't have to think about what they get.
    """
    def __init__(self):
        self._data = {
            "api_url": "https://start.exactonline.nl/api",
            "redirect_url": "https://www.example.com/",
            "client_id": "",
            "client_secret": "",
            "iteration_limit": 60,
            "division": 0,
            "auth": {
                "expiry": 0,
                "access_token": "",
                "refresh_token": "",
                "code": ""
            }
        }
        self.save()

    def get_auth_url(self):
        return self.get_api_url() + "/oauth2/auth"

    def get_api_url(self):
        return self._data['api_url']

    def get_token_url(self):
        return self.get_api_url() + "/oauth2/token"

    def get_redirect_url(self):
        return self._data['redirect_url']

    def get_iteration_limit(self):
        return self._data['iteration_limit']

    def get_client_id(self):
        return self._data['client_id']

    def get_client_secret(self):
        return self._data['client_secret']

    def get_expiry(self):
        return self._data['auth']['expiry']

    def set_expiry(self, value):
        self._data['auth']['expiry'] = int(value)
        self.save()

    def get_access_token(self):
        return self._data['auth']['access_token']

    def set_access_token(self, value):
        self._data['auth']['access_token'] = string(value)
        self.save()

    def get_code(self):
        return self._data['auth']['code']

    def set_code(self, value):
        self._data['auth']['code'] = string(value)
        self.save()

    def get_division(self):
        return self._data['division']

    def set_division(self, value):
        self._data['division'] = int(value)
        self.save()

    def get_refresh_token(self):
        return self._data['auth']['refresh_token']

    def set_refresh_token(self, value):
        self._data['auth']['refresh_token'] = string(value)
        self.save()
    
    def save(self):
        pass

class Storage(ExactOnlineConfig):

    def __init__(self, filename=None):
        super().__init__()
        self.filename = filename
        if self.filename:
            try:
                with open(self.filename) as f:
                    self._data = json.load(f)
            except Exception as e:
                print(e)

    def save(self):
        if self.filename:
            with open(self.filename, 'w') as f:
                json.dump(self._data, f)