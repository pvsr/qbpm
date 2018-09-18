c.input.forward_unbound_keys = 'all'
c.input.insert_mode.auto_leave = False
c.input.insert_mode.auto_load = True
c.input.insert_mode.plugins = True

c.statusbar.hide = True

c.tabs.last_close = 'ignore'
c.tabs.show = 'switching'

c.url.start_pages = '{{url}}'
# TODO load whitelist from separate file
config.set('content.javascript.enabled', True, '*://{{url}}/*')

# single brackets are qutebrowser's interpolation, not jinja's
c.window.title_format = '{title}'
# TODO c.window.title_format = '{{name}}'?
