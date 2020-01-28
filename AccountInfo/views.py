from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import View
from google.oauth2 import service_account
from .models import *
from .api_methods import ApiMethods

FIRST_PAGE_TOKEN = 'First'
VIDEO_PAGE_MAX_RESULTS = 10
CHANNEL_PAGE_MAX_RESULTS = 15

class AccountDetail(View):
    def get(self, request):
        if(request.session.get('credentials') != None and request.session['credentials'].get('account_id') != None):
            my_account = Account.objects.get(account_id=request.session['credentials']['account_id'])
            next_page_token = my_account.pages_list.last().next_page_token
            return render(request, "AccountInfo/index.html", context={'channels': my_account.subscriptions.all(),
                                                                      'is_authorized': True,
                                                                      'page_token': next_page_token,
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
        channel = Channel.objects.get(channel_id=channel_id)
        channel_detail = self.get_channel_detail(request, 'UC' + channel_id[2:])
        channel.views_count = channel_detail['views_count']
        channel.subscribers_count = channel_detail['subscriber_count']
        channel.banner_photo = channel_detail['banner_url']

        next_page_token = ''
        if channel.pages_list.count() != 0:            
            next_page_token = channel.pages_list.all().last().next_page_token  
        return render(request, "AccountInfo/channelInfo.html", context={'channel': channel, 'page_token': next_page_token})

    
    def get_channel_detail(self, request, channel_id):
        response = ApiMethods.get_channel_detail(channel_id)['items'][0]
        channel_detail = {'views_count': response['statistics']['viewCount'],
                          'subscriber_count': response['statistics']['subscriberCount'],
                          'banner_url': response['brandingSettings']['image']['bannerImageUrl']
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
            video_info['published_at'] = video['snippet']['publishedAt']
            video_info['title'] = video['snippet']['title']
            video_info['path_to_photo'] = video['snippet']['thumbnails']['medium']['url']

            detail_info = ApiMethods.get_video_detail_info(video_info['video_id'])

            likes_count = int(detail_info['items'][0]['statistics']['likeCount'])
            dislikes_count = int(detail_info['items'][0]['statistics']['dislikeCount'])

            video_info['views_count'] = int(detail_info['items'][0]['statistics']['viewCount'])            
            video_info['comments_count'] = int(detail_info['items'][0]['statistics']['commentCount']) 
            video_info['likes_count'] = likes_count    
            video_info['dislikes_count'] = dislikes_count    
            video_info['average_likes_count'] = int(likes_count/(likes_count + dislikes_count)*100)
            video_info['average_dislikes_count'] = int(dislikes_count/(likes_count + dislikes_count)*100)
        
            videos_page.append(video_info)        
        return next_page_token, videos_page 

    def get_current_page(self):
        current_page = {}
        current_page['data'] = {}
        for video in self.videos_list.all():
            current_page['data'][video.video_id] = {'photo': video.photo,
                                                    'title': video.title,
                                                    'likes_count': video.likes_count,
                                                    'dislikes_count': video.dislikes_count,
                                                    'average_likes': video.average_likes,
                                                    'average_dislikes': video.average_dislikes,
                                                    'views_count': video.views_count,
                                                    'comments_count': video.comments_count,
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
            video.average_likes = average_likes = int(likes_count/(likes_count + dislikes_count)*100)
            video.average_dislikes = average_dislikes = int(dislikes_count/(likes_count + dislikes_count)*100)
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
                                    published_at=channel['published_at'],
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
            channel_page['published_at'] = channel['snippet']['publishedAt'][:10]           
            
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
            channel.published_at=updated_channel['published_at']
            channel_counter += 1
        
        return self.get_page()

def create_channels_page(request, page_token):
    account_id = request.session['credentials']['account_id']
    channels_page = ChannelsPageDetail(account_id = account_id, 
                                            page_token = page_token)
    new_channels_page = channels_page.create_channels_page()
    return JsonResponse(data=new_channels_page)
    

def update_channels_page(request, page_token):
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