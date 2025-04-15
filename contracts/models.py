from django.db import models
from django.contrib.auth import get_user_model

class Contract(models.Model):
    user_name = models.CharField(max_length=255)
    recipient_name = models.CharField(max_length=255)
    recipient_email = models.EmailField()
    contract_file = models.FilePathField(path='media/')
    document_id = models.CharField(max_length=255, null=True, blank=True)
    is_signed = models.BooleanField(default=False)

class DocusignProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    account_id = models.CharField(max_length=255)
    token_expiry = models.DateTimeField()
    base_uri = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username