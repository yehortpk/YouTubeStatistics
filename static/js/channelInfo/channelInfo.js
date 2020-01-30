import { getNewVideosHTML } from '/static/js/include/cards.js';
const INTERVAL = 20*1000;
const DELAY = 17*1000;
const FIRST_PAGE_TOKEN = 'First'
const LAST_PAGE_TOKEN = 'Last'
var channel_id = window.location.pathname.split('/channel_id/')[1];   

function createFirstVideosPage(){
    $('next-page-token').val(FIRST_PAGE_TOKEN)
    var data = $(".next-videos-page-form").serialize();
    $.ajax({
        type: 'POST',
        url: `/create_videos_page/${channel_id}/${FIRST_PAGE_TOKEN}`,
        async: true,
        data: data,
        success: function(responseData) {
            var nextPageTokenValue = responseData['next_page_token'];
            $(".next-page-token").val(nextPageTokenValue);
            var newVideosHTML = getNewVideosHTML(responseData['data']);
            $('.videos-block').append(newVideosHTML);
            setPageUpdTimeout(channel_id, FIRST_PAGE_TOKEN, INTERVAL);
            if(nextPageTokenValue != LAST_PAGE_TOKEN)
                $(".next-videos-page-btn").css('display', 'block');
        },
        dataType: 'json',
    });
}

function updateVideosPage(channelId, pageToken){
    $.ajax({
        type: 'POST',
        url: `/update_videos_page/${channelId}/${pageToken}`,
        async: true,
        data: $('.next-videos-page-form').serialize(),
        success: function(responseData){
            $(`.video-card[data-page-token=${pageToken}]`).each(function(video){
                var currentVideo = responseData['data'][$(this).data('videoId')];
                var detailInfoBlock = $(this).find('.detail-info-block');
                var ratingBlock = $(this).find('.rating-block');
                detailInfoBlock.find('.views-count-block').text(`Просмотров: ${currentVideo.views_count}`);
                detailInfoBlock.find('.comments-count-block').text(`Комментариев: ${currentVideo.comments_count}`);
                ratingBlock.find('.likes-block').find('p').text(currentVideo.likes_count);
                ratingBlock.find('.dislikes-block').find('p').text(currentVideo.dislikes_count);
                ratingBlock.find('.likes-block').find('.likes-count-block').css('width', currentVideo.average_likes + 'px');
                ratingBlock.find('.dislikes-block').find('.dislikes-count-block').css('width', currentVideo.average_dislikes + 'px');                
            });
            setPageUpdTimeout(channelId, pageToken, INTERVAL);
        },
        dataType: 'json',
    });
}

function setPageUpdTimeout(channel_id, pageToken, interval){
    setTimeout(updateVideosPage, interval, channel_id, pageToken);
}

function setPagesLifeCycle(channel_id){
    var delay = 0;
    var tokens_list = []
    $('.video-card').each(function(){
        var token = $(this).data('pageToken');
        if(tokens_list.indexOf(token) == -1)
            tokens_list.push(token);
    })
    tokens_list.forEach(function(token){
        setPageUpdTimeout(channel_id, token, INTERVAL+delay);
        delay+=DELAY;
    })
}

$(".next-videos-page-btn").click(function(e) {
    e.preventDefault();                                
    var data = $(this).parent().serialize();
    var nextPageTokenBlock = $(this).prev();
    var nextPageTokenValue = nextPageTokenBlock.val();
    $.ajax({
        type: 'POST',
        url: `/create_videos_page/${channel_id}/${nextPageTokenValue}`,
        async: true,
        data: data,
        success: function(responseData) {
            if(responseData['next_page_token'] == LAST_PAGE_TOKEN)
                $(".next-videos-page-btn").css('display', 'none');
            else
                nextPageTokenBlock.val(responseData['next_page_token']);
            var newVideosHTML = getNewVideosHTML(responseData['data']);
            $('.videos-block').append(newVideosHTML);
            setPageUpdTimeout(channel_id, nextPageTokenValue, INTERVAL);
        },
        dataType: 'json',
    });               
})

$(document).ready(function (){
    if($('.next-page-token').val() == ''){
        createFirstVideosPage();
    }
    else
        $(".next-videos-page-btn").css('display', 'block');
    setPagesLifeCycle(channel_id, INTERVAL);
})