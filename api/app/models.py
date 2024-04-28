from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, email=None, **extra_fields):
        if email:
            email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, password, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is False:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is False:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, password, email, **extra_fields)
    

class User(AbstractUser):
    '''
    one-to-many relationship between User and InstantMessage
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, 
                        editable=False)
    email = models.EmailField(blank=True, null=True)
    username = models.CharField(max_length=35, unique=True, 
                                blank=True, null=True)
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        db_table = 'user'
        verbose_name = 'user'
        verbose_name_plural = 'users'
        
    def clean(self) -> None:
        if not self.username:
            raise ValidationError(
                "Username field can't be blank."
            )
        if self.email and User.objects.filter(
            email=self.email).exclude(id=self.id).exists():
            raise ValidationError(
                "User with this email already exists."
            )
        return super().clean()

    def __str__(self):
        if self.email:
            return self.email
        return self.username if self.username else ''

class Chat(models.Model):
    '''
    one-to-many relationship between Chat and Message
    '''
    pass

class InstantMessage(models.Model):
    text = models.TextField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class UserToChat(models.Model):
    '''
    join table to implement many-to-many relationship between User and Chat
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
