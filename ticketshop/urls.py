from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.decorators.csrf import csrf_exempt

from registration.backends.simple.views import RegistrationView

from .views import ConfirmView, HomeView, OrderBarCodeView, OrderDetailView, OrderPdfView, TermsView, WebhookView

urlpatterns = patterns(
    '',
    # url(r'^$', 'ticketshop.views.home', name='home'),
    # url(r'^ticketshop/', include('ticketshop.foo.urls')),

    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^confirm/$', ConfirmView.as_view(), name='confirm'),
    url(r'^order/(?P<pk>\d+)/$', OrderDetailView.as_view(), name='order_detail'),
    url(r'^order/(?P<pk>\d+)/barcode/$', OrderBarCodeView.as_view(), name='order_barcode'),
    url(r'^order/(?P<pk>\d+)/pdf/$', OrderPdfView.as_view(), name='order_pdf'),
    url(r'^terms/$', TermsView.as_view(), name='terms'),
    url(r'^webhook/$', csrf_exempt(WebhookView.as_view()), name='webhook'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password_reset_done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
    url(r'^register/$', RegistrationView.as_view(), name='registration_register'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            }),
    )

urlpatterns += staticfiles_urlpatterns()
