import json

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ALL_PERMISSIONS, Allow, Authenticated
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    User,
    )

### MAP GROUPS TO PERMISSIONS
class Root(object):
    __acl__ = [
        (Allow, Authenticated, 'create'),
        (Allow, 'g:editors', 'edit'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

def groupfinder(userid, request):
    user=DBSession.query(User).filter(User.login==userid).first()
    if user:
        return ['g:%s' % g for g in json.loads(user.groups)]

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    authn_policy = AuthTktAuthenticationPolicy('auth.secret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        root_factory=Root,
    )
    config.include('pyramid_mako')

    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('users', '/users')
    config.add_route('user', '/user/{login}')

    config.add_route('pages', '/pages')
    config.add_route('create_page', '/create_page')
    config.add_route('page', '/page/{title}')
    config.add_route('edit_page', '/page/{title}/edit')
    config.scan()

    return config.make_wsgi_app()
