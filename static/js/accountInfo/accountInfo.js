const INTERVAL = 60*1000;
const DELAY = 47*1000;
const FIRST_PAGE_TOKEN = 'First'
const LAST_PAGE_TOKEN = 'Last'

function getNewChannelsHTML(data){
    var newChannelsHTML = '';
    for(var channel_id in data){
        var channel = data[channel_id];
        channel.title = channel.title.slice(0, 30);
        newChannelsHTML +=`<div class="channel-card" data-page-token=${channel.page_token}>`+
                                `<div class="row">`+
                                    `<div class="channel-card-photo col-4">`+
                                        `<img src="${channel.photo}" alt='Channel photo'>`+
                                    `</div>`+
                                    `<div class="channel-card-body col-8">`+
                                        `<div class="channel-title row">`+
                                            `<a href="/channel_id/${channel_id}" target="_blank" title="${channel.title}">`+
                                                `${channel.title}`+
                                            `</a>`+
                                        `</div>`+
                                        `<div class="channel-info row">`+
                                            `<span>Видео: ${channel.videos_count}</span>`+
                                        `</div>`+
                                        `<div class="channel-url row">`+
                                            `<a href="${channel.channel_url}">Ссылка на канал</a>`+
                                        `</div>`+
                                    `</div>`+
                                `</div>` +
                            `</div>`
    }
    return newChannelsHTML;
}

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

$('.log-out-btn').click(function(e){            
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: '/log_out/',
        async: true,
        data: $(this).parent().serialize(),
        success: function(responseData){ 
            $('.channels-block').empty();
            $('.log-in-btn').css('display', 'block');
            $('.log-out-btn').css('display', 'none');                
            $(".next-channels-page-btn").css('display', 'none');
            setPageUpdTimeout(FIRST_PAGE_TOKEN, INTERVAL);
        }
    });
});

$(document).ready(function (){
    if($('.log-in-btn').css('display') == 'none'){
        setPagesLifeCycle();
        if($('.next-page-token').val() != LAST_PAGE_TOKEN){
            console.log(1);
            $(".next-channels-page-btn").css('display', 'block');
        }  
    }              
});