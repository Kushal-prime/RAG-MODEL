import urllib.request, json
req = urllib.request.Request('http://127.0.0.1:8000/api/query', data=json.dumps({'query':'hi'}).encode(), headers={'content-type': 'application/json'})
try:
    print(urllib.request.urlopen(req).read().decode())
except Exception as e:
    print(e.read().decode())
