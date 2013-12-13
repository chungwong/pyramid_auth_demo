<%inherit file='base.mako' />

<p><a href="${ request.route_url('home') }">Home</a></p>

<h1>All Users</h1>
% for user in users:
<p><a href="${ request.route_url('user', login=user.login) }">${ user.login }</a></p>
% endfor
