from parser import DateFromString

from urllib2 import urlopen
from xml.dom import minidom

'''
<?xml version="1.0" encoding="UTF-8"?>
<gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
    <gesmes:subject>Reference rates</gesmes:subject>
    <gesmes:Sender>
        <gesmes:name>European Central Bank</gesmes:name>
    </gesmes:Sender>
    <Cube>
        <Cube time='2009-02-24'>
            <Cube currency='USD' rate='1.2763'/>

            <Cube currency='JPY' rate='122.40'/>
            <Cube currency='BGN' rate='1.9558'/>
            <Cube currency='CZK' rate='28.363'/>
            <Cube currency='DKK' rate='7.4498'/>
            <Cube currency='EEK' rate='15.6466'/>
            <Cube currency='GBP' rate='0.87970'/>
            <Cube currency='HUF' rate='299.05'/>
            <Cube currency='LTL' rate='3.4528'/>
            <Cube currency='LVL' rate='0.7071'/>

            <Cube currency='PLN' rate='4.6830'/>
            <Cube currency='RON' rate='4.2725'/>
            <Cube currency='SEK' rate='11.3423'/>
            <Cube currency='CHF' rate='1.4805'/>
            <Cube currency='NOK' rate='8.7350'/>
            <Cube currency='HRK' rate='7.5050'/>
            <Cube currency='RUB' rate='45.9195'/>
            <Cube currency='TRY' rate='2.1675'/>
            <Cube currency='AUD' rate='1.9797'/>

            <Cube currency='BRL' rate='3.0558'/>
            <Cube currency='CAD' rate='1.5996'/>
            <Cube currency='CNY' rate='8.7264'/>
            <Cube currency='HKD' rate='9.8956'/>
            <Cube currency='IDR' rate='15315.60'/>
            <Cube currency='INR' rate='63.7100'/>
            <Cube currency='KRW' rate='1933.19'/>
            <Cube currency='MXN' rate='19.0488'/>
            <Cube currency='MYR' rate='4.6770'/>

            <Cube currency='NZD' rate='2.5072'/>
            <Cube currency='PHP' rate='61.450'/>
            <Cube currency='SGD' rate='1.9508'/>
            <Cube currency='THB' rate='45.565'/>
            <Cube currency='ZAR' rate='12.8660'/>
        </Cube>
    </Cube>
</gesmes:Envelope>
'''

def dailyfx():
    url = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
    nss = 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'
    dom = minidom.parse(urlopen(url))
    dt  = None
    ccys = {}
    for node in dom.getElementsByTagNameNS(nss, 'Cube'):
        date  = node.getAttribute('time')
        if date:
            dt = DateFromString(date).date()
        else:
            ccy   = node.getAttribute('currency')
            if ccy:
                ccys[ccy] = node.getAttribute('rate')
    return dt,ccys
                
                        


if __name__ == '''__main__''':
    dte,ccys = dailyfx()
    print dte