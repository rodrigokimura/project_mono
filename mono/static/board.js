var intervals = [];
var cardBeingDragged;
var containerCardIsOver;
var bucketBeingDragged;
var containerBucketIsOver;
var scrollIntervalID;
var isScrolling = false;
var itemEdited = false;


const setFullscreen = bool => {
    $.api({
        on: 'now',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/`,
        method: 'PATCH',
        headers: { 'X-CSRFToken': csrftoken },
        data: { fullscreen: bool },
        success: r => {
            let icon = $('.fullscreen.item i.icon');
            if (r.fullscreen) {
                icon.removeClass('expand alternate icon').addClass('compress alternate icon');
                $('.breadcrumb').parent().parent().parent().hide();
                adjustBoardHeight();
            } else {
                icon.removeClass('compress alternate icon').addClass('expand alternate icon');
                $('.breadcrumb').parent().parent().parent().show();
                adjustBoardHeight();
            };
        },
        error: r => { alert(JSON.stringify(r)) },
    });
};

const changeBucketWidth = width => {
    $.api({
        on: 'now',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/`,
        method: 'PATCH',
        headers: { 'X-CSRFToken': csrftoken },
        data: { bucket_width: width },
        onSuccess: r => {
            loadBoard();
        },
        onError: r => { alert(JSON.stringify(r)) },
    });
};

const setCompact = bool => {
    $.api({
        on: 'now',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/`,
        method: 'PATCH',
        headers: { 'X-CSRFToken': csrftoken },
        data: { compact: bool },
        onSuccess: r => {
            loadBoard(r.compact);
        },
        onError: r => { alert(JSON.stringify(r)) },
    });
};

const toggleFullscreen = () => {
    let icon = $('.fullscreen.item i.icon');
    setFullscreen(icon.hasClass('expand alternate icon'));
};

const setDarkMode = bool => {
    $.api({
        on: 'now',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/`,
        method: 'PATCH',
        headers: { 'X-CSRFToken': csrftoken },
        data: { dark: bool },
        onSuccess: r => {
            loadBoard(r.dark);
        },
        onError: r => { alert(JSON.stringify(r)) },
    });
};

const startElementScroll = (directionX, directionY, elementToScroll, increment, delay) => {
    let scroll = () => {
        elementToScroll.scrollBy(directionX * increment, directionY * increment);
    };
    if (!isScrolling) {
        scrollIntervalID = setInterval(scroll, delay);
        isScrolling = true;
    };
};

const stopElementScroll = intID => {
    clearInterval(intID);
    isScrolling = false;
};

var bucketsDrake = dragula({
    isContainer: el => $(el).hasClass('buckets-drake'),
    moves: (el, source, handle, sibling) =>
        $(el).hasClass('bucket-el')
        && (
            $(handle).hasClass('handle') // use button as handle
            || $(handle).parent().hasClass('handle') // also accept i tag (icon) as handle
        ),
    accepts: (el, target, source, sibling) => sibling !== null,
    invalid: (el, handle) => $(el).hasClass('card-el'),
    direction: 'horizontal'
})
    .on('drop', (el, target, source, sibling) => {
        $(el).removeClass('card').addClass('loading card');
        bucket = $(el).attr('data-bucket-id');
        order = $(target).children().toArray().findIndex(e => e == el) + 1;
        $.ajax({
            url: `/pm/api/bucket_move/`,
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                bucket: bucket,
                board: BOARD_ID,
                order: order,
            },
            success: result => { },
            complete: () => { $(el).removeClass('loading'); }
        });
    })
    .on('drag', (el, source) => {
        bucketBeingDragged = el;
    })
    .on('dragend', (el) => {
        bucketBeingDragged = null;
        stopElementScroll(scrollIntervalID);
    })
    .on('over', (el, container, source) => {
        containerBucketIsOver = container;
    })
    .on('out', (el, container, source) => {
        containerBucketIsOver = null;
    });

var cardsDrake = dragula({
    isContainer: el => $(el).hasClass('cards-drake'),
    moves: (el, source, handle, sibling) =>
        $(el).hasClass('card-el')
        && (
            $(handle).hasClass('handle') // use button as handle
            || $(handle).parent().hasClass('handle') // also accept i tag (icon) as handle
        ),
    direction: 'vertical',
    slideFactorX: '50px',
    slideFactorY: '50px',
})
    .on('drop', (el, target, source, sibling) => {
        $(el).removeClass('card').addClass('loading card');
        source_bucket = $(source).attr('id').replace('bucket-', '');
        target_bucket = $(target).attr('id').replace('bucket-', '');
        card = $(el).attr('data-card-id');
        order = $(target).children().toArray().findIndex(e => e == el) + 1;
        $.ajax({
            url: `/pm/api/card_move/`,
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                source_bucket: source_bucket,
                target_bucket: target_bucket,
                card: card,
                order: order,
            },
            success: r => {
                if (r.success) {
                    status_changed = r.status_changed;
                    timer_action = r.timer_action;
                    if (status_changed || timer_action != 'none') {
                        loadBoard();
                    };
                };
            },
            complete: () => { $(el).removeClass('loading'); }
        });
    })
    .on('drag', (el, source) => {
        cardBeingDragged = el;
    })
    .on('dragend', (el) => {
        cardBeingDragged = null;
        stopElementScroll(scrollIntervalID);
    })
    .on('over', (el, container, source) => {
        containerCardIsOver = container;
    })
    .on('out', (el, container, source) => {
        containerCardIsOver = null;
    });

const adjustBoardHeight = (boardSelector = '#board') => {
    $(boardSelector).height(
        $(window).height()
        - $(boardSelector).offset().top
    );
};

const str = seconds => {
    function pad(num, size = 2) {
        num = num.toString();
        while (num.length < size) num = "0" + num;
        return num;
    }

    var h = Math.floor((seconds % 31536000) / 3600);
    var m = Math.floor((((seconds % 31536000) % 86400) % 3600) / 60);
    var s = Math.floor((((seconds % 31536000) % 86400) % 3600) % 60);
    return `${pad(h)}:${pad(m)}:${pad(s)}`;
};

const incrementSecond = cardId => {
    element = $(`.total-time[data-card-id=${cardId}]`)
    time = element.attr('data-time')
    time++
    element.attr('data-time', time)
    element.text(str(time))
};

const clearIntervals = () => {
    intervals.forEach(el => { clearInterval(el) });
    intervals = [];
};

const loadBoard = () => {
    let compact = $('.board-compact.checkbox').checkbox('is checked');
    let dark = $('.board-dark.checkbox').checkbox('is checked');
    let width = $('.ui.width.slider').slider('get value');
    adjustBoardHeight();
    clearIntervals();
    getBuckets(dark, compact, width);
    enableProximityScroll();
};

const renderBuckets = (containerSelector, buckets, dark = false, compact = false, width) => {
    if (dark) {
        $('.bucket-form.modal.form').addClass('inverted');
    } else {
        $('.bucket-form.modal.form').removeClass('inverted');
    };
    $(containerSelector).empty();
    if (compact) {
        $(containerSelector).parent().css('padding', '.5em');
    } else {
        $(containerSelector).parent().css('padding', '1em');
    };
    if (dark) {
        $(containerSelector).parents().addClass('inverted');
        $(containerSelector).parents().css('background-color', 'black');
    } else {
        $(containerSelector).parents().removeClass('inverted');
        $(containerSelector).parents().css('background-color', 'white');
    };
    buckets.forEach(bucket => {
        $(containerSelector).append(
            `
            <div class="ui loading ${dark ? 'inverted ' : ' '}card bucket-el" data-bucket-id="${bucket.id}" style="width: ${width}px; flex: 0 0 auto; display: flex; flex-flow: column nowrap; overflow-y: visible; scroll-snap-align: start;${compact ? ' margin-right: .25em;' : ''}">
              <div class="center aligned handle content" style="flex: 0 0 auto; display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move; ${bucket.color !== null ? `background-color: ${dark ? bucket.color.dark : bucket.color.primary}; color: ${bucket.color.light}` : ''}; " data-bucket-id="${bucket.id}">
                <i class="grip lines icon"></i>
              </div>
              <div class="content" style="flex: 0 1 auto; ${bucket.color !== null ? `background-color: ${dark ? bucket.color.dark : bucket.color.light};` : ''};${compact ? ' padding: .5em;' : ''}">
                <div class="header" style="display: flex; flex-flow: row nowrap; justify-content: space-between;">
                  <div style="flex: 1 1 auto; overflow-wrap: anywhere; padding-right: .5em; ${bucket.color !== null ? `color: ${dark ? bucket.color.light : bucket.color.dark};` : ''}">
                    ${bucket.name}
                  </div>
                  <div style="flex: 0 0 auto;">
                    ${bucket.auto_status !== 'N' ? '<span class="ui small text" style="margin-right: .5em; opacity: .6;"><i class="robot icon"></i></span><br>' : ''}
                  </div>
                  <div class="ui basic icon top right pointing dropdown ${dark ? 'inverted ' : ' '}button" data-bucket-id="${bucket.id}" style="flex: 0 0 auto; align-self: flex-start;${compact ? ' height: 2em; padding: .5em; margin: 0;' : ''}">
                    <i class="ellipsis horizontal icon"></i>
                    <div class="menu">
                      <div class="add card item" data-bucket-id="${bucket.id}"><i class="add icon"></i>Add new card</div>
                      <div class="divider"></div>
                      <div class="edit bucket item" data-bucket-id="${bucket.id}"><i class="edit icon"></i>Edit this bucket</div>
                      <div class="delete bucket item" data-bucket-id="${bucket.id}"><i class="delete icon"></i>Delete this bucket</div>
                    </div>
                  </div>
                </div>
                <div class="meta">
                  <span style="white-space: pre-line;">${bucket.description ? bucket.description : ''}</span>
                </div>
              </div>
              <div class="extra content cards-drake" id="bucket-${bucket.id}" style="flex: 1 1 auto; display: flex; flex-flow: column nowrap; align-items: stretch; overflow-y: auto;${compact ? ' padding: .5em;' : ''}">
              </div>
            </div>
            `
        );
        document.querySelectorAll(`.handle[data-bucket-id='${bucket.id}']`)[0].addEventListener(
            'touchmove', e => {
                e.preventDefault();
                const board = document.getElementById('board');
                if (bucketsDrake.dragging && containerBucketIsOver !== null && bucketBeingDragged !== null) {
                    var threshold = 50
                    if ((e.touches[0].pageY - threshold) < containerBucketIsOver.getBoundingClientRect().top) {
                        startElementScroll(0, -1, containerBucketIsOver, 50, 100);
                    } else if ((e.touches[0].pageY + threshold) > containerBucketIsOver.getBoundingClientRect().bottom) {
                        startElementScroll(0, 1, containerBucketIsOver, 50, 100);
                    } else if ((e.touches[0].pageX + threshold) > board.getBoundingClientRect().right) {
                        startElementScroll(1, 0, board, 50, 100);
                    } else if ((e.touches[0].pageX - threshold) < board.getBoundingClientRect().left) {
                        startElementScroll(-1, 0, board, 50, 100);
                    } else {
                        stopElementScroll(scrollIntervalID);
                    }
                } else {
                    stopElementScroll(scrollIntervalID);
                };
            },
            { passive: false }
        );
        $(`.ui.dropdown[data-bucket-id=${bucket.id}]`).dropdown({ action: 'hide' });
        $(`.add.card.item[data-bucket-id=${bucket.id}]`).click(e => { showCardModal(card = null, bucket.id); });
        $(`.edit.bucket.item[data-bucket-id=${bucket.id}]`).click(e => { showBucketModal(bucket); });
        $(`.delete.bucket.item[data-bucket-id=${bucket.id}]`).click(e => { deleteBucket(bucket.id); });
        getCards(bucket.id, dark, compact);
    });
    $(containerSelector).append(`<div class="ui add bucket basic ${dark ? 'inverted ' : ' '}button" style="flex: 0 0 auto">Add new bucket</div>`);
    $(`.add.bucket.button`).click(e => { showBucketModal(); });

    e = $('.add.bucket.button').siblings().last();
    $('.add.bucket.button').css('marginTop', e.css('marginTop'));
    $('.add.bucket.button').css('marginBottom', e.css('marginBottom'));
    $('.bucket-el').removeClass('loading');
};

const renderCards = (containerSelector, cards, bucketId, dark = false, compact = false) => {
    if (dark) {
        $('.card-form.modal.form').addClass('inverted');
    } else {
        $('.card-form.modal.form').removeClass('inverted');
    };
    $(containerSelector).empty();
    cards.forEach(card => {
        $(containerSelector).append(
            `
            <div class="ui loading ${dark ? 'inverted ' : ' '}${card.is_running ? 'red ' : ''}${card.status === 'C' ? 'completed ' : ''}card card-el" data-card-id="${card.id}" style="width: 100%; flex: 0 0 auto;${compact ? ' margin-bottom: -.25em;' : 'margin-bottom: .25em;'}">
              <div class="center aligned handle content" style="flex: 0 0 auto; display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move; ${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.primary}; color: ${card.color.light}` : ''};" data-card-id="${card.id}">
                <i class="grip lines small icon"></i>
              </div>
              <div class="content" style="${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.light};` : ''};${compact ? ' padding: .5em;' : ''}">
                <div class="header" style="display: flex; flex-flow: row nowrap; justify-content: space-between; ${card.color !== null ? `color: ${dark ? card.color.light : card.color.dark};` : ''}">
                  <div style="flex: 0 1 auto; overflow-wrap: anywhere; padding-right: .5em;">
                    ${card.name}
                  </div>
                  <div class="ui basic icon top right pointing ${dark ? 'inverted ' : ' '}dropdown button" data-card-id="${card.id}" style="flex: 0 0 auto; align-self: flex-start;${compact ? ' height: 2em; padding: .5em; margin: 0;' : ''}">
                    <i class="ellipsis horizontal icon"></i>
                    <div class="menu">
                      <div class="edit card item" data-card-id="${card.id}"><i class="edit icon"></i>Edit this card</div>
                      <div class="delete card item" data-card-id="${card.id}"><i class="delete icon"></i>Delete this card</div>
                      <div class="divider"></div>
                      <div class="start-stop-timer card item" data-card-id="${card.id}"><i class="stopwatch icon"></i>Start/stop timer</div>
                    </div>
                  </div>
                </div>
                <div class="meta" style="display: flex; flex-flow: column nowrap;">
                  <div class="tags" style="flex: 0 0 auto; padding-top: .5em;" data-card-id="${card.id}">
                  </div>
                  <div class="description" style="white-space: pre-line;">${card.description ? card.description : ''}</div>
                </div>
              </div>
              <div data-card-id="${card.id}" class="extra content" style="${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.light};` : ''};;${compact ? ' padding: .5em;' : ''}">
                <span class="ui right floated ${card.is_running ? 'red ' : ''} text">
                  ${card.is_running ? '<i class="hourglass half icon"></i>' : ''}
                  <span class="total-time" data-card-id="${card.id}" data-time="${card.total_time}">
                    ${card.total_time > 0 ? str(card.total_time) : ''}
                  </span>
                </span>
              </div>
            </div>
            `
        );
        let extraContent = $(containerSelector).find(`.extra.content[data-card-id=${card.id}]`);
        let tags = $(containerSelector).find(`.meta .tags[data-card-id=${card.id}]`);
        if (card.total_items > 0) {
            extraContent.prepend(`
              <span class="ui left floated text">
                ${card.checked_items}/${card.total_items}
              </span>
            `);
        };
        if (card.tag.length > 0) {
            for (tag of card.tag) {
                if (tag.icon !== null) {
                    tags.append(`
                  <span class="ui mini ${tag.color ? tag.color.name.toLowerCase() : ''} label"><i class="${tag.icon.markup} icon"></i> ${tag.name}</span>
                `);
                } else {
                    tags.append(`
                  <span class="ui mini ${tag.color ? tag.color.name.toLowerCase() : ''} label">${tag.name}</span>
                `);
                }
            }
        };
        if (extraContent.text().trim() === '') {
            extraContent.remove();
        };
        document.querySelectorAll(`.handle[data-card-id='${card.id}']`)[0].addEventListener(
            'touchmove', e => {
                e.preventDefault();
                const board = document.getElementById('board');
                if (cardsDrake.dragging && containerCardIsOver !== null && cardBeingDragged !== null) {
                    var threshold = 50
                    if ((e.touches[0].pageY - threshold) < containerCardIsOver.getBoundingClientRect().top) {
                        startElementScroll(0, -1, containerCardIsOver, 50, 100);
                    } else if ((e.touches[0].pageY + threshold) > containerCardIsOver.getBoundingClientRect().bottom) {
                        startElementScroll(0, 1, containerCardIsOver, 50, 100);
                    } else if ((e.touches[0].pageX + threshold) > board.getBoundingClientRect().right) {
                        startElementScroll(1, 0, board, 50, 100);
                    } else if ((e.touches[0].pageX - threshold) < board.getBoundingClientRect().left) {
                        startElementScroll(-1, 0, board, 50, 100);
                    } else {
                        stopElementScroll(scrollIntervalID);
                    }
                } else {
                    stopElementScroll(scrollIntervalID);
                };
            },
            { passive: false }
        );
        $(`.ui.dropdown[data-card-id=${card.id}]`).dropdown({ action: 'hide' });
        $(`.edit.card.item[data-card-id=${card.id}]`).click(e => { showCardModal(card, bucketId); });
        $(`.delete.card.item[data-card-id=${card.id}]`).click(e => { deleteCard(card.id, bucketId); });
        $(`.start-stop-timer.card.item[data-card-id=${card.id}]`).click(e => { startStopTimer(card.id, bucketId); });
        if (card.is_running) {
            intervals.push(setInterval(() => { incrementSecond(card.id) }, 1000));
        };
    });
    $('.card-el').removeClass('loading');
};

const renderItems = (containerSelector, items, bucketId, cardId, dark = false) => {
    $(containerSelector).empty();
    items.forEach(item => {
        $(containerSelector).append(
            `
              <div class="checklist-item" data-item-id="${item.id}" style="display: flex; flex-flow: row nowrap; align-items: center;">
                <div class="ui ${dark ? 'inverted ' : ' '}fitted checkbox" style="flex: 0 0 auto;" data-item-id="${item.id}">
                  <input type="checkbox" ${item.checked ? 'checked' : ''}>
                  <label></label>
                </div>
                <div class="ui ${dark ? 'inverted ' : ' '}transparent input" style="flex: 1 0 auto;">
                  <input class="${item.checked ? 'item-checked' : ''}" data-item-id="${item.id}" type="text" placeholder="Enter text here" data-text="${item.name}" value="${item.name}">
                </div>
                <div data-item-id="${item.id}" class="ui mini icon basic delete-item ${dark ? 'inverted ' : ' '}button"><i data-item-id="${item.id}" class="trash alternate outline icon"></i></div>
              </div>
            `
        );
    });
    $('.checklist-item input').on('keypress', e => {
        if (e.which == 13) {
            let index = $(e.target).parent().parent().index() + 1;
            let nextElement = $(e.target).parent().parent().parent().children().toArray()[index]
            if (nextElement !== undefined) {
                $(nextElement).find('input[type=text]').focus();
            }
        }
    });
    $('.checklist-item input').blur(e => {
        if (e.target.value != $(e.target).attr('data-text')) {
            let itemId = $(e.target).attr('data-item-id');
            $(this).attr("disabled", "disabled");
            $.api({
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/items/${itemId}/`,
                method: 'PATCH',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    name: e.target.value,
                },
                on: 'now',
                onSuccess: r => {
                    getItems(bucketId, cardId, dark);
                },
                onComplete: () => { $(this).removeAttr("disabled"); },
            });
        };
    });
    $('.delete-item.button').click(e => {
        let itemId = $(e.target).attr('data-item-id');
        $.api({
            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/items/${itemId}/`,
            method: 'DELETE',
            headers: { 'X-CSRFToken': csrftoken },
            on: 'now',
            onSuccess: r => {
                getItems(bucketId, cardId, dark);
                itemEdited = true;
            },
        });
    });

    $('.checklist-item .checkbox').toArray().forEach(el => {
        $(el).checkbox({
            onChange: () => {
                let itemId = $(el).attr('data-item-id');
                let checked = $(el).checkbox('is checked');
                $.api({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/items/${itemId}/check/`,
                    method: 'POST',
                    data: { checked: checked },
                    headers: { 'X-CSRFToken': csrftoken },
                    on: 'now',
                    onSuccess: r => {
                        getItems(bucketId, cardId, dark);
                        itemEdited = true;
                    },
                });
            }
        })
    });
};

const enableProximityScroll = () => {
    function proximityScroll(e) {
        if (cardsDrake.dragging && containerCardIsOver !== null && cardBeingDragged !== null) {
            var boardBody = document.getElementById("board")
            var threshold = 50
            if ((e.pageY - threshold) < containerCardIsOver.getBoundingClientRect().top) {
                startElementScroll(0, -1, containerCardIsOver, 50, 100);
            } else if ((e.pageY + threshold) > containerCardIsOver.getBoundingClientRect().bottom) {
                startElementScroll(0, 1, containerCardIsOver, 50, 100);
            } else if ((e.pageX + threshold) > boardBody.getBoundingClientRect().right) {
                startElementScroll(1, 0, boardBody, 50, 100);
            } else if ((e.pageX - threshold) < boardBody.getBoundingClientRect().left) {
                startElementScroll(-1, 0, boardBody, 50, 100);
            } else {
                stopElementScroll(scrollIntervalID);
            }
        } else if (bucketsDrake.dragging && containerBucketIsOver !== null && bucketBeingDragged !== null) {
            var threshold = 50
            if ((e.pageX - threshold) < containerBucketIsOver.getBoundingClientRect().left) {
                startElementScroll(-1, 0, containerBucketIsOver, 50, 100);
            } else if ((e.pageX + threshold) > containerBucketIsOver.getBoundingClientRect().right) {
                startElementScroll(1, 0, containerBucketIsOver, 50, 100);
            } else {
                stopElementScroll(scrollIntervalID);
            }
        } else {
            stopElementScroll(scrollIntervalID);
        };
    }
    document.addEventListener("mousemove", proximityScroll);
};

const getBuckets = (dark = false, compact = false, width) => {
    $.get(`/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/`)
        .done(r => {
            renderBuckets(
                containerSelector = '#board',
                buckets = r,
                dark = dark,
                compact = compact,
                width = width
            );
        })
        .fail(e => { console.error(e) })
        .always()
};

const getCards = (bucketId, dark = false, compact = false) => {
    $.get(`/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/`)
        .done(r => {
            renderCards(
                containerSelector = `#bucket-${bucketId}`,
                cards = r,
                bucketId = bucketId,
                dark = dark,
                compact = compact
            );
        })
        .fail(e => { console.error(e) })
        .always()
};

const getItems = (bucketId, cardId, dark = false) => {
    $.get(`/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/items/`)
        .done(r => {
            renderItems(
                containerSelector = ".checklist-drake",
                items = r,
                bucketId = bucketId,
                cardId = cardId,
                dark = dark,
            );
        })
        .fail(e => { console.error(e) })
        .always()
};

const showCardModal = (card = null, bucketId) => {
    let create;
    const modal = $('.ui.card-form.modal');
    modal.form('reset');
    modal.off();
    let dark = modal.hasClass('inverted');
    if (card !== null) {
        create = false;
        modal.find('input[name=id]').val(card.id);
        modal.find('input[name=name]').val(card.name);
        modal.find('textarea[name=description]').val(card.description);
        modal.find('.ui.status.dropdown').dropdown('set selected', card.status);
        modal.find('.ui.color.dropdown').dropdown('set selected', card.color !== null ? card.color.id : '');
        modal.find('.extra.content .item').show();
        modal.find('.ui.tags.dropdown').dropdown('clear');
        for (tag of card.tag) {
            modal.find('.ui.tags.dropdown').dropdown('set selected', tag.name);
        }
        {
            getItems(bucketId, card.id, dark);
            $('.add-item.input input').off();
            $('.add-item.input input').on('keypress', e => {
                if (e.which == 13) {
                    $(this).attr("disabled", "disabled");
                    $.api({
                        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${card.id}/items/`,
                        method: 'POST',
                        headers: { 'X-CSRFToken': csrftoken },
                        data: {
                            name: e.target.value,
                            card: card.id,
                            order: 1
                        },
                        on: 'now',
                        onSuccess: r => {
                            e.target.value = '';
                            getItems(bucketId, card.id, dark);
                            itemEdited = true;
                        },
                        onComplete: () => { $(this).removeAttr("disabled"); },
                    });
                };
            });
        }
    } else {
        create = true;
        modal.find('input[name=id]').val('');
        modal.find('input[name=name]').val('');
        modal.find('textarea[name=description]').val('');
        modal.find('.ui.status.dropdown').dropdown('set selected', 'NS');
        modal.find('.ui.color.dropdown').dropdown('set selected', '');
        modal.find('.ui.tags.dropdown').dropdown('clear');
        // Prevent users from inserting checklists before card object creation
        modal.find('.extra.content .item').hide();
    };
    modal.modal({
        restoreFocus: false,
        autofocus: false,
        transition: 'scale',
        duration: 400,
        onShow: () => {
            itemEdited = false;
            if (dark) {
                $('.add-item.input').addClass('inverted');
            } else {
                $('.add-item.input').removeClass('inverted');
            };
        },
        onHidden: () => {
            if (itemEdited) { loadBoard(); };
            $('.checklist-drake').empty();
        },
        onApprove: el => {
            modal.form('validate form');
            if (!modal.form('is valid')) {
                return false;
            };
            name = modal.find('input[name=name]').val();
            description = modal.find('textarea[name=description]').val();
            status = modal.find('.ui.status.dropdown').dropdown('get value');
            color = modal.find('.ui.color.dropdown').dropdown('get value');
            tagsString = modal.find('.ui.tags.dropdown').dropdown('get value');
            tags = tagsString.split(",").map(tag => ({ name: tag }));
            if (create === true) {
                method = 'POST';
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/`;
                order = 0;
            } else {
                method = 'PUT';
                id = modal.find('input[name=id]').val();
                order = $(`.card-el[data-card-id=${card.id}]`).index() + 1;
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${id}/`;
            }
            $.ajax({
                url: url,
                type: method,
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    name: name,
                    bucket: bucketId,
                    description: description,
                    status: status,
                    color: color,
                    order: order,
                    tag: JSON.stringify(tags),
                },
                success: function (result) {
                    loadBoard();
                }
            });
        }
    }).modal('show').submit(e => {
        e.preventDefault();
        modal.find('.positive.button').click();
    });
};

const deleteCard = (cardId, bucketId) => {
    modal = $('.ui.delete.confirmation.modal')
    modal
        .modal({
            onShow: () => {
                modal.find('.header').text('Delete card');
                modal.find('.content').text(`Are you sure you want to delete card ${cardId}?`);
            },
            onApprove: () => {
                $.ajax({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}`,
                    type: 'DELETE',
                    headers: { 'X-CSRFToken': csrftoken },
                    success: function (result) {
                        loadBoard();
                    }
                });
            }
        })
        .modal('show');
};

const showBucketModal = (bucket = null) => {
    var create;
    const modal = $('.ui.bucket-form.modal');
    modal.form('reset');
    modal.off();
    if (bucket != null) {
        create = false;
        modal.find('input[name=id]').val(bucket.id);
        modal.find('input[name=name]').val(bucket.name);
        modal.find('textarea[name=description]').val(bucket.description);
        modal.find('.ui.auto-status.dropdown').dropdown('set selected', bucket.auto_status);
        modal.find('.ui.color.dropdown').dropdown('set selected', bucket.color !== null ? bucket.color.id : '');
    } else {
        create = true;
        modal.find('input[name=id]').val('');
        modal.find('input[name=name]').val('');
        modal.find('textarea[name=description]').val('');
        modal.find('.ui.auto-status.dropdown').dropdown('set selected', 'N');
        modal.find('.ui.color.dropdown').dropdown('set selected', '');
    };
    modal.modal({
        restoreFocus: false,
        autofocus: false,
        transition: 'scale',
        duration: 400,
        onApprove: el => {
            modal.form('validate form');
            if (!modal.form('is valid')) {
                return false;
            };
            name = modal.find('input[name=name]').val();
            description = modal.find('textarea[name=description]').val();
            autoStatus = modal.find('.ui.auto-status.dropdown').dropdown('get value');
            color = modal.find('.ui.color.dropdown').dropdown('get value');
            if (create === true) {
                $.ajax({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/`,
                    type: 'POST',
                    headers: { 'X-CSRFToken': csrftoken },
                    data: {
                        name: name,
                        board: BOARD_ID,
                        description: description,
                        auto_status: autoStatus,
                        color: color,
                        order: 0,
                    },
                    success: function (result) {
                        loadBoard();
                    }
                });
            } else {
                id = modal.find('input[name=id]').val();
                order = $(`.bucket-el[data-bucket-id=${bucket.id}]`).index() + 1;
                $.ajax({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${id}/`,
                    type: 'PUT',
                    headers: { 'X-CSRFToken': csrftoken },
                    data: {
                        name: name,
                        board: BOARD_ID,
                        description: description,
                        auto_status: autoStatus,
                        color: color,
                        order: order
                    },
                    success: function (result) {
                        loadBoard();
                    }
                });
            }
        }
    });
    modal.submit(e => {
        e.preventDefault();
        modal.find('.positive.button').click();
    });
    modal.modal('show');
};

const deleteBucket = (bucketId) => {
    modal = $('.ui.delete.confirmation.modal')
    modal
        .modal({
            onShow: () => {
                modal.find('.header').text('Delete bucket');
                modal.find('.content').text(`Are you sure you want to delete bucket ${bucketId}?`);
            },
            onApprove: () => {
                $.ajax({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/`,
                    type: 'DELETE',
                    headers: { 'X-CSRFToken': csrftoken },
                    success: function (result) {
                        loadBoard();
                    }
                });
            }
        })
        .modal('show');
};

const startStopTimer = (cardId, bucketId) => {
    $.ajax({
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/timer/`,
        type: 'POST',
        headers: { 'X-CSRFToken': csrftoken },
        success: function (result) {
            if (result.action == 'start') {
                $('body').toast({ message: `Timer started for card ${cardId}.` });
            } else if (result.action == 'stop') {
                $('body').toast({ message: `Timer stopped for card ${cardId}.` });
            };
            loadBoard();
        }
    });
};

