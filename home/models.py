from django.db import models

class Confirm(models.Model):
    username = models.TextField()
    name = models.TextField()
    email = models.TextField()
    password = models.TextField()
    otp = models.TextField()
    attempts = models.IntegerField(default=0)

class Password(models.Model):
    email = models.TextField()
    otp = models.TextField()
    confirmed = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)


class Post(models.Model):
    user_id = models.IntegerField()
    heading = models.TextField()
    caption = models.TextField(null=True, blank=True)
    upload = models.FileField(upload_to ='uploads/')
    created = models.DateTimeField(auto_now_add=True)
    thumbnail = models.TextField(null=True, blank=True)
    category = models.TextField(null=True, blank=True)
    views = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

class Me(models.Model):
    user_id = models.IntegerField()
    username = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    first_name = models.TextField()
    email = models.TextField()
    bio = models.TextField()
    location = models.TextField()
    online = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    current_chat = models.IntegerField(blank=True, null=True)
    ontime = models.DateTimeField(null=True)


class Comment(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

class Bookmark(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

class Post_report(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    context = models.TextField()
    already = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class Comment_report(models.Model):
    user_id = models.IntegerField()
    comment_id = models.IntegerField()
    context = models.TextField()
    already = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)