import json

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ALL_PERMISSIONS, Allow, Authenticated, Everyone
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    User,
    Page,
    )

### MAP GROUPS TO PERMISSIONS
class RootFactory(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

class UserFactory(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        user = DBSession.query(User).filter(User.login==key).first()
        user.__parent__ = self
        user.__name__ = key
        return user

class PageFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'create'),
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        page = DBSession.query(Page).filter(Page.title==key).first()
        page.__parent__ = self
        page.__name__ = key
        return page

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
        root_factory=RootFactory,
    )
    config.include('pyramid_mako')

    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('users', '/users', factory=UserFactory)
    config.add_route('user', '/user/{login}', factory=UserFactory,
                     traverse='/{login}')

    config.add_route('pages', '/pages', factory=PageFactory)
    config.add_route('create_page', '/create_page', factory=PageFactory)
    config.add_route('page', '/page/{title}', factory=PageFactory,
                     traverse='/{title}')
    config.add_route('edit_page', '/page/{title}/edit', factory=PageFactory,
                     traverse='/{title}')
    config.scan()

    return config.make_wsgi_app()
