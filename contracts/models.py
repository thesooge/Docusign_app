from django.db import models

class Contract(models.Model):
    user_name = models.CharField(max_length=255)
    recipient_name = models.CharField(max_length=255)
    recipient_email = models.EmailField()
    document_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # DocuSign Envelope ID
    is_signed = models.BooleanField(default=False)  # track signing status
    contract_file = models.FileField(upload_to="contracts/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"Contract: {self.user_name} ↔️ {self.recipient_name} - Signed: {self.is_signed}"