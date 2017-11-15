import urllib3
import json

http = urllib3.PoolManager()
r = http.request('GET','http://api.magicthegathering.io/v1/cards?set=XLN&rarity')
cards = json.loads(r.data)['cards']
D = {}

for card in cards:
    if(card['rarity'] == 'Rare' or card['rarity'] == 'Mythic Rare') and ("Transforms from" not in card['text']):
            D[card['name']] = [card['set'],card['rarity']]
print(D)
