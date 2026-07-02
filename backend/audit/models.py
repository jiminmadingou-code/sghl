from django.db import models
from django.conf import settings
import json
import hashlib


class AuditTrail(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'CREATE'),
        ('UPDATE', 'UPDATE'),
        ('DELETE', 'DELETE'),
        ('VIEW', 'VIEW'),
        ('VALIDATE', 'VALIDATE'),
        ('EXPORT', 'EXPORT'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(null=True, blank=True)
    user_email = models.CharField(max_length=255, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    old_value = models.JSONField(default=dict, blank=True)
    new_value = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user_id', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.model_name} #{self.object_id} at {self.timestamp}"

    def save(self, *args, **kwargs):
        """Empêcher la modification des logs d'audit."""
        if self.pk:
            raise NotImplementedError("Les logs d'audit sont immuables et ne peuvent pas être modifiés.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Empêcher la suppression des logs d'audit."""
        raise NotImplementedError("Les logs d'audit sont immuables et ne peuvent pas être supprimés.")

    @classmethod
    def log(cls, request, action_type, model_name, object_id, old_value=None, new_value=None, details=None):
        """Create an audit log entry."""
        ip_address = cls._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500] if request else ''
        
        return cls.objects.create(
            user_id=getattr(request, 'user_id', None),
            user_email=getattr(request, 'user_email', None),
            action_type=action_type,
            model_name=model_name,
            object_id=object_id,
            old_value=old_value or {},
            new_value=new_value or {},
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
        )

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        if not request:
            return None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
