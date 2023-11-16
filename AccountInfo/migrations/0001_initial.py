# Generated by Django 3.0.1 on 2023-11-16 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('channel_id', models.CharField(max_length=255)),
                ('channel_url', models.CharField(max_length=255)),
                ('photo', models.TextField()),
                ('videos_count', models.CharField(default='0', max_length=255)),
                ('average_likes', models.PositiveIntegerField(null=True)),
                ('average_dislikes', models.PositiveIntegerField(null=True)),
                ('description', models.TextField()),
                ('published_at', models.DateField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('views_count', models.CharField(default='0', max_length=255)),
                ('subscribers_count', models.CharField(default='0', max_length=255)),
                ('banner_photo', models.CharField(max_length=255, null=True)),
                ('acc', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='AccountInfo.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_page_token', models.CharField(max_length=15)),
                ('next_page_token', models.CharField(max_length=15)),
                ('size', models.IntegerField(default=5)),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='channel',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='AccountInfo.Channel'),
        ),
        migrations.CreateModel(
            name='VideoPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='AccountInfo.Page')),
                ('channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pages_list', to='AccountInfo.Channel')),
            ],
            bases=('AccountInfo.page',),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('video_id', models.CharField(max_length=255)),
                ('photo', models.TextField()),
                ('likes_count', models.CharField(default='0', max_length=255)),
                ('dislikes_count', models.CharField(default='0', max_length=255)),
                ('views_count', models.CharField(default='0', max_length=255)),
                ('comments_count', models.IntegerField(default=0)),
                ('average_likes', models.IntegerField(default=0)),
                ('average_dislikes', models.IntegerField(default=0)),
                ('published_at', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos_list', to='AccountInfo.Channel')),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos_list', to='AccountInfo.VideoPage')),
            ],
        ),
        migrations.CreateModel(
            name='ChannelPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='AccountInfo.Page')),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pages_list', to='AccountInfo.Account')),
            ],
            bases=('AccountInfo.page',),
        ),
        migrations.AddField(
            model_name='channel',
            name='page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channels_list', to='AccountInfo.ChannelPage'),
        ),
    ]
