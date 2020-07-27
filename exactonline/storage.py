import json

class Storage():

    def __init__(self, filename):
        self.filename = filename
        try:
            with open(self.filename) as f:
                self._data = json.load(f)
        except Exception as e:
            print(e)
            self._data = None
    
    def __setitem__(self, k, v):
        self._data.__setitem__(k, v)

    def __getitem__(self, k):
        return self._data.__getitem__(k)

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self._data, f)

def string(value):
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return str(value)

class ExactOnlineConfig(Storage):
    """
    The configuration class.

    The getters all assert that a native-string type is returned (unless
    a different type is explicitly mentioned). This way the callers
    won't have to think about what they get.
    """
    def __init__(self, filename):
        super().__init__(filename)
        if not self._data:
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
        return self['api_url']

    def get_token_url(self):
        return self.get_api_url() + "/oauth2/token"

    def get_redirect_url(self):
        return self['redirect_url']

    def get_iteration_limit(self):
        return self['iteration_limit']

    def get_response_url(self):
        return self.get_redirect_url()

    def get_client_id(self):
        return self['client_id']

    def get_client_secret(self):
        return self['client_secret']

    def get_expiry(self):
        return self['auth']['expiry']

    def set_expiry(self, value):
        self['auth']['expiry'] = int(value)
        self.save()

    def get_access_token(self):
        return self['auth']['access_token']

    def set_access_token(self, value):
        self['auth']['access_token'] = string(value)
        self.save()

    def get_code(self):
        return self['auth']['code']

    def set_code(self, value):
        self['auth']['code'] = string(value)
        self.save()

    def get_division(self):
        return self['division']

    def set_division(self, value):
        self['division'] = int(value)
        self.save()

    def get_refresh_token(self):
        return self['auth']['refresh_token']

    def set_refresh_token(self, value):
        self['auth']['refresh_token'] = string(value)
        self.save()

    # ; aliases

    def get_refresh_url(self):
        "Alias for get_token_url()."
        return self.get_token_url()
