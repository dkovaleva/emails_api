from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import EmailUser, EmailObject, Relationship


def str_is_email(text):
    result = False
    try:
        validate_email(text)
        result = True
    except ValidationError:
        pass
    return result

class SendEmailForm(forms.ModelForm):
    From = forms.EmailField(required=True)
    To = forms.CharField(required=True)

    class Meta:
        model = EmailObject
        fields = ['header', 'content']
        hidden_fields = ['sender']

    def clean_To(self):
        receivers_emails = self.cleaned_data['To'].split(',')
        receivers = []
        for email_address in receivers_emails:
            if not str_is_email(email_address):
                raise ValidationError('Enter valid list of email addresses, separated by comma', code='invalid')
        return self.cleaned_data['To']

    def save(self, *args, **kwargs):
        sender, created = EmailUser.objects.get_or_create(email_address=self.cleaned_data['From'])
        self.instance.sender = sender
        super(SendEmailForm, self).save(*args, **kwargs)
        if kwargs.get('commit'):
            new_relationships = []
            for receiver_email in self.cleaned_data['To'].split(','):
                receiver, created = EmailUser.objects.get_or_create(email_address=receiver_email)
                new_relationships.append(Relationship(email=self.instance, receiver=receiver))
            Relationship.objects.bulk_create(new_relationships)