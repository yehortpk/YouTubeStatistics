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

    videos_count = models.CharField(max_length=255, default='0')
    average_likes = models.PositiveIntegerField(null=True)
    average_dislikes = models.PositiveIntegerField(null=True)
    description = models.TextField()
    published_at = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.CharField(max_length=255, default='0')
    subscribers_count = models.CharField(max_length=255, default='0')
    banner_photo = models.CharField(max_length=255, null=True)

    page = models.ForeignKey('ChannelPage', on_delete=models.CASCADE, related_name='channels_list', null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.views_count = reduce_number(self.views_count)
        self.subscribers_count = reduce_number(self.subscribers_count)

        super().save(*args, **kwargs)


class Page(models.Model):
    current_page_token = models.CharField(max_length=255)
    next_page_token = models.CharField(max_length=255)
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
    likes_count = models.CharField(max_length=255, default='0')
    dislikes_count = models.CharField(max_length=255, default='0')
    views_count = models.CharField(max_length=255, default='0')
    comments_count = models.IntegerField(default=0)
    average_likes = models.IntegerField(default=0)
    average_dislikes = models.IntegerField(default=0)
    published_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='videos_list', null=True)
    page = models.ForeignKey('VideoPage', on_delete=models.CASCADE, related_name='videos_list', null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.likes_count = reduce_number(self.likes_count)
        self.dislikes_count = reduce_number(self.dislikes_count)
        self.views_count = reduce_number(self.views_count)

        super().save(*args, **kwargs)


def reduce_number(num):
    if type(num) == int or type(num) == str and num.isdigit():
        num = int(num)
        if num / 1000000000 >= 1:
            num = str(round(num / 1000000000, 2)) + 'b'
        elif num / 1000000 >= 1:
            num = str(round(num / 1000000, 2)) + 'm'
        elif num / 1000 >= 1:
            num = str(round(num / 1000, 2)) + 'k'
    return num
