c.input.forward_unbound_keys = 'all'
c.input.insert_mode.auto_leave = False
c.input.insert_mode.auto_load = True
c.input.insert_mode.plugins = True

c.statusbar.hide = True

c.tabs.last_close = 'ignore'
c.tabs.show = 'switching'

c.url.start_pages = '{{ url }}'
# TODO multiple urls?
config.set('content.javascript.enabled', True, '*://{{ url }}/*')

c.window.title_format = '{title}'
