from requests import get

print(get('http://localhost:5000/api/matches').json())
print(get('http://localhost:5000/api/matches/5').json())
print(get('http://localhost:5000/api/matches/500').json())
