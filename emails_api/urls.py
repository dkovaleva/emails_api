from django.conf.urls import url, include

urlpatterns = [
    url(r'^emails/', include('emails.urls', namespace='emails')),
]
