from django.db import models
from . import constants
from django.contrib.auth.models import Group


class Notifications(models.Model):
    title = models.CharField(max_length=150)
    info = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("coreapp.user", on_delete=models.SET_NULL,null=True, blank=True)
    class Meta:
        ordering = ('-created_at',)
    
    @property
    def creator_image(self):
        if self.created_by is None:
            return ""
        return self.created_by.image.url if self.created_by.image else None
        
    def __str__(self):
        return f"{self.title} | {self.info[:50]}..."
    


    def save(self, *args, **kwargs):
        if not self.id:
            from utility.utils import notification_utils
            notification_utils.update_dashboard_notification("notification",1,True)
        return super(Notifications, self).save(*args, **kwargs)


    
class GroupTime(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):

        return self.group.name