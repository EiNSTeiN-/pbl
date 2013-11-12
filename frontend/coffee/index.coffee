# -*- coding: utf-8 *-*

app_url = '/pbl/'

feed = null
login_details = null

create_menu = () =>

    $('content').insert new Element('div', {'class': 'menu', 'id': 'menu'})
    $('content').insert new Element('div', {'class': 'page', 'id': 'feeds'})

    # menu
    $('menu').insert new Element('span').update('&nbsp;&nbsp;')
    $('menu').insert new Element('a', {'href':'#live', 'id': 'link_live'}).update('all feeds')
    $('menu').insert new Element('span').update('&nbsp;&nbsp;|&nbsp;&nbsp;')
    $('menu').insert new Element('a', {'href':'#pastebin.com', 'id': 'link_pastebin.com'}).update('pastebin.com')

    $('menu').insert new Element('a', {'href':'#login', 'id': 'link_login', 'class': 'link_login'}).update('login')
    $('menu').insert new Element('span', {'id': 'logging_in'}).update('logging in...')
    $('logging_in').hide()

    # events
    $('link_live').observe('click', () => navigate_feed('live'))
    $('link_pastebin.com').observe('click', () => navigate_feed('pastebin.com'))

    $('link_login').observe('click', (event) => login_show(); event.stop())

    return

check_login = () =>
    # Check if the user is logged in or not, and update the local flag

    new Ajax.Request(app_url + 'json/session.py/get',
        onSuccess: (r) =>
            r = r.responseJSON
            if r and (not login_details or (login_details.created is not r.created))
                # we were not logged in before, or the session is not the same we had (should not happen...)
                feed.user_login()
                $('link_login').hide()
                $('menu').insert new Element('span', {'id': 'logged_in_details'}).update('logged in as <b>'+
                    r.username + '</b>')

            login_details = r
    )

    return

is_logged_in = () =>
    return login_details?

login_response = (response) =>

    $('logging_in').hide()

    if response.success
        if feed
            check_login()
    else
        $('link_login').show()

    return

login_submit = () =>

    login_hide()
    $('link_login').hide()
    $('logging_in').show()

    new Ajax.Request(app_url + 'json/session.py/login',
        onSuccess: (r) => @login_response(r.responseJSON),
        parameters:
            u: $('username').value,
            p: $('password').value
    )

    return

login_hide = () =>

    $('link_login').removeClassName('login_shown')

    $('loginbox').hide()

    return

login_show = () =>

    if $('loginbox')?

        $('username').value = ''
        $('password').value = ''

        $('loginbox').show()

        $('link_login').addClassName('login_shown')
        $('username').focus()
        return

    box = new Element('div', {'id': 'loginbox'})
    box.insert new Element('span', {'id': 'label_username'}).update('username')
    box.insert new Element('input', {'type':'text', 'id': 'username'})
    box.insert new Element('br')
    box.insert new Element('span', {'id': 'label_password'}).update('password')
    box.insert new Element('input', {'type':'password', 'id': 'password'})
    box.insert new Element('br')
    box.insert new Element('input', {'type':'button', 'id': 'loginok', 'value': 'login'})
    box.insert new Element('a', {'id': 'logincancel', 'href': '#cancel'}).update('Cancel&nbsp;')

    document.body.insert box
    box.absolutize()
    $('link_login').absolutize()

    top = $('link_login').viewportOffset().top + $('link_login').getHeight() - 2
    left = $('link_login').viewportOffset().left + $('link_login').getWidth() - box.getWidth()
    box.setStyle { 'top': top+'px', 'left': left+'px'}

    $('logincancel').observe('click', (e) => login_hide(); e.stop())
    $('loginbox').observe('keyup', (e) => login_hide() if e.keyCode == 27)

    $('loginok').observe('click', () => login_submit())
    $('loginbox').observe('keypress', (e) => login_submit() if e.keyCode == 13)

    $('link_login').addClassName('login_shown')
    $('username').focus()

    return

find_current_page = () =>
    loc = document.location.href
    i = loc.indexOf('#')
    if i == -1
        page = 'live'
    else
        page = loc.substr(i+1)
    if page not in ['live', 'pastebin.com']
        page = 'live'

    navigate_feed(page)

    return

navigate_feed = (page) =>

    for o in $$('.current_page')
        o.removeClassName('current_page')
    current_page = page

    $('link_'+page).addClassName('current_page')

    if feed?
        feed.remove()

    # load specific feed...
    feed = new Feed(page)

    return

main = () =>

    create_menu()
    check_login()
    find_current_page()

    return

document.observe('dom:loaded', () => main())
