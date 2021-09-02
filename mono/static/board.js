var intervals = [];
var cardBeingDragged;
var containerCardIsOver;
var bucketBeingDragged;
var containerBucketIsOver;
var scrollIntervalID;
var isScrolling = false;
var itemEdited = false;
const PLACEHOLDER_AVATAR = '/static/image/avatar-1577909.svg';


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
            url: `/pm/api/bucket-move/`,
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
            url: `/pm/api/card-move/`,
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
            complete: () => {
                $(el).removeClass('loading');
                $('.cardlet').popup();
            }
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
        $(`.add.card.item[data-bucket-id=${bucket.id}]`).on('click', e => { showCardModal(card = null, bucket.id, compact); });
        $(`#bucket-${bucket.id}`).on('dblclick', e => { showCardModal(card = null, bucket.id, compact); })
        $(`.edit.bucket.item[data-bucket-id=${bucket.id}]`).on('click', e => { showBucketModal(bucket); });
        $(`.delete.bucket.item[data-bucket-id=${bucket.id}]`).on('click', e => { deleteBucket(bucket.id); });
        getCards(bucket.id, dark, compact);
    });
    $(containerSelector).append(`<div class="ui add bucket basic ${dark ? 'inverted ' : ' '}button" style="flex: 0 0 auto">Add new bucket</div>`);
    $(`.add.bucket.button`).off().click(e => { showBucketModal(); });
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
        switch (card.status) {
            case 'NS':
                status_icon = 'circle outline'
                break;
            case 'IP':
                status_icon = 'dot circle outline'
                break;
            case 'C':
                status_icon = 'check circle outline'
                break;
        }
        var overdue = false;
        var dueDate = null;
        if (card.due_date !== null) {
            var now = new Date();
            dueDate = card.due_date.split('-');
            dueDate = new Date(dueDate[0], dueDate[1] - 1, dueDate[2]);
            overdue = now > dueDate;
        }
        $(containerSelector).append(`
            <div class="ui loading ${dark ? 'inverted ' : ' '}${card.is_running ? 'red ' : ''}${card.status === 'C' ? 'completed ' : ''}${overdue ? 'overdue ' : ''}card card-el" data-card-id="${card.id}" style="width: 100%; flex: 0 0 auto;${compact ? ' margin-bottom: -.25em;' : 'margin-bottom: .25em;'}">
                <div class="center aligned handle content" style="flex: 0 0 auto; display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move; ${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.primary}; color: ${card.color.light}` : ''};" data-card-id="${card.id}">
                    <i class="grip lines small icon"></i>
                </div>
                <div class="content" style="${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.light};` : ''};${compact ? ' padding: .5em;' : ''}">
                    <div class="header" style="display: flex; flex-flow: row nowrap; justify-content: space-between; ${card.color !== null ? `color: ${dark ? card.color.light : card.color.dark};` : ''}">
                        <div class="" style="flex: 0 1 auto; overflow-wrap: anywhere; padding-right: .5em;">
                            <i class="card-status ${dark ? 'dark ' : ' '}${status_icon} icon" data-status="${card.status}" data-card-id="${card.id}"></i>
                            <span class="${dark ? 'dark ' : ' '}card-name" data-card-id="${card.id}" style="${card.color !== null ? `color: ${dark ? card.color.light : card.color.dark};` : ''}">${card.name}</span>
                        </div>
                        <div class="ui basic icon top right pointing ${dark ? 'inverted ' : ' '}dropdown button" data-card-id="${card.id}" style="flex: 0 0 auto; align-self: flex-start;${compact ? ' height: 1.5em; padding: .25em; margin: 0;' : ''}">
                            <i class="ellipsis horizontal icon"></i>
                            <div class="menu">
                            <div class="edit card item" data-card-id="${card.id}"><i class="edit icon"></i>Edit this card</div>
                            <div class="delete card item" data-card-id="${card.id}"><i class="delete icon"></i>Delete this card</div>
                            <div class="divider"></div>
                            <div class="start-stop-timer card item" data-card-id="${card.id}"><i class="stopwatch icon"></i>Start/stop timer</div>
                            <div class="edit-time-entries card item" data-card-id="${card.id}"><i class="history icon"></i>Edit time entries</div>
                            </div>
                        </div>
                    </div>
                    <div class="meta" style="display: flex; flex-flow: column nowrap;">
                        <div class="tags" style="flex: 0 0 auto; padding-top: .5em;" data-card-id="${card.id}"></div>
                        <div class="description" style="white-space: pre-line;">${card.description ? card.description : ''}</div>
                        <div class="assignees" style="flex: 0 0 auto; padding-top: .5em;" data-card-id="${card.id}"></div>
                    </div>
                </div>
                <div data-card-id="${card.id}" class="extra content" style="${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.light};` : ''};;${compact ? ' padding: .5em;' : ''}">
                </div>
                <div data-card-id="${card.id}" class="ui bottom attached progress" data-percent="${card.checked_items > 0 ? card.checked_items / card.total_items * 100 : 0}">
                    <div class="bar"></div>
                </div>
            </div>
        `);
        $(`.ui.progress[data-card-id=${card.id}]`).progress();
        let extraContent = $(containerSelector).find(`.extra.content[data-card-id=${card.id}]`);
        let tagsContainer = $(containerSelector).find(`.meta .tags[data-card-id=${card.id}]`);
        if (card.total_time > 0) {
            extraContent.append(`
                <span class="ui right floated ${card.is_running ? 'red ' : ''} text">
                    <a class="start-stop-timer cardlet" data-card-id="${card.id}" data-content="${card.is_running ? 'Stop timer' : 'Start timer'}" data-variation="tiny basic">
                        ${card.is_running ? '<i class="stop circle icon"></i>' : '<i class="play circle icon"></i>'}
                    </a>
                    <span class="total-time noselect cardlet" data-card-id="${card.id}" data-time="${card.total_time}" data-content="Total tracked time." data-variation="tiny basic">
                        ${str(card.total_time)}
                    </span>
                </span>
            `)
        };
        if (card.total_items > 0) {
            extraContent.prepend(`
                <span class="ui left floated text noselect cardlet" style="margin-right: 1em;" data-title="Checklist items" data-content="${card.checked_items} checked, ${card.total_items} total." data-variation="tiny basic">
                    <i class="tasks icon"></i> ${card.checked_items}/${card.total_items}
                </span>
            `);
        };
        if (card.comments > 0) {
            extraContent.prepend(`
              <span class="ui left floated text noselect cardlet" style="margin-right: 1em;" data-title="Comments" data-content="${card.comments}" data-variation="tiny basic">
                <i class="comment icon"></i> ${card.comments}
              </span>
            `);
        };
        if (card.due_date !== null) {
            extraContent.prepend(`
              <span class="ui left floated${overdue ? ' red' : ''} text noselect cardlet" style="margin-right: 1em;" data-title="Due date" data-content="${dueDate.toLocaleDateString(LANGUAGE_CODE)}${overdue ? ' - This card is overdue!' : ''}" data-variation="tiny red basic"><i class="calendar day icon"></i></span>
            `);
        };
        $('.cardlet').popup();
        if (card.tag.length > 0) {
            renderTags(tagsContainer, card.tag, dark);
        };
        let assigneesContainer = $(containerSelector).find(`.meta .assignees[data-card-id=${card.id}]`);
        if (card.assigned_to.length > 0) {
            renderAssignees(
                assigneesContainer,
                card.assigned_to,
                card.color !== null ? dark ? card.color.dark : card.color.light : null,
                dark
            );
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
        $(`.card-name[data-card-id=${card.id}]`).on('click', e => { showCardModal(card, bucketId, compact); });
        $(`.edit.card.item[data-card-id=${card.id}]`).on('click', e => { showCardModal(card, bucketId, compact); });
        $(`.delete.card.item[data-card-id=${card.id}]`).on('click', e => { deleteCard(card.id, bucketId, dark, compact); });
        $(`.start-stop-timer[data-card-id=${card.id}]`).on('click', e => { startStopTimer(card.id, bucketId, dark, compact); });
        $(`.edit-time-entries[data-card-id=${card.id}]`).on('click', e => { showTimeEntriesModal(card.id, bucketId, dark, compact); });
        $(`.card-status.icon[data-card-id=${card.id}]`).on('click', e => {
            toggleCardStatus(card.id, bucketId, $(e.target).attr('data-status'), dark, compact);
        });
        if (card.is_running) {
            intervals.push(setInterval(() => { incrementSecond(card.id) }, 1000));
        };
    });
    $('.card-el').removeClass('loading');
};

const renderItems = (containerSelector, items, bucketId, cardId, dark = false) => {
    $(containerSelector).empty();
    items.forEach(item => {
        $(containerSelector).append(`
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
        `);
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

const renderTimeEntries = (containerSelector, timeEntries, bucketId, cardId, dark = false) => {
    $(containerSelector).empty();
    if (timeEntries.length == 0) {
        $(containerSelector).append(`
            <div class="ui header">
                No time entries for this card.
            </div>
        `);
        return;
    }
    timeEntries.forEach(timeEntry => {
        $(containerSelector).append(`
            <div data-time-entry-id="${timeEntry.id}" class="ui form segment">
                <div class="field">
                    <label>Name</label>
                    <input type="text" name="name" placeholder="Name" value="${timeEntry.name}" data-time-entry-id="${timeEntry.id}">
                </div>
                <div class="two fields">
                    <div class="field">
                        <label>Started at</label>
                        <div class="ui time-entry start-date calendar" data-time-entry-id="${timeEntry.id}">
                            <div class="ui input left icon">
                                <i class="calendar icon"></i>
                                <input type="text" placeholder="Date/Time">
                            </div>
                        </div>
                    </div>
                    <div class="field">
                        <label>Stopped at</label>
                        <div class="ui time-entry stop-date calendar" data-time-entry-id="${timeEntry.id}">
                            <div class="ui input left icon">
                                <i class="calendar icon"></i>
                                <input type="text" placeholder="Date/Time">
                            </div>
                        </div>
                    </div>
                </div>
                <div style="height: 2.5em;">
                    <div class="ui left floated red icon labeled delete button" data-time-entry-id="${timeEntry.id}">
                        <i class="delete icon"></i>
                        Delete
                    </div>
                    <div class="ui right floated icon labeled primary save button" data-time-entry-id="${timeEntry.id}">
                        <i class="save icon"></i>
                        Save
                    </div>
                </div>
            </div>
        `);
        let startDate = $(`.time-entry.start-date[data-time-entry-id=${timeEntry.id}]`);
        console.log(containerSelector)
        startDate.calendar({
            popupOptions: {
                boundary: containerSelector,
                preserve: true
            },
            type: 'datetime',
            today: true,
            ampm: false,
            formatInput: true,
            formatter: {
                date: (date, settings) => {
                    if (!date) return '';
                    return date.toLocaleDateString(LANGUAGE_CODE);
                }
            }
        });
        let stopDate = $(`.time-entry.stop-date[data-time-entry-id=${timeEntry.id}]`);
        stopDate.calendar({
            popupOptions: {
                boundary: containerSelector,
                preserve: true
            },
            type: 'datetime',
            today: true,
            ampm: false,
            formatInput: true,
            formatter: {
                date: (date, settings) => {
                    if (!date) return '';
                    return date.toLocaleDateString(LANGUAGE_CODE);
                }
            }
        });

        if (timeEntry.started_at !== null) {
            let startedAt = new Date(timeEntry.started_at);
            startDate.calendar('set date', startedAt);
        }

        if (timeEntry.stopped_at !== null) {
            let stoppedAt = new Date(timeEntry.stopped_at);
            stopDate.calendar('set date', stoppedAt);
        }
        let timeEntrySegment = $(`.ui.form.segment[data-time-entry-id=${timeEntry.id}]`);
        $(`.delete.button[data-time-entry-id=${timeEntry.id}]`).click(e => {
            timeEntrySegment.addClass('loading');
            $.ajax({
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/time-entries/${timeEntry.id}/`,
                headers: { 'X-CSRFToken': csrftoken },
                method: 'DELETE',
                success: r => {
                    timeEntrySegment.remove();
                    $('body').toast({
                        class: 'warning',
                        message: `Time entry deleted!`
                    })
                },
                complete: () => {
                    timeEntrySegment.removeClass('loading');
                }
            })
        });
        $(`.save.button[data-time-entry-id=${timeEntry.id}]`).click(e => {
            timeEntrySegment.addClass('loading');
            $.ajax({
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/time-entries/${timeEntry.id}/`,
                headers: { 'X-CSRFToken': csrftoken },
                method: 'PATCH',
                data: {
                    name: $(`input[name=name][data-time-entry-id=${timeEntry.id}]`).val(),
                    started_at: startDate.calendar('get date').toISOString(),
                    stopped_at: stopDate.calendar('get date').toISOString(),
                },
                success: r => {
                    $('body').toast({
                        class: 'success',
                        message: `Time entry successfully updated!`
                    })
                },
                complete: () => {
                    timeEntrySegment.removeClass('loading');
                }
            })
        });
    });
};

const insertLinksAndMentions = (text, allowedUsers) => {
    function getIndicesOf(searchStr, str, caseSensitive) {
        var searchStrLen = searchStr.length;
        if (searchStrLen == 0) {
            return [];
        }
        var startIndex = 0, index, indices = [];
        if (!caseSensitive) {
            str = str.toLowerCase();
            searchStr = searchStr.toLowerCase();
        }
        while ((index = str.indexOf(searchStr, startIndex)) > -1) {
            indices.push(index);
            startIndex = index + searchStrLen;
        }
        return indices;
    }
    text = text.replace(
        /(https?:\/\/)([^ ]+)/g,
        '<a target="_blank" href="$&">$2</a>'
    );
    var newText = text;
    for (user of allowedUsers) {
        username = `@${user.username}`;
        usernameIndices = getIndicesOf(username, text);
        validIndices = [];
        offset = 0;
        for (index of usernameIndices) {
            nextChar = text.substr(index + username.length, 1);
            if (",.!? ".includes(nextChar)) {
                validIndices.push(index - offset);
                newText = newText.substr(0, index - offset) + newText.substr(index - offset + username.length);
                offset += username.length;
            }
        }
        offset = 0;
        for (index of validIndices) {
            avatar = user.profile.avatar !== null ? user.profile.avatar : PLACEHOLDER_AVATAR;
            span = `<span class="mention" data-html="<img class='ui avatar image' src='${avatar}'><span><b>${user.username}</b></span><p>${user.email}</p>" data-variation="tiny">@${user.username}</span>`
            newText = newText.substr(0, index + offset)
                + span
                + newText.substr(index + offset);
            offset += span.length;
        }
        text = newText;
    }
    return newText;
}

const renderComments = (containerSelector, comments, bucketId, cardId, dark = false, allowedUsers) => {
    $(containerSelector).empty();
    if (dark) {
        $(containerSelector).addClass('inverted')
        $(containerSelector).parent().addClass('inverted')
    } else {
        $(containerSelector).removeClass('inverted')
        $(containerSelector).parent().removeClass('inverted')
    }
    comments.forEach(comment => {
        text = insertLinksAndMentions(comment.text, allowedUsers);
        if (comment.created_by.username === USERNAME) {
            $(containerSelector).append(
                `
                <div class="comment">
                    <div class="avatar">
                        <img class="ui small image" src="${comment.created_by.profile.avatar != null ? comment.created_by.profile.avatar : PLACEHOLDER_AVATAR}">
                    </div>
                    <div class="content">
                        <span class="author">${comment.created_by.username}</span>
                        <div class="metadata">
                            <span class="date">${comment.created_at}</span>
                        </div>
                        <div class="text" style="white-space: pre-line;">${text}</div>
                        <div class="actions">
                            <a class="edit-comment" data-comment-id=${comment.id}>Edit</a>
                            <a class="delete-comment" data-comment-id=${comment.id}>Delete</a>
                        </div>
                    </div>
                </div>
                `
            );
            $(`a.edit-comment[data-comment-id=${comment.id}]`).off().click(e => {
                editCommentTextarea = $('textarea.comment-edit')
                $('.comment-edit.modal').modal({
                    onShow: () => {
                        editCommentTextarea.val(comment.text);
                    },
                    onApprove: () => {
                        $.ajax({
                            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/comments/${comment.id}/`,
                            method: 'PATCH',
                            data: { text: editCommentTextarea.val() },
                            headers: { 'X-CSRFToken': csrftoken },
                            success: r => {
                                editCommentTextarea.val('');
                                $('body').toast({ message: "Comment edited." });
                            },
                        })
                    },
                }).modal('show');
            });
            $(`a.delete-comment[data-comment-id=${comment.id}]`).off().click(e => {
                $(containerSelector).modal({
                    title: 'Deletion confirmation',
                    class: 'mini',
                    closeIcon: true,
                    content: 'Are you sure you want to delete this comment?',
                    actions: [
                        {
                            text: 'Cancel',
                            class: 'deny'
                        },
                        {
                            text: 'Confirm',
                            class: 'positive'
                        }
                    ],
                    onApprove: () => {
                        $.ajax({
                            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/comments/${comment.id}/`,
                            method: 'DELETE',
                            headers: { 'X-CSRFToken': csrftoken },
                            success: r => {
                                $('body').toast({ message: "Comment deleted." });
                            },
                        });
                    }
                }).modal('show');
            });
        } else {
            $(containerSelector).append(
                `
                <div class="right aligned comment" style="display: flex; flex-flow: row nowrap; align-items: start;">
                    <div class="content" style="flex: 1 1 auto; margin-right: 1em;">
                        <div class="metadata">
                            <span class="date">${comment.created_at}</span>
                        </div>
                        <span class="author" style="margin-left: .5em;">${comment.created_by.username}</span>
                        <div class="text" style="white-space: pre-line;">${text}</div>
                    </div>
                    <div class=" avatar" style="flex: 0 0 auto;">
                        <img class="ui small image" src="${comment.created_by.profile.avatar != null ? comment.created_by.profile.avatar : PLACEHOLDER_AVATAR}">
                    </div>
                </div>
                `
            );
        };
        $(`.mention`).popup();
    });
};

const renderTags = (container, tags, dark = false) => {
    for (tag of tags) {
        if (tag.icon !== null) {
            container.append(`
                <span class="ui mini ${tag.color ? tag.color.name.toLowerCase() : ''} label"><i class="${tag.icon.markup} icon"></i> ${tag.name}</span>
            `);
        } else {
            container.append(`
                <span class="ui mini ${tag.color ? tag.color.name.toLowerCase() : ''} label">${tag.name}</span>
            `);
        }
    }
};

const renderAssignees = (container, assignees, borderColor = null, dark = false) => {
    if (borderColor === null) {
        for (user of assignees) {
            container.append(`
                <img data-username="${user.username}" data-content="${user.username}" data-variation="basic" class="ui avatar mini image assignee${dark ? ' dark' : ''}" src="${user.profile.avatar === null ? PLACEHOLDER_AVATAR : user.profile.avatar}"">
            `);
            $(`img[data-username='${user.username}']`).popup();
        }
    } else {
        for (user of assignees) {
            container.append(`
                <img data-username="${user.username}" data-content="${user.username}" data-variation="basic" class="ui avatar mini image assignee${dark ? ' dark' : ''}" src="${user.profile.avatar === null ? PLACEHOLDER_AVATAR : user.profile.avatar}" style="border-color: ${borderColor};">
            `);
            $(`img[data-username='${user.username}']`).popup();
        }
    }
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

const getComments = (bucketId, cardId, dark = false, allowedUsers) => {
    $.get(`/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/comments/`)
        .done(r => {
            renderComments(
                containerSelector = "#card-comments",
                items = r,
                bucketId = bucketId,
                cardId = cardId,
                dark = dark,
                allowedUsers = allowedUsers,
            );
        })
        .fail(e => { console.error(e) })
        .always()
};

const getTimeEntries = (bucketId, cardId, dark = false) => {
    $.get(`/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/time-entries/`)
        .done(r => {
            renderTimeEntries(
                containerSelector = "#time-entries .content",
                timeEntryes = r,
                bucketId = bucketId,
                cardId = cardId,
                dark = dark,
            );
        })
        .fail(e => { console.error(e) })
        .always()
};

const getTags = () => {
    var tags = [];
    $.ajax({
        on: 'now',
        async: false,
        throttleFirstRequest: false,
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/`,
        method: 'GET',
        cache: false,
        loadingDuration: 500,
    })
        .done(r => { tags = r; })
    return tags;
}

const initializeTagsDropdown = dropdown => {
    var tags = getTags().map(tag => {
        if (tag.icon === null) {
            return {
                value: tag.name,
                name: `
                    <div class="ui ${tag.color === null ? '' : tag.color.name.toLowerCase()} label"  data-value="${tag.name}">
                        <span class="ui text">${tag.name}</span>
                    </div>
                `,
            }
        } else {
            return {
                value: tag.name,
                name: `
                    <div class="ui ${tag.color === null ? '' : tag.color.name.toLowerCase()} label" data-value="${tag.name}">
                        <i class="${tag.icon.markup} icon"></i><span class="ui text">${tag.name}</span>
                    </div>
                `,
            }
        }
    });
    dropdown.dropdown('refresh').dropdown({
        placeholder: 'Select tags to this card',
        values: tags,
        clearable: true,
        allowAdditions: false,
        forceSelection: false,
        onLabelCreate: (value, text) => {
            var el = $(text);
            el.append('<i class="delete icon"></i>')
            return el;
        },
    });
}

const getBoardAllowedUsers = () => {
    var allowed_users = [];
    $.ajax({
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/`,
        method: 'GET',
        headers: { 'X-CSRFToken': csrftoken },
        async: false,
    })
        .done(r => { allowed_users = r.allowed_users; })
    return allowed_users;
}

const showCardModal = (card = null, bucketId, compact) => {
    let create;
    const modal = $('.ui.card-form.modal');
    modal.off().form('reset');
    let dark = modal.hasClass('inverted');
    if (dark) {
        modal.find('.checklist.segment').addClass('inverted');
        modal.find('.add-item.input').addClass('inverted');
        modal.find('.add-item.input').addClass('inverted');
        modal.find('.ui.dividing.header').addClass('inverted');
    } else {
        modal.find('.checklist.segment').removeClass('inverted');
        modal.find('.add-item.input').removeClass('inverted');
        modal.find('.ui.dividing.header').removeClass('inverted');
    };
    initializeTagsDropdown(modal.find('.ui.tags.dropdown'));
    modal.find('.manage-tags').off().on('click', e => {
        selectedTags = modal.find('.ui.tags.dropdown').dropdown('get value').split(',');
        showManageTagsModal(
            true,
            true,
            () => {
                initializeTagsDropdown(modal.find('.ui.tags.dropdown'));
                modal.find('.ui.tags.dropdown').dropdown('set exactly', selectedTags);
            },
        );
    });
    if (card !== null) {
        create = false;
        modal.find('input[name=id]').val(card.id);
        modal.find('input[name=name]').val(card.name);
        modal.find('textarea[name=description]').val(card.description);
        modal.find('.ui.status.dropdown').dropdown('set selected', card.status);
        modal.find('.ui.card-color.dropdown').dropdown('set selected', card.color !== null ? card.color.id : '');
        modal.find('.extra.content .item').show();
        modal.find('.comments-segment.segment').show();
        modal.find('.ui.card-due-date.calendar').calendar('set date', card.due_date);
        modal.find('.ui.tags.dropdown').dropdown('clear');
        modal.find('.ui.assigned_to.dropdown').parent().show();
        modal.find('#suggest-comment').val('');
        new Suggest.LocalMulti(
            "suggest-comment",
            "suggest",
            card.allowed_users.map(user => `@${user.username}`),
            {
                dispAllKey: true,
                prefix: true,
                highlight: true,
            }
        );
        allowed_users = card.allowed_users.map(user => (
            {
                value: user.username,
                name: user.username,
                image: user.profile.avatar !== null ? user.profile.avatar : PLACEHOLDER_AVATAR,
                imageClass: 'ui allowed_users avatar image',
            }
        ));
        {
            getItems(bucketId, card.id, dark);
            $('.add-item.input input').off().on('keypress', e => {
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
        {
            getComments(bucketId, card.id, dark, card.allowed_users);
            $('.add-reply.button').off().click(e => {
                $(this).attr("disabled", "disabled");
                $.api({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${card.id}/comments/`,
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrftoken },
                    data: {
                        card: card.id,
                        text: $('textarea.add-reply').val(),
                    },
                    on: 'now',
                    onSuccess: r => {
                        $('textarea.add-reply').val('');
                        getComments(bucketId, card.id, dark, card.allowed_users);
                        itemEdited = true;
                    },
                    onComplete: () => { $(this).removeAttr("disabled"); },
                });
            });
        }
    } else {
        create = true;
        modal.find('input[name=id]').val('');
        modal.find('input[name=name]').val('');
        modal.find('textarea[name=description]').val('');
        modal.find('.ui.status.dropdown').dropdown('set selected', 'NS');
        modal.find('.ui.card-color.dropdown').dropdown('set selected', '');
        // Prevent users from inserting checklists or comments before card object creation
        modal.find('.extra.content .item').hide();
        modal.find('.comments-segment.segment').hide();
        modal.find('.ui.tags.dropdown').dropdown('clear');
        modal.find('.ui.assigned_to.dropdown').dropdown('clear');
        modal.find('.ui.card-due-date.calendar').calendar('clear');
        allowed_users = getBoardAllowedUsers().map(user => (
            {
                value: user.username,
                name: user.username,
                image: user.profile.avatar !== null ? user.profile.avatar : PLACEHOLDER_AVATAR,
                imageClass: 'ui allowed_users avatar image',
            }
        ));
    };
    modal.find('.ui.assigned_to.dropdown').dropdown({
        placeholder: 'Assign users to this card',
        values: allowed_users
    });

    modal.modal({
        restoreFocus: false,
        autofocus: false,
        transition: 'scale',
        duration: 400,
        onShow: () => {
            itemEdited = false;
            modal.find('.manage-tags').popup();
            modal.find('.scrolling.content').animate({ scrollTop: 0 });
            modal.find('.ui.card-due-date.calendar').calendar({
                type: 'date',
                today: true,
                formatInput: true,
                formatter: {
                    date: (date, settings) => {
                        if (!date) return '';
                        return date.toLocaleDateString(LANGUAGE_CODE);
                    }
                }
            });
            if (card !== null) {
                modal.find('.ui.assigned_to.dropdown').dropdown('set exactly', card.assigned_to.map(user => user.username));
                modal.find('.ui.tags.dropdown').dropdown('set exactly', card.tag.map(tag => tag.name));
            }
        },
        onHidden: () => {
            if (itemEdited) { getCards(bucketId, dark, compact); };
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
            color = modal.find('.ui.card-color.dropdown').dropdown('get value');
            tagsString = modal.find('.ui.tags.dropdown').dropdown('get value');
            tags = tagsString.split(",").map(tag => ({ name: tag }));
            assigneesString = modal.find('.ui.assigned_to.dropdown').dropdown('get value');
            assignees = assigneesString.split(",").map(username => ({ username: username }));
            dueDate = modal.find('.ui.card-due-date.calendar').calendar('get date'); // If not null, dueDate is a Date object
            if (dueDate !== null) { dueDate.toISOString().split("T")[0] } // Convert to string in correct format
            if (create) {
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
                    due_date: dueDate,
                    tag: JSON.stringify(tags),
                    assigned_to: JSON.stringify(assignees),
                },
                success: function (result) {
                    getCards(bucketId, dark, compact);
                }
            });
        }
    }).modal('show').submit(e => {
        e.preventDefault();
        modal.find('.positive.button').click();
    });
};

const deleteCard = (cardId, bucketId, dark, compact) => {
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
                        getCards(bucketId, dark, compact);
                    }
                });
            }
        })
        .modal('show');
};

const toggleCardStatus = (cardId, bucketId, currentStatus, dark, compact) => {
    switch (currentStatus) {
        case 'NS':
            status = 'IP';
            status_name = 'In Progress';
            status_icon = 'dot circle outline';
            break;
        case 'IP':
            status = 'C';
            status_name = 'Completed';
            status_icon = 'check circle outline';
            break;
        case 'C':
            status = 'NS';
            status_name = 'Not Started';
            status_icon = 'circle outline';
            break;
    }
    $.ajax({
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/`,
        type: 'PATCH',
        headers: { 'X-CSRFToken': csrftoken },
        data: { status: status },
    })
        .done(r => {
            $('body').toast({
                title: 'Card status changed',
                message: `Card was marked as <strong>${status_name}<i class="${status_icon} icon"></i></strong>`,
                showProgress: 'bottom'
            });
            getCards(bucketId, dark, compact)
        })
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
        modal.find('.ui.color.dropdown').dropdown('clear');
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

const showTimeEntriesModal = (cardId, bucketId, dark, compact) => {
    const modal = $('#time-entries.modal');
    modal.modal({
        autofocus: false,
        onShow: () => {
            modal.addClass('loading');
            getTimeEntries(bucketId, cardId, dark);
        },
        onVisible: () => {
            modal.removeClass('loading');
        },
        onHidden: () => {
            getCards(bucketId, dark, compact);
            modal.find('.content').empty();
        },
    }).modal('show');
}

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

const startStopTimer = (cardId, bucketId, dark, compact) => {
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
            getCards(bucketId, dark, compact);
        }
    });
};

const addNewTagInput = (containerElement) => {
    el = containerElement.append(`
      <form class="ui unstackable form" data-tag-id="" style="width: 100%; margin-bottom: .5em;">
        <div class="" style="display: flex; flex-flow: row nowrap;">
          <input type="hidden" name="id" value="">
          <div style="flex: 0 0 auto; width: 5.5em; display: flex; margin-right: .5em;">
            <select class="ui tag-icon new-tag clearable compact dropdown" data-tag-id="">
            </select>
          </div>
          <div style="flex: 0 0 auto; width: 5.5em; display: flex; margin-right: .5em;">
            <select class="ui tag-color new-tag clearable compact dropdown" data-tag-id="">
            </select>
          </div>
          <div style="flex: 1 1 auto; margin-right: .5em;">
            <input class="tag-name" type="text" placeholder="Name" data-tag-id="">
          </div>
          <div style="">
            <div class="ui icon red delete new-tag button"><i class="delete icon"></i></div>
          </div>
        </div>
      </form>
    `);
    let iconDropdown = $(`.tag-icon.new-tag.dropdown`);
    iconDropdown.dropdown({ values: ICON_VALUES });
    let colorDropdown = $(`.tag-color.new-tag.dropdown`);
    colorDropdown.dropdown({ values: COLOR_VALUES });
    el.find('.delete.button.new-tag').off();
    el.find('.delete.button.new-tag').click(e => {
        $(e.target).closest('form').remove();
    })
}

const renderTagForms = (containerElement, tag) => {
    containerElement.append(`
      <form class="ui unstackable form" data-tag-id="${tag.id}" style="width: 100%; margin-bottom: .5em;">
        <div class="" style="display: flex; flex-flow: row nowrap;">
          <input type="hidden" name="id" value="${tag.id}">
          <div style="flex: 0 0 auto; width: 6em; display: flex; margin-right: .5em;">
            <select class="ui tag-icon clearable compact two column mini dropdown" data-tag-id="${tag.id}">
            </select>
          </div>
          <div style="flex: 0 0 auto; width: 6em; display: flex; margin-right: .5em;">
            <select class="ui tag-color clearable compact two column mini dropdown" data-tag-id="${tag.id}">
            </select>
          </div>
          <div style="flex: 1 1 auto; margin-right: .5em;" class="ui mini input">
            <input class="tag-name" type="text" placeholder="Name" data-tag-id="${tag.id}">
          </div>
          <div style="">
            <div class="ui icon red delete mini button" data-content="Delete tag" data-tag-id="${tag.id}"><i class="delete icon"></i></div>
          </div>
        </div>
      </form>
    `);
    $(`.delete.button[data-tag-id=${tag.id}]`).popup();
    let iconDropdown = $(`.tag-icon.dropdown[data-tag-id=${tag.id}]`);
    iconDropdown.dropdown({
        placeholder: 'Icon',
        values: ICON_VALUES,
        context: '.tags.modal .content'
    });
    if (tag.icon !== null) {
        iconDropdown.dropdown('set selected', tag.icon.id);
    };
    let colorDropdown = $(`.tag-color.dropdown[data-tag-id=${tag.id}]`);
    colorDropdown.dropdown({
        placeholder: 'Color',
        values: COLOR_VALUES,
        context: '.tags.modal .content',
    });
    if (tag.color !== null) {
        colorDropdown.dropdown('set selected', tag.color.id);
    };
    $(`input[type=text][data-tag-id=${tag.id}]`).val(tag.name);
    $(`.delete.button[data-tag-id=${tag.id}]`).click(() => {
        $('body').modal({
            title: 'Deletion confirmation',
            class: 'mini',
            closeIcon: true,
            content: `Are you sure yo want to delete tag ${tag.name}?`,
            allowMultiple: true,
            actions: [
                {
                    text: 'Yes',
                    class: 'positive'
                },
                {
                    text: 'Cancel',
                    class: 'deny'
                },
            ],
            onApprove: () => {
                $.ajax({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/${tag.id}`,
                    method: 'DELETE',
                    headers: { 'X-CSRFToken': csrftoken },
                }).done(r => {
                    $(`form[data-tag-id=${tag.id}]`).remove();
                    loadBoard();
                })
            }
        }).modal('show');
    })
};

const showManageTagsModal = (allowMultiple = false, fromCardModal = false, callback = undefined) => {
    $('.ui.sidebar').sidebar('hide');
    let tagsModal = $('.ui.tags.modal');
    tagsModal.modal({
        autofocus: false,
        allowMultiple: allowMultiple,
        onShow: () => {
            el = tagsModal.find('.content');
            el.empty();
            el.append(`
                <div class="ui new-tag icon labeled green button" style="margin-bottom: 1em;">
                    <i class="add icon"></i>
                    Add new tag
                </div>
            `)
            el.find('.new-tag').click(() => {
                addNewTagInput(el);
            })
            $.get(`/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/`)
                .done(r => {
                    for (tag of r) {
                        renderTagForms(el, tag);
                    };
                })
                .fail(e => { console.error(e) })
                .always(() => { })
        },
        onApprove: () => {
            el.find('.ui.form').each((index, form) => {
                var id = $(form).find('input[name=id]').val();
                var icon = $(form).find('.tag-icon').dropdown('get value');
                var color = $(form).find('.tag-color').dropdown('get value');
                var name = $(form).find('.tag-name').val();
                if (id == '') {
                    $.ajax({
                        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/`,
                        method: 'POST',
                        headers: { 'X-CSRFToken': csrftoken },
                        data: {
                            icon: icon,
                            color: color,
                            name: name,
                        }
                    })
                } else {
                    $.ajax({
                        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/${id}/`,
                        method: 'PUT',
                        headers: { 'X-CSRFToken': csrftoken },
                        data: {
                            icon: icon,
                            color: color,
                            name: name,
                        }
                    })
                }
            });
            if (fromCardModal) {
                callback();
            }
            loadBoard();
        },
    });
    tagsModal.modal('show');
}