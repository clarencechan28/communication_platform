from django.db import models

# Create your models here.
class Search(models.Model):
    keyword = models.CharField(max_length = 200)
    start_date = models.DateField('Start date')
    end_date = models.DateField('End date')

class Email(models.Model):
    body = models.TextField()
    subject = models.TextField()
    sender = models.TextField()
    recipient = models.TextField()
    cc = models.TextField()
    date = models.DateTimeField()
    
    def __str__(self):
        return self.subject