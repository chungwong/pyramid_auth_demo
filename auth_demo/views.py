import urllib
from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid, forget, remember

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    User,
    Page,
    )

def websafe_uri(txt):
    uri = txt.replace(' ', '-')
    return urllib.quote(uri)

### DEFINE VIEWS
@forbidden_view_config()
def forbidden_view(request):
    # do not allow a user to login if they are already logged in
    if authenticated_userid(request):
        return HTTPForbidden()

    loc = request.route_url('login', _query=(('next', request.path),))
    return HTTPFound(location=loc)

@view_config(
    route_name='home',
    renderer='home.mako',
)
def home_view(request):
    login = authenticated_userid(request)
    user = DBSession.query(User).filter(User.login==login).first()

    return {
        'user': user,
        'user_pages': DBSession.query(Page).filter(Page.owner == login).all(),
    }

@view_config(
    route_name='login',
    renderer='login.mako',
)
def login_view(request):
    next = request.params.get('next') or request.route_url('home')
    login = ''
    did_fail = False
    if 'submit' in request.POST:
        login = request.POST.get('login', '')
        passwd = request.POST.get('passwd', '')

        user = DBSession.query(User).filter(User.login==login).first()
        if user and user.check_password(passwd):
            headers = remember(request, login)
            return HTTPFound(location=next, headers=headers)
        did_fail = True

    return {
        'login': login,
        'next': next,
        'failed_attempt': did_fail,
        'users': DBSession.query(User).all(),
    }

@view_config(
    route_name='logout',
)
def logout_view(request):
    headers = forget(request)
    loc = request.route_url('home')
    return HTTPFound(location=loc, headers=headers)

@view_config(
    route_name='users',
    renderer='users.mako',
)
def users_view(request):
    return {
        'users': DBSession.query(User).all(),
    }

@view_config(
    route_name='user',
    renderer='user.mako',
)
def user_view(request):
    login = request.matchdict['login']
    user = DBSession.query(User).filter(User.login==login).first()
    if not user:
        raise HTTPNotFound()

    pages = DBSession.query(Page).filter(Page.owner == login)

    return {
        'user': user,
        'pages': pages,
    }

@view_config(
    route_name='pages',
    renderer='pages.mako',
)
def pages_view(request):
    return {
        'pages': DBSession.query(Page).all(),
    }

@view_config(
    route_name='page',
    renderer='page.mako',
)
def page_view(request):
    uri = request.matchdict['title']
    page = DBSession.query(Page).filter(Page.uri==uri).first()
    if not page:
        raise HTTPNotFound()

    return {
        'page': page,
    }

def validate_page(title, body):
    errors = []

    title = title.strip()
    if not title:
        errors.append('Title may not be empty')
    elif len(title) > 32:
        errors.append('Title may not be longer than 32 characters')

    body = body.strip()
    if not body:
        errors.append('Body may not be empty')

    return {
        'title': title,
        'body': body,
        'errors': errors,
    }

@view_config(
    route_name='create_page',
    renderer='edit_page.mako',
)
def create_page_view(request):
    owner = authenticated_userid(request)
    if owner is None:
        raise HTTPForbidden()

    errors = []
    body = title = ''
    if request.method == 'POST':
        title = request.POST.get('title', '')
        body = request.POST.get('body', '')

        v = validate_page(title, body)
        title = v['title']
        body = v['body']
        errors += v['errors']

        if not errors:
            page = Page(title=title, owner=owner, body=body, uri=websafe_uri(title))
            DBSession.add(page)
            url = request.route_url('page', title=page.uri)
            return HTTPFound(location=url)

    return {
        'title': title,
        'owner': owner,
        'body': body,
        'errors': errors,
    }

@view_config(
    route_name='edit_page',
    renderer='edit_page.mako',
)
def edit_page_view(request):
    uri = request.matchdict['title']
    page = DBSession.query(Page).filter(Page.uri==uri).first()
    if not page:
        raise HTTPNotFound()

    errors = []
    if request.method == 'POST':
        title = request.POST.get('title', '')
        body = request.POST.get('body', '')

        v = validate_page(title, body)
        title = v['title']
        body = v['body']
        errors += v['errors']

        if not errors:
            page.title=v['title']
            page.body=v['body']
            page.uri=websafe_uri(page.title)
            url = request.route_url('page', title=page.uri)
            return HTTPFound(location=url)

    return {
        'title': page.title,
        'owner': page.owner,
        'body': page.body,
        'errors': errors,
    }
