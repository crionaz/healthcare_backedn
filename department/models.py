from django.db import models
from django.core.exceptions import ValidationError

class Department(models.Model):
    """
    Model for departments within the organization
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Custom validation to ensure department name is unique and not empty.
        """
        if not self.name:
            raise ValidationError({'name': 'Department name cannot be empty.'})
        if Department.objects.filter(name=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': 'Department name must be unique.'})
        
    def save(self, *args, **kwargs):
        """
        Override save method to ensure clean validation is called.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']

    def __str__(self):
        return self.name