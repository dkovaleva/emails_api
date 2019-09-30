from django.db import models

from django.core.exceptions import ObjectDoesNotExist


class EmailUser(models.Model):
    email_address = models.EmailField(null=False, blank=False, unique=True)

    def __str__(self):
        return self.email_address

    def sent_objects(self):
        return self.author.all()

    def inbox(self):
        return Relationship.objects.select_related('email', 'email__sender').filter(receiver=self.pk)


class EmailObject(models.Model):
    header = models.CharField(null=False, blank=True, max_length=255)
    content = models.TextField(null=False, blank=True)
    sender = models.ForeignKey(EmailUser, related_name='author', on_delete=models.PROTECT)

    def receivers_list(self):
        return list(self.relationship_set.prefetch_related('receiver').values_list('receiver__email_address', flat=True))

    def get_relationship(self, user):
        return Relationship.objects.get(email=self, receiver=user)

    def is_read_by_user(self, user):
        try:
            relationship  = self.get_relationship(user)
            result = relationship.is_read
        except ObjectDoesNotExist:
            result = False
        return result

    def mark_as_read_by_user(self, user):
        relationship  = self.get_relationship(user)
        relationship.is_read = True
        relationship.save()

    def mark_as_unread_by_user(self, user):
        relationship  = self.get_relationship(user)
        relationship.is_read = False
        relationship.save()

    def delete_from_user_inbox(self, user):
        relationship = self.get_relationship(user)
        relationsip.delete()


class Relationship(models.Model):
    email = models.ForeignKey(EmailObject, on_delete=models.PROTECT)
    receiver = models.ForeignKey(EmailUser, on_delete=models.PROTECT)
    is_read = models.BooleanField(default=False)

