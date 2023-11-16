import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

from YouTubeApi.settings import BASE_DIR

scopes = ['https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/userinfo.email',
          'openid',
          'https://www.googleapis.com/auth/userinfo.profile']
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = os.path.join(BASE_DIR, "static/info.json")
redirect_uri = "http://localhost:8000/token"

class ApiMethods:
    youtube = None

    @staticmethod
    def connect(request, authorization_response=None, state=None):
        if request.session.get('credentials') is None:
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                                                client_secrets_file,
                                                scopes=scopes,
                                                state=state)
            flow.redirect_uri = redirect_uri
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials

            request.session['credentials'] = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'id_token': credentials.id_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': scopes
            }

        credentials_dict = request.session.get('credentials')
        credentials = Credentials(token=credentials_dict['token'],
                                    refresh_token=credentials_dict['refresh_token'],
                                    token_uri=credentials_dict['token_uri'],
                                    client_id=credentials_dict['client_id'],
                                    client_secret=credentials_dict['client_secret'],
                                    scopes=credentials_dict['scopes'])

        ApiMethods.youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    @staticmethod
    def get_flow():
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=scopes)
        flow.redirect_uri = redirect_uri

        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true', scopes=scopes)

        return authorization_url

    @staticmethod
    def get_my_channel_info():
        request = ApiMethods.youtube.channels().list(
            part="snippet",
            mine=True
        )
        my_channel_info = request.execute()
        return my_channel_info

    @staticmethod
    def get_videos_page(channel_id, max_results, page_token=None):
        if page_token is None:
            query = ApiMethods.youtube.playlistItems().list(
                part="snippet",
                playlistId=channel_id,
                maxResults=max_results
            )
        else:
            query = ApiMethods.youtube.playlistItems().list(
                part="snippet",
                playlistId=channel_id,
                pageToken=page_token,
                maxResults=max_results
            )

        videos_page = query.execute()
        return videos_page

    @staticmethod
    def get_video_detail_info(video_id):
        query = ApiMethods.youtube.videos().list(
            part="statistics",
            id=video_id
        )
        video_detail_info = query.execute()
        return video_detail_info

    @staticmethod
    def get_channels_page(max_results, page_token=None):
        if page_token:
            query = ApiMethods.youtube.subscriptions().list(
                part="snippet, contentDetails",
                mine=True,
                maxResults=max_results,
                pageToken=page_token,
            )
        else:
            query = ApiMethods.youtube.subscriptions().list(
                part="snippet, contentDetails",
                maxResults=max_results,
                mine=True,
            )

        channels_page = query.execute()
        return channels_page

    @staticmethod
    def get_channel_detail(channel_id):
        query = ApiMethods.youtube.channels().list(
            part="snippet,statistics,brandingSettings",
            id=channel_id
        )
        channel_detail = query.execute()
        if channel_detail['pageInfo']['totalResults'] == 0:
            query = ApiMethods.youtube.channels().list(
                part="snippet,statistics,brandingSettings",
                forUsername=channel_id
            )
            channel_detail = query.execute()
        return channel_detail
