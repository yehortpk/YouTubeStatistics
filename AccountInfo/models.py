from django.db import models

class Account(models.Model):
    account_id = models.CharField(max_length=255)
    channel = models.OneToOneField('Channel', on_delete=models.CASCADE, null=True)    

    def __str__(self):
        return self.channel.title    

class Channel(models.Model):
    acc = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='subscriptions', null=True) 
    title = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    channel_url = models.CharField(max_length=255)
    photo = models.TextField()

    videos_count = models.IntegerField(default=0)
    average_likes = models.PositiveIntegerField(null=True)
    average_dislikes = models.PositiveIntegerField(null=True)
    description = models.TextField()
    published_at = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(null=True)
    subscribers_count = models.IntegerField(null=True)
    banner_photo = models.CharField(max_length=255, null=True)

    page = models.ForeignKey('ChannelPage', on_delete=models.CASCADE, related_name='channels_list', null=True)  

    def __str__(self):
        return self.title

class Page(models.Model):
    current_page_token = models.CharField(max_length=15)
    next_page_token = models.CharField(max_length=15)
    size = models.IntegerField(default=5)

    def __str__(self):
        return self.current_page_token

class VideoPage(Page):
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='pages_list', null=True)

class ChannelPage(Page):
    account = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='pages_list', null=True)

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=255)
    photo = models.TextField()
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    average_likes = models.PositiveIntegerField(default=0)
    average_dislikes = models.PositiveIntegerField(default=0)
    published_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='videos_list', null=True)
    page = models.ForeignKey('VideoPage', on_delete=models.CASCADE, related_name='videos_list', null=True)

    def __str__(self):
        return self.title