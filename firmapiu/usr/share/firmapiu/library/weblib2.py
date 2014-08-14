import ldap
import ldapurl
import requests


request_timeout = 5


def _test_ldap_connection(fullurl):
    try:
        host = fullurl.split(':')
        if len(host) == 1:
            s = socket.create_connection((host[0], 389), timeout=request_timeout)
        elif len(host) == 2:
            s = socket.create_connection((host[0], host[1]), timeout=request_timeout)
        s.close()
        return True
    except socket.timeout:
        return False
    except socket.gaierror:
        return False


def execute_download(url):
    if url.startswith('http://'):
        return _http_download(url)
    elif url.startswith('https://'):
        return _https_download(url)
    elif url.startswith('ldap://') or url.startswith('LDAP://'):
        return _ldap_download(url)
        #return None, 'ldap not implemented'
    else:
        return None, 'dowload url not recognized'


def _https_download(url):
    try:
        return _http_download(url)
    except requests.exceptions.SSLError:  # errore ssl nel server
        return _http_download(url, verify=False)


def _http_download(url, verify=True):
    try:
        res = requests.get(url, timeout=request_timeout, verify=verify)
        if res.status_code == 200:
            return res.content, ''
        else:
            return None, '%d bad response code' % res.status_code
    except requests.exceptions.Timeout:
        return None, 'http timeout'


def _ldap_download(url):
    url = url.replace('LDAP', 'ldap')
    if ldapurl.isLDAPUrl(url):
        try:
            ldap_url = ldapurl.LDAPUrl(url)
        except ValueError, e:
            return None, e
        try:
            if not _test_ldap_connection(ldap_url.hostport):
                return None, 'test connection failed'
            l = ldap.initialize('ldap://%s' % ldap_url.hostport)

            l.simple_bind()
            try:
                lis = l.search_st(ldap_url.dn, ldap.SCOPE_BASE, timeout=request_timeout)
                if lis is None:
                    return None, 'ldap search failed'

                lis = lis[0][1]
                if lis.has_key('certificateRevocationList'):
                    return lis['certificateRevocationList'][0], ''
                elif lis.has_key('certificateRevocationList;binary'):
                    return lis['certificateRevocationList;binary'][0], ''
                else:
                    return None, 'ldap no certificateRevocationList found'
            except ldap.TIMEOUT:
                return None, 'ldap timeout'

        except ldap.LDAPError, e:
            return None, 'ldap error: %s' % e
    else:
        return None, 'no ldap url'