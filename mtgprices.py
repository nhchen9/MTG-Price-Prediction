from bs4 import BeautifulSoup as bs
import urllib
import datetime
import urllib3
import json
import csv
sets = {"XLN":"Ixalan", "HOU":"Hour+of+Devastation", "AKH":"Amonkhet", "AER":"Aether+Revolt", "KLD":"Kaladesh"}
def getprices(card, setname):
    print("Getting price of", procname(card), "from", sets[setname])
    r = urllib.request.urlopen("https://www.mtggoldfish.com/price/"+ sets[setname] +"/" + procname(card) +"#online").read()
    soup = bs(r, "lxml")
    soup = soup.prettify()
    x = soup.index('(".price-sources-online").toggle(true);')
    y = soup.index('document.getElementById("graphdiv-online"),')
    return(soup[x+142:y-40])

def procname(name):
   z = []
   for i in name:
     if (i.isalpha() or i == '-' or i == '+'):
        z.append(i)
     if i == ' ' and (len(z) > 0 and not(z[len(z)-1] == '+')):
        z.append('+')
   return(''.join(z))

def pconv(prices):
    sol = []
    sol = prices.split('\n  d += "\\n')
    sol[0] = sol[0].replace('  d += "\\n', "")
    for i in range(0, len(sol)):
        sol[i] = sol[i].replace('";', "")
        sol[i] = sol[i].replace(';',"")
        sol[i] = sol[i].replace("'", "")
        if(sol[i] == ";"):
            del sol[i]
    for j in range(1, len(sol)):
        sol[j] = sol[j].split(',')
        sol[j][1] = float(sol[j][1])
    return(sol)

def perprice(card, periods, length):
    now = datetime.date.today()
    prices = pconv(getprices(card, "Ixalan"))
    times= []
    for i in range(0,periods):
        times.append((now-datetime.timedelta(days = length*i)).strftime("%Y-%m-%d"))
    sol = []
    for i in prices:
        if(i[0] in times ):
            sol.append(i)
    for i in range(1, len(sol)):
        sol[i].append(round((sol[i][1]-sol[i-1][1])/sol[i-1][1] , 3))
    sol[0].append(0)
    return (sol)
def curprice(card, setname):
    prices = pconv(getprices(card, setname))
    sol = [prices[len(prices)-1][0], prices[len(prices)-1][1]]
    return sol
def dprice(card, setname, date1, date2):
    prices = pconv(getprices(card, setname))
    sol = ['','']
    for x in prices:
        if date1 in x:
            sol[0] = x[1]
        if date2 in x:
            sol[1] = x[1]
    return (sol)
def getcards(setname):
    d = {}
    http = urllib3.PoolManager()
    r = http.request('GET', 'http://api.magicthegathering.io/v1/cards?rarity=Rare&set=' + setname)
    cards = json.loads(r.data)['cards']
    
    for card in cards:
        if( "Transforms from" not in card['text']) and (card['layout'] != 'aftermath'):
            d[procname(card['name'])] = [card['set'],card['rarity']]

        if( "Transforms from" not in card['text']) and (card['layout'] == 'aftermath'):
            d[procname(card['names'][0] + " " +card['names'][1])] = [card['set'],card['rarity']]

    r = http.request('GET', 'http://api.magicthegathering.io/v1/cards?rarity=mythic%20Rare&set=' + setname)
    cards = json.loads(r.data)['cards']
    for card in cards:
        if("Transforms from" not in card['text']) and (card['layout'] != 'aftermath'):
            d[procname(card['name'])] = [card['set'],card['rarity']]
        if( "Transforms from" not in card['text']) and (card['layout'] == 'aftermath'):
            d[procname(card['names'][0] + " " +card['names'][1])] = [card['set'],card['rarity']]

    return d

def getplays(card, setname):
    r = urllib.request.urlopen("https://www.mtggoldfish.com/price/"+ sets[setname] +"/" + procname(card) +"#online")    .read()
    soup = bs(r,"lxml")
    soup = soup.prettify()
    sol = []
    
    for i in range(34000, min(46000, len(soup)-1000)):
      if("col-num-decks" in soup[i:len(soup)]):
        if(soup[i:min(47500,len(soup)-1000)].index("col-num-decks") == 0):
            try:
                int(soup[i+28])
                try:
                    int(soup[i+29])
                    sol.append(int(soup[i+27:i+30]))
                except ValueError:
                    sol.append(int(soup[i+27:i+29]))
            except ValueError:
                sol.append(int(soup[i+27]))
   # x = soup.index("table-condensed'>")
   # y = soup.index("Commonly Played with in")
   # soup = soup[x:y]
    return(sum(sol))

def getpt():
    pturl = 'https://www.mtggoldfish.com/tournament/pro-tour-ixalan#paper'
    r = urllib.request.urlopen(pturl).read()
    soup = bs(r, "lxml")
    soup = soup.prettify()
    deckids = []
    print(soup.index("data-deckid"))
    cards = {}
    counts = 1
    numdecks= 1
    for i in range(20207, 139700):
        if("data-deckid" in soup[i:139800]):
            if(soup[i:139800].index("data-deckid") == 0):
                deckids.append(soup[i+13:i+19])
    for deckid in deckids:
        print("Getting deck #", numdecks)
        numdecks= numdecks+1
        c = countcards(deckid)
        for key in c.keys():
            if key in cards:
                cards[key][0] = cards[key][0] + c[key][0]
                cards[key][1] = cards[key][1] + c[key][1]
            else: 
                cards[key] = [c[key][0],c[key][1], 0, 0]
            
            if (counts < 9):
                
                cards[key][2] = cards[key][2] + c[key][0]
                cards[key][3] = cards[key][3] + c[key][1]
        counts = counts + 1

    return(cards)
def countcards(deckid):
        url = 'https://www.mtggoldfish.com/deck/' + str(deckid) + "#paper"
        r = urllib.request.urlopen(url).read()
        soup = bs(r,"lxml")
        soup = soup.prettify()
        cards= {}   
        dlist= soup[soup.index("deck_input_deck")+62:soup.index('data-disable-with="Edit Copy"')-64].split("\n")
        board = 0
        for item in dlist:
            if("sideboard" in item):
                board = 1
            else:
              if(board ==0 ):  
                  cards[procname(item[2:len(item)])] = [int(item[0]),0]
              if(board == 1):
                if item[2:len(item)] in cards:
                    cards[procname(item[2:len(item)])][1] = int(item[0])
                else:
                    cards[procname(item[2:len(item)])] = [0,int(item[0])]
        return (cards)
now = datetime.datetime.now()
pt = {}

'''
pt = getpt()
with open('ptcards.csv','w') as csv_file:
    writer = csv.writer(csv_file)
    for key in pt.keys():
        writer.writerow([key, pt[key][0],pt[key][1], pt[key][2],pt[key][3]])
'''

with open('ptcards.csv', 'r') as csv_file:
    for row in csv_file:
      print(row)  
      data = row.split(',')
      if(len(data[0])> 2):
        data[4] = data[4][:-1]
        print(data)
        pt[data[0]] = [int(data[1]),int(data[2]), int(data[3]), int(data[4])]


'''
D = {**getcards("XLN"), **getcards("HOU"), **getcards("AKH"), **getcards("AER"), **getcards("KLD")}

with open('allcards.csv','w') as csv_file:
    writer= csv.writer(csv_file)
    for key in D.keys():
        writer.writerow([key, D[key][0], D[key][1]])
'''
D={}

with open('allcards.csv', 'r') as csv_file:
    writer = csv.writer(csv_file)
    for row in csv_file:
        if len(row)>2:
            data = row.split(',')
            data[2] = data[2][:-1]
            D[data[0]] = [data[1], data[2]]

with open('cards.csv','w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Card Name", "Set","Rarity","Pre-PT Price", "Post-PT Price", "# Decks Total", "#PT Main", "#PT Side","#top 8 main", "#top 8 side"])
    for key in D:
        if (key in pt):
            dp = dprice(key, D[key][0], "2017-10-27","2017-11-12")
            writer.writerow([key, D[key][0], D[key][1], dp[0], dp[1], getplays(key,D[key][0]), pt[key][0], pt[key][1], pt[key][2],pt[key][3]])
 
