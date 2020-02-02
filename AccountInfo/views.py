from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views.generic import View
from google.oauth2 import service_account
from .models import *
from .api_methods import ApiMethods
import math

FIRST_PAGE_TOKEN = 'First'
VIDEO_PAGE_MAX_RESULTS = 10
CHANNEL_PAGE_MAX_RESULTS = 15

class AccountDetail(View):
    def get(self, request):
        if(request.session.get('credentials') != None and request.session['credentials'].get('account_id') != None):
            ApiMethods.connect(request)
            my_account = Account.objects.get(account_id=request.session['credentials']['account_id'])
            if  request.session.get('channel_to_delete')!= None:
                my_account.subscriptions.get(channel_id=request.session['channel_to_delete']).delete()
                request.session.pop('channel_to_delete')
            next_page_token = my_account.pages_list.last().next_page_token
            authorization_url = ApiMethods.get_flow(request)
            return render(request, "AccountInfo/index.html", context={
                        'channels': my_account.subscriptions.all().order_by('page', '-created_at'),
                        'is_authorized': True,
                        'page_token': next_page_token,
                        'authorization_url': authorization_url
                        })

        authorization_url = ApiMethods.get_flow(request)
        return render(request, "AccountInfo/index.html", context={'is_authorized': False, 
                                                                    'authorization_url': authorization_url})
    def post(self, request):
        return self.get(request)

    @staticmethod
    def log_in(request):
        ApiMethods.connect(request)
        my_channel_info = ApiMethods.get_my_channel_info()['items'][0]
        channel_id =  'UU' + my_channel_info['id'][2:]
        account = Account.objects.create(account_id=channel_id)
        title = my_channel_info['snippet']['title']
        url = 'https://www.youtube.com/channel/' + my_channel_info['id']
        published_at = my_channel_info['snippet']['publishedAt'][:10]
        description = my_channel_info['snippet']['description']
        photo = my_channel_info['snippet']['thumbnails']['high']
        my_channel = Channel(account=account,
                            title=title,
                            channel_id=channel_id, 
                            photo=photo, 
                            channel_url=url, 
                            description=description,
                            published_at=published_at)
        my_channel.save()
        account.channel = my_channel
        account.save()

        request.session['credentials']['account_id'] = account.account_id
        print(request.session['credentials']['account_id']) 
        response_data = create_channels_page(request, FIRST_PAGE_TOKEN)
        return redirect('index_url')
    
    @staticmethod
    def log_out(request):
        account_id = request.session['credentials']['account_id']
        account = Account.objects.get(account_id=account_id).delete()
        request.session.pop('credentials')
        return JsonResponse(data={})

class ChannelDetail(View):
    def get(self, request, channel_id):
        ApiMethods.connect(request)

        my_account = Account.objects.get(account_id=request.session['credentials']['account_id'])
        channel = get_object_or_404(my_account.subscriptions, channel_id=channel_id)
        channel_detail = self.get_channel_detail(request, 'UC' + channel_id[2:])
        channel.views_count = channel_detail['views_count']
        channel.subscribers_count = channel_detail['subscriber_count']
        channel.banner_photo = channel_detail['banner_url'].replace('1060', '1920')
        channel.published_at = channel_detail['published_at']
        channel.save()

        next_page_token = ''
        if channel.pages_list.count() != 0:
            next_page_token = channel.pages_list.all().last().next_page_token  
        return render(request, "AccountInfo/channelInfo.html", context={'channel': channel,
                                                             'page_token': next_page_token,
                                                             'videos_list': channel.videos_list.all().order_by('-published_at')})

    
    def get_channel_detail(self, request, channel_id):
        response = ApiMethods.get_channel_detail(channel_id)['items'][0]
        channel_detail = {'views_count': response['statistics']['viewCount'],
                          'subscriber_count': response['statistics']['subscriberCount'],
                          'banner_url': response['brandingSettings']['image']['bannerImageUrl'],
                          'published_at': response['snippet']['publishedAt'][:10],
                         }
        return channel_detail

class VideosPageDetail():
    channel_id = ''
    current_page_token = ''
    next_page_token = ''
    videos_list = []

    def __init__(self, channel_id, page_token):
        self.channel_id = channel_id
        self.current_page_token = page_token
        try:
            channel = Channel.objects.get(channel_id=self.channel_id)
            current_page = channel.pages_list.get(current_page_token=self.current_page_token)
            self.videos_list = current_page.videos_list.all()
        except:
            self.videos_list = []

    def create_videos_page(self):        
        channel = Channel.objects.get(channel_id=self.channel_id)
        self.next_page_token, videos_page = self.get_current_page_videos(VIDEO_PAGE_MAX_RESULTS)

        page = VideoPage.objects.create(current_page_token=self.current_page_token,
                                        next_page_token=self.next_page_token,
                                        channel=channel,
                                        size=VIDEO_PAGE_MAX_RESULTS
                                        )
        for video in videos_page:
            self.create_video(page=page, channel=channel, video=video)
        page.save()
        channel.save()  

        channel = Channel.objects.get(channel_id=self.channel_id)
        current_page = channel.pages_list.get(current_page_token=self.current_page_token)
        self.videos_list = current_page.videos_list.all()  

    def get_current_page_videos(self, max_results=5):
        videos_page = []
        if self.current_page_token == FIRST_PAGE_TOKEN:
            response_info = ApiMethods.get_videos_page( channel_id=self.channel_id,
                                                        max_results=max_results )
        else:
            response_info = ApiMethods.get_videos_page( channel_id=self.channel_id,
                                                        page_token=self.current_page_token,
                                                        max_results=max_results )
                                                
        next_page_token = response_info.get('nextPageToken')
        if next_page_token == None:
            next_page_token = 'Last'

        for video in response_info['items']:
            video_info = {}
            video_info['video_id'] = video['snippet']['resourceId']['videoId']
            video_info['published_at'] = video['snippet']['publishedAt'][:10]
            video_info['title'] = video['snippet']['title']
            video_info['path_to_photo'] = video['snippet']['thumbnails']['medium']['url']

            detail_info = ApiMethods.get_video_detail_info(video_info['video_id'])

            likes_count = int(detail_info['items'][0]['statistics']['likeCount'])
            dislikes_count = int(detail_info['items'][0]['statistics']['dislikeCount'])

            video_info['views_count'] = int(detail_info['items'][0]['statistics']['viewCount'])
            video_info['comments_count'] = int(detail_info['items'][0]['statistics']['commentCount']) 
            video_info['likes_count'] = likes_count    
            video_info['dislikes_count'] = dislikes_count
            if likes_count+dislikes_count == 0:
                video_info['average_likes_count'] = 0
                video_info['average_dislikes_count'] = 0
            else:
                video_info['average_likes_count'] = int(likes_count/(likes_count + dislikes_count)*100)*2
                video_info['average_dislikes_count'] = int(dislikes_count/(likes_count + dislikes_count)*100)*2
        
            videos_page.append(video_info)
        return next_page_token, videos_page 

    def get_current_page(self):
        current_page = {}
        current_page['data'] = {}
        for video in self.videos_list.all():
            current_page['data'][video.video_id] = {'photo': video.photo,
                                                    'title': video.title,
                                                    'likes_count': reduce_number(video.likes_count),
                                                    'dislikes_count': reduce_number(video.dislikes_count),
                                                    'average_likes': reduce_number(video.average_likes),
                                                    'average_dislikes': reduce_number(video.average_dislikes),
                                                    'views_count': reduce_number(video.views_count),
                                                    'comments_count': reduce_number(video.comments_count),
                                                    'published_at': video.published_at,
                                                    'page_token': self.current_page_token,
                                                    }
        current_page['next_page_token'] = self.next_page_token
        return current_page

    def update_videos_page(self):
        channel = Channel.objects.get(channel_id=self.channel_id)
        page = channel.pages_list.get(current_page_token=self.current_page_token)
        updated_page = {}
        for video in page.videos_list.all():
            detail_info = ApiMethods.get_video_detail_info(video_id = video.video_id)['items'][0]['statistics']
            video.likes_count = likes_count = int(detail_info['likeCount'])
            video.dislikes_count = dislikes_count = int(detail_info['dislikeCount'])
            video.views_count = views_count = int(detail_info['viewCount'])
            video.comments_count = comments_count = int(detail_info['commentCount'])
            if likes_count+dislikes_count == 0:
                video.average_likes_count = 0
                video.average_dislikes_count = 0
            else:
                video.average_likes_count = int(likes_count/(likes_count + dislikes_count)*100)*2
                video.average_dislikes_count = int(dislikes_count/(likes_count + dislikes_count)*100)*2
            video.save()

    def create_video(self, channel, page, video):
        new_video = Video()
        new_video.title = video['title']
        new_video.video_id = video['video_id']
        new_video.photo = video['path_to_photo']
        new_video.likes_count = video['likes_count']
        new_video.dislikes_count = video['dislikes_count']
        new_video.views_count = video['views_count']
        new_video.comments_count = video['comments_count']
        new_video.average_likes = video['average_likes_count']
        new_video.average_dislikes = video['average_dislikes_count']
        new_video.published_at = video['published_at']
        new_video.page = page
        new_video.channel = channel
        new_video.save()

class ChannelsPageDetail():
    account_id = ''
    current_page_token = ''
    next_page_token = ''
    channels_list = []

    def __init__(self, account_id, page_token):
        self.account_id = account_id
        self.current_page_token = page_token
        try:
            account = Account.objects.get(account_id=account_id)
            current_page = account.pages_list.get(current_page_token=self.current_page_token)
            self.channels_list = current_page.channels_list.all()
        except:
            self.channels_list = []

    def create_channels_page(self):
        account = Account.objects.get(account_id=self.account_id)
        self.next_page_token, channels_page = self.get_channels(CHANNEL_PAGE_MAX_RESULTS)
        page = ChannelPage.objects.create(current_page_token=self.current_page_token,
                                            next_page_token=self.next_page_token,
                                            account=account,
                                            size=VIDEO_PAGE_MAX_RESULTS
                                            )
        for channel in channels_page:  
            new_channel = Channel(acc=account,
                                title=channel['title'],
                                channel_id=channel['channel_id'], 
                                photo=channel['path_to_photo'], 
                                channel_url=channel['channel_url'], 
                                videos_count=channel['videos_count'],
                                description=channel['description'],
                                page=page
                                 )
            new_channel.save()              
            page.save()
        account.save()

        current_page = account.pages_list.get(current_page_token=self.current_page_token)
        self.channels_list = current_page.channels_list.all()
        return self.get_page()

    def get_channels(self, max_results=10):
        channels_page = []
        if self.current_page_token == FIRST_PAGE_TOKEN:
            response_info = ApiMethods.get_channels_page(max_results=max_results)
        else:
            response_info = ApiMethods.get_channels_page(page_token=self.current_page_token, 
                                                                    max_results=max_results)
                                                
        next_page_token = response_info.get('nextPageToken')
        if next_page_token == None or next_page_token =='':
            next_page_token = 'Last'

        for channel in response_info['items']:
            channel_page = {}
            channel_id = channel['snippet']['resourceId']['channelId']
            channel_page['channel_id'] =  'UU' + channel_id[2:]
            channel_page['videos_count'] = channel['contentDetails']['totalItemCount']
            channel_page['title'] = channel['snippet']['title']   
            channel_page['channel_url'] = 'https://www.youtube.com/channel/' + channel_id
            channel_page['path_to_photo'] = channel['snippet']['thumbnails']['high']['url']
            channel_page['description'] = channel['snippet']['description']  
            
            channels_page.append(channel_page)

        return next_page_token, channels_page

    def get_page(self):
        current_page = {}
        current_page['data'] = {}
        for channel in self.channels_list:
            current_page['data'][channel.channel_id] = {'photo': channel.photo,
                                                        'title': channel.title,
                                                        'videos_count': channel.videos_count,
                                                        'channel_url': channel.channel_url,
                                                        'page_token': self.current_page_token
                                                        }
        current_page['next_page_token'] = self.next_page_token
        return current_page

    def update_channels_page(self):
        channel_counter = 0
        updated_channels = self.get_channels(CHANNEL_PAGE_MAX_RESULTS)[1]
        for channel in self.channels_list:
            updated_channel = updated_channels[channel_counter]
            channel.title=updated_channel['title']
            channel.channel_id=updated_channel['channel_id']
            channel.photo=updated_channel['path_to_photo']
            channel.channel_url=updated_channel['channel_url']
            channel.videos_count=updated_channel['videos_count']
            channel.description=updated_channel['description']
            channel_counter += 1
        
        return self.get_page()

def create_channels_page(request, page_token):
    account_id = request.session['credentials']['account_id']
    channels_page = ChannelsPageDetail(account_id = account_id, 
                                            page_token = page_token)
    new_channels_page = channels_page.create_channels_page()
    return JsonResponse(data=new_channels_page)
 
def update_channels_page(request, page_token):
    ApiMethods.connect(request)
    if request.method == 'POST' and request.is_ajax():
        account_id = request.session['credentials']['account_id']
        channels_page = ChannelsPageDetail(account_id = account_id, 
                                            page_token = page_token)
        updated_channels_page = channels_page.update_channels_page()
        return JsonResponse(data=updated_channels_page)
    else:
        return HttpResponseForbidden()

def create_videos_page(request, channel_id, page_token):
    if request.method == 'POST' and request.is_ajax():
        new_videos_page = VideosPageDetail(channel_id, page_token)
        new_videos_page.create_videos_page()
        return JsonResponse(data=new_videos_page.get_current_page())
    else:
        return HttpResponseForbidden()

def update_videos_page(request, channel_id, page_token):
    ApiMethods.connect(request)
    if request.method == 'POST' and request.is_ajax():
        videos_page = VideosPageDetail(channel_id, page_token)
        videos_page.update_videos_page()
        return JsonResponse(data=videos_page.get_current_page())
    else:
        return HttpResponseForbidden()

def get_policy(request):
    return render(request, 'AccountInfo/policy.html')

def get_terms(request):
    return render(request, 'AccountInfo/terms.html')

def confirm_html(request):
    return render(request, 'AccountInfo/include/google34ecf22213c98a0d.html')

def get_token(request):
    authorization_response = request.build_absolute_uri()
    state = request.GET.get('state')
    ApiMethods.connect(request, authorization_response, state)
    return AccountDetail.log_in(request)

def find_channel(request):
    url = request.POST.get('url')
    channel_id = url.rsplit('/', 1)[-1]
    channel_info = ApiMethods.get_channel_detail(channel_id)
    if channel_info['pageInfo']['totalResults'] == 0:
        return HttpResponse('Канал не найден')
    channel_info = channel_info['items'][0]
    channel_id = channel_info['id']
    channel_playlist_id = 'UU' + channel_id[2:]
    account = Account.objects.get(account_id = request.session['credentials']['account_id'])
    try:
        account.subscriptions.get(channel_id=channel_playlist_id)
    except:
        channel = Channel(
                        acc=account, 
                        channel_id =  channel_playlist_id,
                        videos_count = channel_info['statistics']['videoCount'],
                        title = channel_info['snippet']['title'],   
                        channel_url = 'https://www.youtube.com/channel/' + channel_id ,
                        photo = channel_info['snippet']['thumbnails']['high']['url'],
                        description = channel_info['snippet']['description']
                        )
        channel.save()
    channel_id =  'UU' + channel_id[2:]
    request.session['channel_to_delete'] = channel_id
    redirect_uri = reverse('channel_info_url', args=[channel_playlist_id])
    return redirect(redirect_uri)

def create_new_videos(channel):
    new_videos_list = []
    current_page_token = None
    while(current_page_token!='Last'):
        videos_page = ApiMethods.get_videos_page(channel_id=channel.channel_id,
                                                max_results=VIDEO_PAGE_MAX_RESULTS,
                                                page_token=current_page_token)
        if current_page_token == None:
                    current_page_token = 'First'
        
        next_page_token = videos_page.get('nextPageToken')
        if next_page_token == None:
            next_page_token = 'Last'
        
        for video in videos_page['items']:
            video_id=video['snippet']['resourceId']['videoId']
            try:
                current_page = channel.pages_list.get(current_page_token=current_page_token)
            except:
                current_page = VideoPage(current_page_token=current_page_token, 
                                        next_page_token=next_page_token,
                                        channel=channel)
                current_page.save()
            try:
                current_video = channel.videos_list.get(video_id=video_id)
                return new_videos_list
            except:
                new_video = create_video(video, channel)
                new_video.page = current_page
                new_video.save()
                new_videos_list.append(new_video.title)

        current_page_token = next_page_token
    return new_videos_list

def update_videos_list(request, channel_id):
    ApiMethods.connect(request)
    account = Account.objects.get(account_id=request.session['credentials']['account_id'])
    channel = account.subscriptions.get(channel_id=channel_id)

    new_videos = create_new_videos(channel)
    removed_videos = remove_deleted_videos(channel)

    data = {}
    data['next_page_token'] = channel.pages_list.last().next_page_token
    data['data'] = {}
    
    if  len(new_videos) != 0 or len(removed_videos) != 0:    
        for video in channel.videos_list.all().order_by('-published_at'):
            data['data'][video.video_id] = {'photo': video.photo,
                                                    'title': video.title,
                                                    'likes_count': reduce_number(video.likes_count),
                                                    'dislikes_count': reduce_number(video.dislikes_count),
                                                    'average_likes': reduce_number(video.average_likes),
                                                    'average_dislikes': reduce_number(video.average_dislikes),
                                                    'views_count': reduce_number(video.views_count),
                                                    'comments_count': reduce_number(video.comments_count),
                                                    'published_at': video.published_at,
                                                    'page_token': video.page.current_page_token,
                                                    }
    
    return JsonResponse(data=data)

def create_video(video, channel):
    video_id=video['snippet']['resourceId']['videoId']
    new_video = Video(video_id=video_id,
                    published_at = video['snippet']['publishedAt'][:10],
                    title = video['snippet']['title'],
                    photo = video['snippet']['thumbnails']['medium']['url'], 
                    channel=channel
                    )   
                
    detail_info = ApiMethods.get_video_detail_info(video_id)

    likes_count = int(detail_info['items'][0]['statistics']['likeCount'])
    dislikes_count = int(detail_info['items'][0]['statistics']['dislikeCount'])

    new_video.views_count = int(detail_info['items'][0]['statistics']['viewCount'])
    new_video.comments_count = int(detail_info['items'][0]['statistics']['commentCount'])
    new_video.likes_count = likes_count    
    new_video.dislikes_count = dislikes_count
    if likes_count+dislikes_count == 0:
        new_video.average_likes_count = 0
        new_video.average_dislikes_count = 0
    else:
        new_video.average_likes_count = int(likes_count/(likes_count + dislikes_count)*100)*2
        new_video.average_dislikes_count = int(dislikes_count/(likes_count + dislikes_count)*100)*2
    new_video.save()
    return new_video

def remove_deleted_videos(channel):
    channel_videos_count = channel.videos_list.count()
    new_videos_set = set()
    old_videos_set = set()
    pages_count = math.ceil(channel_videos_count/VIDEO_PAGE_MAX_RESULTS)
    current_page_token = None
    for page_num in range(pages_count):
        current_page = ApiMethods.get_videos_page(channel_id=channel.channel_id,
                                                max_results=VIDEO_PAGE_MAX_RESULTS,
                                                page_token=current_page_token)
        if current_page_token == None:
            current_page_token = 'First'
        try:
            next_page_token = current_page['nextPageToken']
        except:
            next_page_token = 'Last'

        try:
            current_videos_page = channel.pages_list.get(
                        current_page_token=current_page_token)
        except:
            current_videos_page = VideoPage(current_page_token=current_page_token,
                                            next_page_token=next_page_token,
                                            channel=channel
                                            )
            current_videos_page.save()
        for video in current_page['items']:
            video_id = video['snippet']['resourceId']['videoId']
            old_video = channel.videos_list.get(video_id=video_id)
            old_video.page = current_videos_page
            old_video.save()
            new_videos_set.add(video_id)
        
        current_page_token = next_page_token
    
    for video in channel.videos_list.all():
        old_videos_set.add(video.video_id)

    different_set = old_videos_set.difference(new_videos_set)
    for video_id in different_set:       
        channel.videos_list.get(video_id=video_id).delete()
    
    return different_set

def create_new_channels(account):
    new_channels_list = []
    current_page_token = None
    while(current_page_token!='Last'):
        channels_page = ApiMethods.get_channels_page(CHANNEL_PAGE_MAX_RESULTS, current_page_token)
        if current_page_token == None:
                    current_page_token = 'First'
        
        next_page_token = channels_page.get('nextPageToken')
        if next_page_token == None:
            next_page_token = 'Last'
        
        for channel in channels_page['items']:
            channel_id = 'UU' + channel['snippet']['resourceId']['channelId'][2:]
            try:
                current_page = account.pages_list.get(current_page_token=current_page_token)
            except:
                current_page = ChannelPage(current_page_token=current_page_token, 
                                            next_page_token=next_page_token,
                                            account=account)
                current_page.save()
            try:
                current_channel = account.subscriptions.get(channel_id=channel_id)
                return new_channels_list
            except:
                new_channel = create_channel(account, channel)
                new_channel.page = current_page
                new_channel.save()
                new_channels_list.append(new_channel.title)

        current_page_token = next_page_token
    return new_channels_list

def create_channel(account, channel):
    channel_id = 'UU' + channel['snippet']['resourceId']['channelId'][2:]
    new_channel = Channel(acc=account,
                        title=channel['snippet']['title'],
                        channel_id=channel_id, 
                        photo=channel['snippet']['thumbnails']['high']['url'], 
                        channel_url='https://www.youtube.com/channel/UU' + channel_id[2:], 
                        videos_count=channel['contentDetails']['totalItemCount'],
                        description=channel['snippet']['description'],
                        )   
    new_channel.save()
    return new_channel

def remove_deleted_channels(account):
    channels_count = account.subscriptions.count()
    new_channels_set = set()
    old_channels_set = set()
    pages_count = math.ceil(channels_count/CHANNEL_PAGE_MAX_RESULTS)
    
    current_page_token = None
    for page_num in range(pages_count):
        current_page = ApiMethods.get_channels_page(max_results=CHANNEL_PAGE_MAX_RESULTS,
                                                page_token=current_page_token)
        if current_page_token == None:
            current_page_token = 'First'
        try:
            next_page_token = current_page['nextPageToken']
        except:
            next_page_token = 'Last'

        try:
            current_channels_page = account.pages_list.get(
                        current_page_token=current_page_token)
        except:
            current_channels_page = ChannelPage(current_page_token=current_page_token,
                                                next_page_token=next_page_token,
                                                account=account
                                                )
            current_channels_page.save()
        for channel in current_page['items']:
            channel_id = channel['snippet']['resourceId']['channelId']
            title = channel['snippet']['title']
            try:
                old_channel = account.subscriptions.get(channel_id=channel_id)
                old_channel.page = current_channels_page
                old_channel.save()
            except:
                pass
            new_channels_set.add('UU'+channel_id[2:])
        
        current_page_token = next_page_token
    
    for channel in account.subscriptions.all():
        old_channels_set.add(channel.channel_id)

    print('old: ', old_channels_set)
    print('new: ', new_channels_set)
    different_set = old_channels_set.difference(new_channels_set)
    print(different_set)
    for channel_id in different_set:       
        account.subscriptions.get(channel_id=channel_id).delete()
    
    return different_set

def update_channels_list(request):
    ApiMethods.connect(request)
    account = Account.objects.get(account_id=request.session['credentials']['account_id'])

    new_channels = create_new_channels(account)
    removed_channels = remove_deleted_channels(account)

    data = {}
    data['next_page_token'] = account.pages_list.last().next_page_token
    data['data'] = {}
    
    if  len(new_channels) != 0 or len(removed_channels) != 0:    
        for channel in account.subscriptions.all().order_by('page', '-created_at'):
            data['data'][channel.channel_id] = {'photo': channel.photo,
                                                'title': channel.title,
                                                'videos_count': channel.videos_count,
                                                'channel_url': channel.channel_url,
                                                'page_token': channel.page.current_page_token
                                                }
    
    return JsonResponse(data=data)