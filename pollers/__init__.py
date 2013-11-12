from pbl.pollers.pastebin import Pastebin
#from pbl.pollers.gist import Gist
#from pbl.pollers.pastebay import Pastebay
from pbl.pollers.lodgeit import Lodgeit
from pbl.pollers.pastie import Pastie
from pbl.pollers.codepad import Codepad
from pbl.pollers.kde import Kde
from pbl.pollers.pasteitin import Pasteitin
from pbl.pollers.slexy import Slexy

requestoptions = dict(
    timeout=8,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) ' +
            'Ubuntu/11.10 Chromium/17.0.963.65 Chrome/17.0.963.65 Safari/535.11'
    }
)

POLLERS = dict(
    pastebin=Pastebin(
        name='pastebin.com',
        interval=10,
        poll_url='http://pastebin.com/ajax/realtime_data.php',
        regexp=r'created a new [^\[]* \[<a href="\/([^"]+)">[^<]+<\/a>\]'
    ),
#    gist=Gist(
#        name='gist.github.com',
#        interval=5,
#        poll_url='https://gist.github.com/gists',
#        regexp=r'<a href="\/[^"]+">gist: ([^<]+)</a>'
#    ),
#    pastebay=Pastebay(
#        name='pastebay.net',
#        interval=20,
#        poll_url='http://www.pastebay.net/',
#        regexp=r'<li><a href="http:\/\/www\.pastebay\.net\/([^"]+)">[^<]+<\/a><br\/>[^<]+ ago<\/li>'
#    ),
    lodgeit=Lodgeit(
        name='paste.pocoo.org',
        interval=20,
        poll_url='http://paste.pocoo.org/all/',
        regexp=r'<a href="\/show\/[^\/]+\/">Paste #([^<]+)<\/a>'
    ),
    pastie=Pastie(
        name='pastie.org',
        interval=30,
        poll_url='http://pastie.org/pastes',
        regexp=r'<a href="http:\/\/pastie\.org\/pastes\/([^"]+)">View all<\/a>'
    ),
    codepad=Codepad(
        name='codepad.org',
        interval=30,
        poll_url='http://codepad.org/recent',
        regexp=r'<a href="http:\/\/codepad\.org/([^"]+)">view</a>'
    ),
    kde=Kde(
        name='paste.kde.org',
        interval=60,
        poll_url='http://paste.kde.org/all/',
        regexp=r'<legend>Paste #([^<]+)</legend>'
    ),
    pasteitin=Pasteitin(
        name='pasteit.in',
        interval=30,
        poll_url='http://www.pasteit.in/',
        regexp=r'<a href="http:\/\/www\.pasteit\.in/([^"]+)">[^<]+</a>[^<]+ ago</td>'
    ),
    slexy=Slexy(
        name='slexy.org',
        interval=30,
        poll_url='http://slexy.org/recent',
        regexp=r'<a href="/view/([^"]+)">View paste</a>'
    ),

    #~ pastebin_ca=Pastebin('pastebin.ca', 120, 'http://pastebin.ca/archive1', r'')
)
