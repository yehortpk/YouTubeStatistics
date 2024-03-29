from django.urls import path

from .views import *

urlpatterns = [
    path('', AccountDetail.as_view(), name = 'index_url'),
    path('channel_id/<channel_id>', ChannelDetail.as_view(), name = 'channel_info_url'),
    path('create_videos_page/<channel_id>/<page_token>', create_videos_page),
    path('update_videos_page/<channel_id>/<page_token>', update_videos_page),
    path('create_channels_page/<page_token>', create_channels_page),
    path('update_channels_page/<page_token>', update_channels_page),
    path('log_in/', AccountDetail.log_in, name = 'log_in_url'),
    path('log_out/', AccountDetail.log_out, name = 'log_out_url'),
    path('google34ecf22213c98a0d.html', confirm_html, name='confirm_html_url'),
    path('token/', get_token, name='get_token'),
    path('find_channel/', find_channel, name='find_channel_url'),
    path('update_videos_list/<channel_id>/', update_videos_list, name='update_videos_list_url'),
    path('update_channels_list/', update_channels_list, name='update_channels_list_url'),
]