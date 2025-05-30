from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Role(models.Model):
    """
    Model for defining roles within the staff management system
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Custom validation to ensure role name is unique and not empty.
        """
        if not self.name:
            raise ValidationError({'name': 'Role name cannot be empty.'})
        if Role.objects.filter(name=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': 'Role name must be unique.'})
        
    def save(self, *args, **kwargs):
        """
        Override save method to ensure clean validation is called.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['name']

    def __str__(self):
        return self.name
