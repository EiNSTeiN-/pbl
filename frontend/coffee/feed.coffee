# -*- coding: utf-8 *-*

class Feed

    constructor: (page) ->
        # page: the name of the feed to display.
        @page = page
        @next_item_id = null
        @create()

        domain = window.location.href.match(/https?:\/\/([^\/]*)\//)
        domain = if domain then domain[1] else ''

        @jar = new CookieJar({
            expires: 60 * 60 * 24 * 365,   # time in seconds
            path: '/',                     # cookie path
            domain: domain,      # cookie domain
            secure: false                  # secure ?
        })

        @seen_updater = null

        return

    create: () =>
        # Create the whole GUI for this feed

        $('feeds').insert new Element('div', {'id': 'waitball'})
        $('waitball').insert new Element('div', {'class': 'pleasewait'}).update('please wait...')
        $('waitball').insert new Element('img', {'src': app_url+'img/goldballs.gif'})

        @load_initial_items()

        # check if user is logged in already...
        if is_logged_in()
            @login_successful()

        return

    load_initial_items: () =>
        # Load the initial leaks list, then start the periodical check for new leaks.

        new Ajax.Request(app_url + 'json/leaks.py?period=initial', {
            onSuccess: (r) => @new_items_callback(r.responseJSON)
        })

        new PeriodicalExecuter((() =>
            if @next_item_id is null
                return
            new Ajax.Request(app_url + 'json/leaks.py?after=' + @next_item_id, {
                onSuccess: (r) => @new_items_callback(r.responseJSON)
            })
        ), 60)

        return

    update_seen: (r) =>

        for seen in r.items
            @mark_seen(seen)

        return

    user_login: () =>
        # This is called upon a successful login. It starts the periodical updated which
        # makes sure we always have the most recent list of seen leaks.

        if @seen_updater
            return

        # update once now
        new Ajax.Request(app_url + 'json/leaks.py/seen', {
            onSuccess: (r) => @update_seen(r.responseJSON)
        })

        @seen_updater = new PeriodicalExecuter((() =>
            new Ajax.Request(app_url + 'json/leaks.py/seen', {
                onSuccess: (r) => @update_seen(r.responseJSON)
            })
        ), 60 * 5)

        return

    user_logout: () =>
        # This is called upon a successful logout.

        return

    add_item: (item) =>

        [id, seen, timestamp, comment, reason, source, metadata] = item

        container = new Element('div', {'class': 'feeditem', 'id': 'feeditem' + id})

        if seen or @is_seen(id)
            container.addClassName('seen')

        container.insert new Element('div', {'class': 'uid'}).update(id + '&nbsp;&nbsp;')
        container.insert new Element('div', {'class': 'favicon ' + source + '_favicon', 'title': 'source: ' + source})

        f = (s) => if s.toString().length is 1 then '0'+s else s
        month = ['jan.', 'feb.', 'march', 'april', 'may', 'june', 'july', 'aug.', 'sept.', 'oct.', 'dec.']
        date = new Date(timestamp * 1000)
        date = f(date.getHours()) + ':' + f(date.getMinutes()) + ', ' +
            month[date.getMonth()] + ' ' + date.getDate() + ', ' + f(date.getFullYear())
        container.insert new Element('span', {'class': 'subtext'}).update('posted on ')
        container.insert new Element('span', {'class': 'date'}).update(date + '&nbsp;&nbsp;')

        if metadata['title']?
            container.insert new Element('span', {'class': 'title'}).update(metadata['title'])
#        else
#            container.insert new Element('span', {'class': 'notitle'}).update('')

        if reason
            container.insert new Element('span', {'class': 'subtext'}).update('  reason ')
            container.insert new Element('span', {'class': 'reason'}).update(reason)
            container.insert new Element('span', {'class': 'subtext'}).update('&nbsp;&nbsp;')

        if comment
            container.insert new Element('span', {'class': 'subtext'}).update('  comment ')
            container.insert new Element('span', {'class': 'comment'}).update(comment)
            container.insert new Element('span', {'class': 'subtext'}).update('&nbsp;&nbsp;')

        if metadata['user']? or metadata['syntax']? or metadata['url']?
            container.insert new Element('br')
            container.insert new Element('div', {'class': 'spacer'}).update('&nbsp;')

        if metadata['user']?
            container.insert new Element('span', {'class': 'subtext'}).update('by ')
            container.insert new Element('a', {'class': 'user', 'href': app_url + '#user:'+metadata['user']}).update(
                metadata['user'])
            container.insert new Element('span', {'class': 'subtext'}).update('&nbsp;&nbsp;')

        if metadata['syntax']?
            container.insert new Element('span', {'class': 'subtext'}).update('syntax ')
            container.insert new Element('span', {'class': 'syntax'}).update(metadata['syntax'])
            container.insert new Element('span', {'class': 'subtext'}).update('&nbsp;&nbsp;')

        if metadata['url']?
            container.insert new Element('span', {'class': 'subtext'}).update('link ')
            container.insert new Element('a', {'href': metadata['url'], 'target': '_blank'}).update(metadata['url'])
            container.insert new Element('span', {'class': 'subtext'}).update('&nbsp;&nbsp;')

        container.observe('click', (e) => @expand_item(e, id))
        container.observe('mouseover', () => @highlight_item(id, true))
        container.observe('mouseout', () => @highlight_item(id, false))

        $('feeds').insert({'top': container })

        return

    highlight_item: (id, highlight) =>
        if highlight
            $('feeditem'+ id).addClassName('feedhightlight')
        else
            $('feeditem'+ id).removeClassName('feedhightlight')

        return

    makevisible: (id) =>
        viewbottom = document.viewport.getScrollOffsets().top + document.body.clientHeight
        itembottom = $('feeditem' + id).cumulativeOffset().top + $('feeditem' + id).getHeight()

        if itembottom > viewbottom
            newtop = document.viewport.getScrollOffsets().top + (itembottom - viewbottom) + 10
#            alert newtop
            window.scrollTo(document.viewport.getScrollOffsets().left, newtop)
        return

    expand_item: (event,id) =>

        return if Event.element(event).tagName == 'A'

        if $('details' + id)?
            $('details' + id).toggle()

            if $('details' + id).visible()
                @makevisible(id)
        else
            if not $('waitball' + id)?
                $('feeditem' + id).insert new Element('div', {'id': 'waitball' + id})
                $('waitball' + id).insert new Element('div', {'class': 'itemloading'}).update('loading...')

            new Ajax.Request(app_url + 'json/details.py?id='+ id, {
                  onSuccess: (r) => @display_details(id, r.responseJSON)
            });

        return

    mark_seen: (id) =>

        seen_list = @jar.get('seen')
        seen_list ?= new Array()

        for seen in seen_list
            if id >= seen.start and id <= seen.end
                # nothing to do!
                return true

        found = false
        for seen in seen_list
            if id + 1 == seen.start
                seen.start = id
                found = true
                break
            else if id - 1 == seen.end
                seen.end = id
                found = true
                break

        if not found
            seen_list.push({ start: id, end: id })

        @jar.put('seen', seen_list)

        $('feeditem'+id)?.addClassName('seen')

        return true

    is_seen: (id) =>

        seen_list = @jar.get('seen')
        if not seen_list
            return false

        for seen in seen_list
            if id >= seen.start and id <= seen.end
                # nothing to do!
                return true

        return false

    display_details: (id, details) =>

        [data, htmldata] = details

        $('waitball' + id).remove()

        $('feeditem' + id).insert new Element('div', {'id': 'details' + id, 'class': 'details'})

        data = data.replace(/\r\n/g, "<br />")
        data = data.replace(/\n/g, "<br />")
        $('details' + id).insert new Element('span', {'class': 'data'}).update(htmldata)

        $('details' + id).observe('click', (event) => Event.stop(event))

        @makevisible(id)

        # mark this as seen in cookies
        @mark_seen(id)

        return

    new_items_callback: (leaks_items) =>

        items = leaks_items.items
        if items.length > 0
            # keep the last item's id
            @next_item_id = items[items.length-1][0]+1
        else if @next_item_id is null
            # list is empty, query ANY item starting with index 0, when it gets added...
            @next_item_id = 0

        if  $('waitball')?
            $('waitball').remove()

        for item in items
            @add_item(item)

        return

    remove: () =>
        # clear out the GUI

        return
