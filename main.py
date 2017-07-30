#!/usr/bin/env python3
from bottle import auth_basic, request, route, run, template, error, redirect, static_file as sf
import onetimepass as otp
from time import gmtime, strftime
from base64 import b64decode
from os import getenv
import json

_cred = str(b64decode(getenv('TOFU_CRED','')),'utf-8').split('$')
_otps = json.loads(str(b64decode(getenv('TOFU_OTPS','')),'utf-8').split('$')[0])

http_user = _cred[0]
http_pass = _cred[1]

def check(user, pw):
    return True if user == http_user and pw == http_pass else False

def get_otp(n):
    return str(otp.get_totp(n)).zfill(6)

def list_otps():
    htmline = '<a href="./{}">{}</a>: {}<br/>\n'
    otps = [ (s,get_otp(c)) for (s,c) in _otps.items()]
    markup = ''.join([htmline.format(s,s,c) for (s,c) in otps])
    return markup

@route('/ping')
def ping():
    return 'pong'

@route('/2fa/')
@route('/2fa/<key>')
@auth_basic(check)
def page(key=None):
    sec = int(strftime("%S", gmtime()))
    waits = (30-sec if sec<30 else 60-sec)+1
    if key in _otps:
        rcode = get_otp(_otps.get(key))
        _title = rcode
        _body = rcode
    else:
        _title = '2fa'
        _body = list_otps()
    return template(_html, rld = waits, title = _title, body = _body)

### For passing through files
@route('/static/<filename:path>')
def send_static(filename): return sf(filename, root='.')

### Catch-all section
@route('/<X>')
@route('/<X>/')

def redir(X): redirect('/2fa/')

_html = '''<!doctype html><html><head>
<meta http-equiv="refresh" content="{{rld}}"/>
<title>{{title}}</title>
</head>
<body>
{{!body}}
</body>
</html>
'''

if __name__ == '__main__':
    run(host='0.0.0.0', port=8081, debug=True)

