import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Base,
    User,
    Page,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        _make_demo_user('luser')
        _make_demo_user('editor', groups=['editors'])
        _make_demo_user('admin', groups=['admin'])
        
        _make_demo_page('hello', owner='luser', body='''<h3>Hello World!</h3><p>I'm the body text</p>''')

def _make_demo_user(login, **kw):
    kw.setdefault('password', login)
    user = User(login, **kw)
    DBSession.add(user)


def _make_demo_page(title, **kw):
    from ..views import websafe_uri
    uri = kw.setdefault('uri', websafe_uri(title))
    page = Page(title, **kw)
    DBSession.add(page)

