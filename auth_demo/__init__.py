from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    authn_policy = AuthTktAuthenticationPolicy('auth.secret')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
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
