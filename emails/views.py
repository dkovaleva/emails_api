import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist


from .models import EmailObject, EmailUser, Relationship
from .forms import SendEmailForm

def as_json(fn):
    def wrapped(*args, **kwargs):
        result = fn(*args, **kwargs)
        return HttpResponse(json.dumps(result), content_type='application/json')
    return wrapped


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_POST, name='dispatch')
class SendEmailView(View):
    form_class = SendEmailForm
    data = {}

    @as_json
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(commit=True)
            self.data = {
                'result': 'OK',
                'msg': 'Successfully create email'
            }
        else:
            self.data = {
                'result': 'Fail',
                'msg': 'Please, enter valid data',
                'description': str(form.errors.as_data())
            }
        return self.data


@method_decorator(require_GET, name='dispatch')
class SentBoxView(View):
    user = None
    data = None

    @staticmethod
    def get_item_dict(item):
        return {
            'id': item['pk'],
            'header': item['header'],
        }

    @as_json
    def get(self, request, *args, **kwargs):
        self.user = get_object_or_404(EmailUser, email_address=request.GET.get('email_address'))
        values = self.user.sent_objects().values('pk', 'header', )
        self.data = [self.get_item_dict(item) for item in values]
        return self.data


@method_decorator(require_GET, name='dispatch')
class InboxView(View):
    user = None
    data = None

    @staticmethod
    def get_item_dict(item):
        return {
            'id': item['email__pk'],
            'header': item['email__header'],
            'from': item['email__sender__email_address'],
            'is_read': item['is_read']
        }

    @as_json
    def get(self, request, *args, **kwargs):
        self.user = get_object_or_404(EmailUser, email_address=request.GET.get('email_address'))
        values = self.user.inbox().values('email__pk', 'email__header', 'is_read', 'email__sender__email_address')
        self.data = [self.get_item_dict(item) for item in values]
        return self.data


@method_decorator(require_GET, name='dispatch')
class EmailDetailView(View):
    instance = None
    data = {}

    @as_json
    def get(self, request, email_id):
        self.instance = get_object_or_404(EmailObject, pk=email_id)
        self.data = {
            'id': self.instance.pk,
            'header': self.instance.header,
            'content': self.instance.content,
            'from': self.instance.sender.email_address,
            'to': self.instance.receivers_list()
        }
        return self.data



@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_POST, name='dispatch')
class MarkIfIsReadView(View):
    instance = None
    email_address = None
    email_id = None
    is_read = None
    data = {}

    def get_ok_result(self):
        return {
            'result': 'OK',
            'msg': 'Email with id %s marked as %s' % (self.email_id, "unread" if self.is_read == '0' else "read")
        }

    @staticmethod
    def get_fail_result(msg):
        return {
            'result': 'Fail',
            'msg': 'Error',
            'description' : msg
        }

    @as_json
    def post(self, request, email_id):
        self.email_id = email_id
        self.email_address = request.POST.get('email_address')
        self.is_read = request.POST.get('is_read')
        if not self.is_read in ['1', '0']:
            self.data = self.get_fail_result('is_read parameter is required and must be 0 or 1')
        else:
            try:
                relationship = Relationship.objects.select_related('receiver').get(email=self.email_id, receiver__email_address=self.email_address)
                relationship.is_read = self.is_read == '1'
                relationship.save()
                self.data = self.get_ok_result()
            except ObjectDoesNotExist:
                self.data = self.get_fail_result('Email with id %s is not in %s inbox list' % (self.email_id, self.email_address))
            except:
                self.data = self.get_fail_result('Something went wrong. Please, contant administrator.')
        return self.data


@require_POST
@as_json
def remove_email(request, email_id):
    email_address = request.POST.get('email_address')
    try:
        relationship = Relationship.objects.select_related('receiver').get(email=email_id, receiver__email_address=email_address)
        relationship.delete()
        data = {
            'result': 'OK',
            'msg': 'Email is deleted from inbox list for user %s' % email_address
        }
    except ObjectDoesNotExist:
        data = {
            'result': 'Fail',
            'msg': 'Error',
            'description': 'Email with id %s is not in user %s inbox list' % (email_id, email_address)
        }
    except:
        data = {
            'result': 'Fail',
            'msg': 'Something went wrong. Please, contant administrator.'
        }
    return data






