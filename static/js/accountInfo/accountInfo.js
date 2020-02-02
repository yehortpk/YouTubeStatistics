import { getNewChannelsHTML } from '/static/js/include/cards.js';
const INTERVAL = 60*1000;
const DELAY = 47*1000;
const FIRST_PAGE_TOKEN = 'First'
const LAST_PAGE_TOKEN = 'Last'

function updateChannelsPage(pageToken){
    $.ajax({
        type: 'POST',
        url: `/update_channels_page/${pageToken}`,
        async: true,
        data: $('.next-channels-page-form').serialize(),
        success: function(responseData){
            $(`.channels-card[data-page-token=${pageToken}]`).each(function(channel){
                var currentChannel = responseData['data'][$(this).data('channelId')];
                $('.channel-card-photo').find('img').data('src') = currentChannel.photo;
                $('.channel-title').find('a').data('href') = '/channel_id/' + $(this).data('channelId');
                $('.channel-title').find('a').text(currentChannel.title);
                $('.channel-info').text(`Видео: ${currentChannel.videos_count}`);
                $('.channel-url').find('a').data('href') = currentChannel.channel_url;                
            });
            setPageUpdTimeout(pageToken, INTERVAL);
        },
        dataType: 'json',
    });
}

function setPageUpdTimeout(pageToken, interval){
    setTimeout(updateChannelsPage, interval, pageToken);
}

function setPagesLifeCycle(){
    var delay = 0;
    var tokens_list = []
    $('.channel-card').each(function(){
        var token = $(this).data('pageToken');
        if(tokens_list.indexOf(token) == -1)
            tokens_list.push(token);
    })
    tokens_list.forEach(function(token){
        setPageUpdTimeout(token, INTERVAL+delay);
        delay+=DELAY;
    })   
}

$(".next-channels-page-btn").click(function(e) {
    e.preventDefault();                                
    var data = $(this).parent().serialize();
    var nextPageTokenBlock = $(this).prev();
    var nextPageTokenValue = nextPageTokenBlock.val();
    $.ajax({
        type: 'POST',
        url: `/create_channels_page/${nextPageTokenValue}`,
        async: true,
        data: data,
        success: function(responseData) {
            nextPageTokenBlock.val(responseData['next_page_token']);
            var newChannelsHTML = getNewChannelsHTML(responseData['data']);
            $('.channels-block').append(newChannelsHTML);
            setPageUpdTimeout(nextPageTokenValue, INTERVAL);
            if(responseData['next_page_token'] == LAST_PAGE_TOKEN)
                $(".next-channels-page-btn").css('display', 'none');
        },
        dataType: 'json',
    })
});

function totalChannelsUpdate(){
    var data = $('.update-token').serialize();
    $.ajax({
        type: 'POST',
        url: `/update_channels_list/`,
        async: true,
        data: data,
        success: function(responseData) {
            if(Object.keys(responseData['data']).length != 0){
                $('.channels-block').empty();
                var newChannelsHTML = getNewChannelsHTML(responseData['data']);
                $('.channels-block').append(newChannelsHTML);
                $(".next-page-token").val(responseData['next_page_token']);             
                setPagesLifeCycle();
            }
            if(responseData['next_page_token'] == LAST_PAGE_TOKEN)
                    $(".next-channels-page-btn").css('display', 'none');
        },
        dataType: 'json', 
    });
}

function clearAllTymeouts(){
    var id = window.setTimeout(function() {}, 0);

    while (id--) {
        window.clearTimeout(id); // will do nothing if no timeout with id is present
    }
}

$('.log-out-btn').click(function(){
    clearAllTymeouts();
    location.replace('/log_out/');
})

$(document).ready(function (){
    if($('.log-in-btn').css('display') == 'none'){
        totalChannelsUpdate();
        clearAllTymeouts();
        setPagesLifeCycle();
        if($('.next-page-token').val() != LAST_PAGE_TOKEN){
            $(".next-channels-page-btn").css('display', 'block');
        }  
    }
    else{
        clearAllTymeouts();
    }              
});