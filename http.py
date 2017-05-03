import urllib2
from urllib2 import URLError

def load_html_page(url, values):

    requesturl = url + '?'

    for key, value in values.items():
        requesturl += key + "=" + str(value) + '&'

    print requesturl

    try:
        response = urllib2.urlopen(requesturl, None)

    except URLError as e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    except:
        print "Cannot get response from server '{}'".format(url)
        return ''

    else:
        results = response.read()
        return results



