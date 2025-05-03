from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] 

    def __str__(self):
        return f'Post by {self.user} at {self.created_at.strftime('%d-%Y-%m %H:%M')}' # UK date format

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followee")

    def __str__(self):
        return f'{self.follower} follows {self.followee}'

class Like(models.Model):
    user_liking = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_liking")
    post_liked = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_liked")
    
    def __str__(self):
        return f'{self.user_liking} likes {self.post_liked}'

