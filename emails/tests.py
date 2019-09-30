from django.test import TestCase
from django.urls import reverse

from .models import EmailUser, EmailObject, Relationship
from .forms import SendEmailForm

class SendEmailFormTestClass(TestCase):

    def test_receivers_is_empty(self):
        data = {'To': ''}
        form = SendEmailForm(data)
        self.assertFalse(form.is_valid())


    def test_receivers_is_invalid(self):
        data = {'To': 'test@mail.ru,12344,test2@gmail.com'}
        form = SendEmailForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('To'), ['Enter valid list of email addresses, separated by comma'])

    def test_receivers_is_ok(self):
        data = {'To': 'test1@mail.ru,test2@gmail.com,test3@list.ru'}
        form = SendEmailForm(data)
        self.assertTrue(form.is_valid)

    def test_single_receiver(self):
        data = {'To': 'test1@mail.ru'}
        form = SendEmailForm(data)
        self.assertTrue(form.is_valid)

class SendEmailViewTestClass(TestCase):
    url = reverse('emails:send_email')

    def test_remove_email(self):
        post_data = {
            'header': 'test',
            'content': 'test',
            'From': 'sender@mail.ru',
            'To': 'receiver1@mail.ru,receiver2@mail.ru'
        }
        r = self.client.post(self.url, data=post_data)
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'OK')
        self.assertEqual(EmailUser.objects.filter(email_address='sender@mail.ru').count(), 1)
        self.assertEqual(EmailUser.objects.filter(email_address='receiver1@mail.ru').count(), 1)
        self.assertEqual(EmailUser.objects.filter(email_address='receiver2@mail.ru').count(), 1)
        self.assertEqual(EmailObject.objects.count(), 1)
        self.assertEqual(Relationship.objects.count(), 2)

    def test_remove_email_bad_data1(self):
        post_data = {
            'header': 'test',
            'content': 'test',
            'From': 'sender@mail.ru',
            'To': 'test'
        }
        r = self.client.post(self.url, data=post_data)
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'Fail')
        self.assertEqual(EmailUser.objects.count(), 0)
        self.assertEqual(EmailObject.objects.count(), 0)
        self.assertEqual(Relationship.objects.count(), 0)


    def test_remove_email_bad_data2(self):
        post_data = {
            'header': 'test',
            'content': 'test',
            'From': 'sender@mail.ru',
            'To': ''
        }
        r = self.client.post(self.url, data=post_data)
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'Fail')
        self.assertEqual(EmailUser.objects.count(), 0)
        self.assertEqual(EmailObject.objects.count(), 0)
        self.assertEqual(Relationship.objects.count(), 0)

    def test_remove_email_bad_data3(self):
        post_data = {
            'header': 'test',
            'content': 'test',
            'From': 'test',
            'To': 'receiver@mail.ru'
        }
        r = self.client.post(self.url, data=post_data)
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'Fail')
        self.assertEqual(EmailUser.objects.count(), 0)
        self.assertEqual(EmailObject.objects.count(), 0)
        self.assertEqual(Relationship.objects.count(), 0)

    def test_remove_email_bad_data4(self):
        post_data = {
            'header': 'test',
            'content': 'test',
            'From': '',
            'To': 'receiver@mail.ru'
        }
        r = self.client.post(self.url, data=post_data)
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'Fail')
        self.assertEqual(EmailUser.objects.count(), 0)
        self.assertEqual(EmailObject.objects.count(), 0)
        self.assertEqual(Relationship.objects.count(), 0)



class SentBoxViewTestClass(TestCase):

    url = reverse('emails:sentbox')

    @classmethod
    def setUpTestData(cls):
        user = EmailUser.objects.create(email_address='sender@mail.ru')
        user2 = EmailUser.objects.create(email_address='inactive@mail.ru')
        for i in range(5):
            header = 'header_%s' % i
            content = 'content_%s' % i
            EmailObject.objects.create(header=header, content=content, sender=user)

    def test_view_sentbox_not_empty(self):
        r = self.client.get(self.url, data={'email_address': 'sender@mail.ru'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(len(json_data), 5)

    def test_view_sentbox_empty(self):
        r = self.client.get(self.url, data={'email_address': 'inactive@mail.ru'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(len(json_data), 0)

    def test_view_sentbox_not_exist(self):
        r = self.client.get(self.url, data={'email_address': 'not_exist@mail.ru'})
        self.assertEqual(r.status_code, 404)


class InboxBoxViewTestClass(TestCase):
    url = reverse('emails:inbox')

    @classmethod
    def setUpTestData(cls):
        senders = []
        email_objects = []
        receiver1 = EmailUser.objects.create(email_address='receiver1@mail.ru')#receive 5 emails
        receiver2 = EmailUser.objects.create(email_address='receiver2@mail.ru')#receive 1 email
        receiver3 = EmailUser.objects.create(email_address='receiver_empty_list@mail.ru')# receive 0 emails
        for i in range (5):
            user = EmailUser.objects.create(email_address='sender%s@mail.ru' % i)
            email_object = EmailObject.objects.create(header='test', content='test', sender=user)
            relationship = Relationship.objects.create(email=email_object, receiver=receiver1)
        Relationship.objects.create(email=email_object, receiver=receiver2)

    def test_view_inbox_5_emails(self):
        r = self.client.get(self.url, data={'email_address': 'receiver1@mail.ru'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(len(json_data), 5)

    def test_view_inbox_1_email(self):
        r = self.client.get(self.url, data={'email_address': 'receiver2@mail.ru'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(len(json_data), 1)

    def test_view_inbox_empty(self):
        r = self.client.get(self.url, data={'email_address': 'receiver_empty_list@mail.ru'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(len(json_data), 0)

    def test_view_sentbox_not_exist(self):
        r = self.client.get(self.url, data={'email_address': 'not_exist@mail.ru'})
        self.assertEqual(r.status_code, 404)


class EmailDetailViewTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        sender = EmailUser.objects.create(email_address='sender@mail.ru')
        receiver = EmailUser.objects.create(email_address='receiver@mail.ru')
        email = EmailObject.objects.create(header='test', content='test', sender=sender)
        Relationship.objects.create(email=email, receiver=receiver)

    def test_view_email_details(self):
        email = EmailObject.objects.all()[0]
        url = reverse('emails:email_detail', args=[email.pk])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['id'], email.pk)
        self.assertEqual(json_data['header'], email.header)
        self.assertEqual(json_data['content'], email.content)
        self.assertEqual(json_data['from'], email.sender.email_address)
        self.assertEqual(json_data['to'], email.receivers_list())

    def test_view_email_not_exist(self):
        url = reverse('emails:email_detail', args=[100])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 404)


class MarkIfIsReadViewTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        sender = EmailUser.objects.create(email_address='sender@mail.ru')
        receiver = EmailUser.objects.create(email_address='receiver@mail.ru')
        receiver2 = EmailUser.objects.create(email_address='receiver2@mail.ru')
        email = EmailObject.objects.create(header='test', content='test', sender=sender)
        Relationship.objects.create(email=email, receiver=receiver)

    def test_mark_as_read(self):
        email = EmailObject.objects.all()[0]
        receiver = EmailUser.objects.get(email_address='receiver@mail.ru')
        self.assertFalse(email.is_read_by_user(receiver))
        url = reverse('emails:mark_if_is_read', args=[email.pk])
        r = self.client.post(url, data={'email_address': receiver.email_address, 'is_read': '1'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'OK')
        self.assertTrue(email.is_read_by_user(receiver))

    def test_mark_as_unread(self):
        email = EmailObject.objects.all()[0]
        receiver = EmailUser.objects.get(email_address='receiver@mail.ru')
        relationship = Relationship.objects.get(email=email, receiver=receiver)
        relationship.is_read = True
        relationship.save()
        self.assertTrue(email.is_read_by_user(receiver))
        url = reverse('emails:mark_if_is_read', args=[email.pk])
        r = self.client.post(url, data={'email_address': receiver.email_address, 'is_read': '0'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'OK')
        self.assertFalse(email.is_read_by_user(receiver))

    def test_mark_as_read_fail(self):
        email = EmailObject.objects.all()[0]
        receiver = EmailUser.objects.get(email_address='receiver@mail.ru')
        self.assertFalse(email.is_read_by_user(receiver))
        url = reverse('emails:mark_if_is_read', args=[email.pk])
        r = self.client.post(url, data={'email_address': receiver.email_address, 'is_read': 'xxx'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'Fail')
        self.assertFalse(email.is_read_by_user(receiver))

    def test_mark_as_read_fail_bad_parameter(self):
        email = EmailObject.objects.all()[0]
        receiver = EmailUser.objects.get(email_address='receiver@mail.ru')
        self.assertFalse(email.is_read_by_user(receiver))
        url = reverse('emails:mark_if_is_read', args=[email.pk])
        r = self.client.post(url, data={'email_address': receiver.email_address, 'is_read': 'xxx'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'Fail')
        self.assertEqual(json_data['description'], 'is_read parameter is required and must be 0 or 1')

    def test_mark_as_read_fail_bad_email_address(self):
        email = EmailObject.objects.all()[0]
        receiver = EmailUser.objects.get(email_address='receiver2@mail.ru')
        self.assertFalse(email.is_read_by_user(receiver))
        url = reverse('emails:mark_if_is_read', args=[email.pk])
        r = self.client.post(url, data={'email_address': receiver.email_address, 'is_read': '1'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'Fail')
        wait_for_msg = 'Email with id %s is not in %s inbox list' % (email.id, receiver.email_address)
        self.assertEqual(json_data['description'], wait_for_msg)

    def test_mark_as_read_fail_not_exist(self):
        receiver = EmailUser.objects.get(email_address='receiver2@mail.ru')
        url = reverse('emails:mark_if_is_read', args=[100])
        r = self.client.post(url, data={'email_address': receiver.email_address, 'is_read': '1'})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'Fail')
        wait_for_msg = 'Email with id %s is not in %s inbox list' % (100, receiver.email_address)
        self.assertEqual(json_data['description'], wait_for_msg)

class RemoveEmailTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        sender = EmailUser.objects.create(email_address='sender@mail.ru')
        receiver = EmailUser.objects.create(email_address='receiver@mail.ru')
        receiver2 = EmailUser.objects.create(email_address='receiver2@mail.ru')
        email = EmailObject.objects.create(header='test', content='test', sender=sender)
        Relationship.objects.create(email=email, receiver=receiver)

    def test_remove_email(self):
        email = EmailObject.objects.all()[0]
        receiver = EmailUser.objects.get(email_address='receiver@mail.ru')
        self.assertTrue(receiver.email_address in email.receivers_list())
        url = reverse('emails:remove_email', args=[email.pk])
        r = self.client.post(url, data={'email_address': receiver.email_address})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'OK')
        wait_for_msg = 'Email is deleted from inbox list for user %s' % receiver.email_address
        self.assertEqual(json_data['msg'], wait_for_msg)
        self.assertFalse(receiver.email_address in email.receivers_list())

    def test_remove_email_bad_email_address(self):
        email = EmailObject.objects.all()[0]
        receiver = EmailUser.objects.get(email_address='receiver2@mail.ru')
        self.assertFalse(receiver.email_address in email.receivers_list())
        url = reverse('emails:remove_email', args=[email.pk])
        r = self.client.post(url, data={'email_address': receiver.email_address})
        self.assertEqual(r.status_code, 200)
        json_data = r.json()
        self.assertEqual(json_data['result'], 'Fail')
        wait_for_msg = 'Email with id %s is not in user %s inbox list' % (email.pk, receiver.email_address)
        self.assertEqual(json_data['description'], wait_for_msg)
        self.assertFalse(receiver.email_address in email.receivers_list())