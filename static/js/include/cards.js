export function getNewChannelsHTML(data){
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

export function getNewVideosHTML(data){
    var newVideosHTML = "";
    for(var video_id in data){
        var video = data[video_id];
        var cut_title;
        if(video.title.length >= 21)        
            cut_title = video.title.slice(0, 18) + '...';
        else
            cut_title = video.title;
        newVideosHTML += `<div class="card video-card mr-5 mt-5" style="width: 18rem;" data-video-id=${video_id} page-token=${video.page_token}>`+
                            `<img src="${video.photo}" class="card-img-top" alt="video-img">`+
                            `<div class="card-body">`+
                                `<h5 class="card-title">`+
                                    `<a href="https://www.youtube.com/watch?v=${video_id}" target="_blank" title="${video.title}">`+
                                        `${cut_title}`+
                                    `</a>`+
                                `</h5>`+
                                `<div class="detail-info-block">`+                                
                                    `<div class="views-count-block">`+
                                        `Просмотров: ${video.views_count}`+
                                    `</div>`+
                                    `<div class="comments-count-block">`+
                                        `Комментариев: ${video.comments_count}`+
                                    `</div>`+
                                    `<div class="published-at-block">`+
                                    `Дата выхода: ${video.published_at}`+
                                  `</div>`+
                                `</div>`+
                                `<div class="rating-block row ml-3">`+
                                    `<div class="likes-block">`+
                                        `<p>${video.likes_count}</p>`+
                                        `<div class="likes-count-block" style="width:${video.average_likes}px"></div>`+
                                        `</div>`+
                                    `<div class="dislikes-block">`+
                                        `<p>${video.dislikes_count}</p>`+
                                        `<div class="dislikes-count-block" style="width:${video.average_dislikes}px"></div>`+
                                    `</div>`+
                                `</div>`+
                            `</div>`+
                        `</div>`;
        }
    return newVideosHTML
}