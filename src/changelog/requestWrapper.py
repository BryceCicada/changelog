from urllib2 import Request, urlopen, URLError, HTTPError

class RequestWrapper:
    def __init__(self):
        pass

    def call(self, request):
        result = {}
        try:
            response = urlopen(request)
            result['body'] = response.read()
            result['code'] = response.getcode()
        except HTTPError, e:
            result['code'] = e.getcode()
            result['body'] = ''
        except URLError, e:
            print 'No kittez. Got an error code:', e
            exit(1)
        return result
