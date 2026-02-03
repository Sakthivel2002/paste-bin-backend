from django.db import models

class Paste(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_views = models.IntegerField(null=True, blank=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.id
