from django.urls import re_path
import emails.views as views

app_name = 'emails'

urlpatterns = [
    #re_path(r'^index/?$', views.MainPageView.as_view(), name="main_page"),
    re_path(r'^send_email/?$', views.SendEmailView.as_view(), name="send_email"),
    re_path(r'^sentbox/?$', views.SentBoxView.as_view(), name="sentbox"),
    re_path(r'^inbox/?$', views.InboxView.as_view(), name="inbox"),
    re_path(r'^detail/(?P<email_id>\d+)/?$', views.EmailDetailView.as_view(), name="email_detail"),
    re_path(r'^mark_email/(?P<email_id>\d+)/?$', views.MarkIfIsReadView.as_view(), name="mark_if_is_read"),
    re_path(r'^remove/(?P<email_id>\d+)/?$', views.remove_email, name="remove_email"),
]
