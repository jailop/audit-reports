#!/usr/bin/python

# Audit Reports Scrapper
#
# It obtains a list of audit reports published
# by Corte de Cuentas (El Salvador)
#
# (2019) Jaime Lopez <jailop AT gmail DOT com>

import sys
import re
import requests
from lxml import html
import pandas as pd

site = "http://www.cortedecuentas.gob.sv"
url_base = "/index.php/es/resultado-del-proceso-de-fiscalizacion/informes-finales-de-auditoria/"

def getAdministrativeUnits(site, url):
    """
    This function get the link in which audit reports are indexed for each
    administrative unit (direcciones de auditoria).
    """
    try:
        page = requests.get(site + url);
    except:
        print("error: main page cannot be obtained")
        sys.exit(0)
    if page.status_code != 200:
        print("error: main page request failed")
        sys.exit(0)
    data = html.fromstring(page.content)
    urls = data.xpath("//a/@href")
    res = []
    r_year = re.compile("[0-9]{4}")
    for link in urls:
        if (url in link and len(url) < len(link)):
            if len(r_year.findall(link)) == 1: 
                res.append(link)
    return list(set(res))

def splitDescription(description):
    date = re.compile('\d{2}/\d{2}/\d{4}')
    pos = description.rfind(".")
    entity = description[0:pos]
    period = date.findall(description[pos:])
    if len(period) == 2:
        start = period[0]
        end = period[1]
    else:
        start = ''
        end = ''
    return {'entity': entity, 'start': start, 'end': end} 

def getReports(site, url):
    """
    This function returns the references of audit reports
    indexed for each page.
    """
    date = re.compile('\d{4}')
    y = date.findall(url)
    if len(y) > 0:
        year = y[0]
    else:
        year = None
    try:
        fields = {'limit': 0}
        page = requests.post(site + url, fields)
    except:
        return None
    if page.status_code != 200:
        return None
    data = html.fromstring(page.content)
    title = data.xpath('//a[@class=""]/text()')
    href = [site + link for link in data.xpath('//a[@class=""]/@href')]
    # desc = data.xpath('//div[@class="pd-fdesc"]/text()')
    # desc = [splitDescription(d) for d in desc]
    out = pd.DataFrame({"title": title, "url": href})
    out['year'] = year
    print("%s: %d records" % (url, len(out)))
    return out
    
def scrap():
    links = getAdministrativeUnits(site, url_base)
    df = getReports(site, links[0])
    for l in links[1:]: 
        out = getReports(site, l)
        df = df.append(out)
    df.to_csv("audit-reports.csv", index=False)
    df.to_excel("audit-reports.xlsx", index=False)

if __name__ == "__main__":
    scrap()
