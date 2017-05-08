#!/usr/bin/env python3
from bottle import auth_basic, request, route, run, template, error, redirect, static_file as sf
import onetimepass as otp
import myoptsecrets as s
http_user = s.http_user
http_pass = s.http_pass
codes = s.codes

def check(user, pw):
	return True if user == s.http_user and pw == s.http_pass else False

def decode(n):
	return str(otp.get_totp(n)).zfill(6)

def decodes():
	otps = [ (s,decode(c)) for (s,c) in codes.items()]
	#print(otps)
	htmline = '<a href="./{}">{}</a>: {}<br/>\n'
	markup = ''.join([htmline.format(s,s,c) for (s,c) in otps])
	return markup

@route('/2fa/')
@route('/2fa/<key>')
@auth_basic(check)
def page(key=None):
	if key in codes: 
		rcode = decode(codes.get(key))
		return template(_html, title=rcode, body = rcode)
	else:
	    return template(_html, title='2fa', body = decodes())

_html = '''<!doctype html><html><head>
<meta http-equiv="refresh" content="10"/>
<title>{{title}}</title>
</head>
<body>
{{!body}}
</body>
</html>
'''

### For passing through files
@route('/static/<filename:path>')
def send_static(filename): return sf(filename, root='.')

### Catch-all section
@route('/<X>')
@route('/<X>/')
def redir(X): redirect('/2fa/')

if __name__ == '__main__':
	run(host='0.0.0.0', port=8081)

