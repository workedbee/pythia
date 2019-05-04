import urllib2
from urllib2 import URLError


def load_html_page(url, values):
    request_url = url + '?'

    for key, value in values.items():
        request_url += key + "=" + str(value) + '&'

    print request_url

    try:
        response = urllib2.urlopen(request_url, None)

    except URLError as url_exception:
        if hasattr(url_exception, 'reason'):
            print 'We failed to reach a server. Reason: ', url_exception.reason
        elif hasattr(url_exception, 'code'):
            print 'The server couldn\'t fulfill the request. Error code: ', url_exception.code
    except Exception as exception:
        print "Cannot get response from server '{}': ".format(url), exception.message
    else:
        results = response.read()
        return results

    return ''


