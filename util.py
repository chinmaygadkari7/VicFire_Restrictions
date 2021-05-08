import urllib
import mysql.connector
from datetime import datetime
import logging
from collections import defaultdict
import re
from lxml import etree

DATE_LAST_UPDATED = datetime.today().date()
        

def _update(cursor):
    urls = {
        "mallee": "https://www.cfa.vic.gov.au/documents/50956/50964/mallee-firedistrict_rss.xml",
        "wimmera": "https://www.cfa.vic.gov.au/documents/50956/50964/wimmera-firedistrict_rss.xml",
        "south west": "https://www.cfa.vic.gov.au/documents/50956/50964/southwest-firedistrict_rss.xml",
        "northern country": "https://www.cfa.vic.gov.au/documents/50956/50964/northerncountry-firedistrict_rss.xml",
        "north central": "https://www.cfa.vic.gov.au/documents/50956/50964/northcentral-firedistrict_rss.xml",
        "central": "https://www.cfa.vic.gov.au/documents/50956/50964/central-firedistrict_rss.xml",
        "north east": "https://www.cfa.vic.gov.au/documents/50956/50964/northeast-firedistrict_rss.xml",
        "east gippsland": "https://www.cfa.vic.gov.au/documents/50956/50964/eastgippsland-firedistrict_rss.xml",
        "west and south gippsland": "https://www.cfa.vic.gov.au/documents/50956/50964/westandsouthgippsland-firedistrict_rss.xml"
    }
    
    rss = defaultdict(dict)
    query = "UPDATE restrictions SET fire_ban='{}' start='{}' end='{}' WHERE council='{}'"
    for region, url in urls.items():
        feed = get(url)
        for f in feed:
            rss[f[0]]["fire_ban"] = 'False' if f[1].startswith("No restrictions") else 'True'
            rss[f[0]]["start"] = datetime.strptime(f[2], "%d/%m/%Y").strftime("%Y-%m-%d")
            rss[f[0]]["end"] = datetime.strptime(f[3], "%d/%m/%Y").strftime("%Y-%m-%d")
            
    
    for council, data in rss.items():
        cursor.execute(query.format(data['fire_ban'], data['start'], data['end'], council))
            
def _get_url(url):
    response = urllib.request.urlopen(url)
    r = etree.fromstring(response.read())
    item = [_ for _ in r.iterfind(".//item")][1]
    to_clean = item.find("description").text
    to_clean = to_clean.replace("<p>", "")
    to_clean = to_clean.split("<br/>")
    to_clean = [_ for _ in to_clean if len(_)!=0]
    to_clean = [ [_b.strip() for _b in re.split(r"[-:]", _) if _b.strip() !='Restrictions'] for _ in to_clean]
    
    for itm in to_clean:
        if len(itm) > 4:
            _ = itm.pop(1)
            
    return to_clean


def get_data(locality):
    mydb = mysql.connector.connect(host="localhost", user="chinmay", password="foopass")
    cursor = mydb.cursor()
    cursor.execute("USE firesafe;")
    
    if datetime.today().date() > DATE_LAST_UPDATED:
        update(cursor)
        DATE_LAST_UPDATED = datetime.today().date()
        
                       
    query = "SELECT locality, fire_ban, start, end FROM restriction WHERE locality='{locality}';"
    #cursor.execute("SELECT * from restriction;")
    _ = cursor.execute(query.format(locality=locality.upper()))
    result = cursor.fetchone()

    if result is None:
        raise LookupError("Locality not found.")

    _, fire_ban, start, end = result
    result = {
        "locality": locality,
        "fire_ban": True if fire_ban.lower() == 'true' else False,
        "start": datetime.strftime(start, "%Y-%m-%d"),
        "end": datetime.strftime(end, "%Y-%m-%d")
    }
    cursor.close()
    mydb.close()
    return result
