var intervals = [];
var cardBeingDragged;
var containerCardIsOver;
var bucketBeingDragged;
var containerBucketIsOver;
var scrollIntervalID;
var isScrolling = false;
var cardEdited = false;
var boardTimestamp = new Date();
var autoRefresh = null;
const PLACEHOLDER_AVATAR = '/static/image/avatar-1577909.svg';
const allowedUsers = getBoardAllowedUsers();

var cardsDrake = dragula({
    isContainer: el => $(el).hasClass('cards-drake') && $(el).attr('data-day') !== '',
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
        if ($(target).hasClass('no-due-date')) {
            data = {
                due_date: null,
            }
        } else {
            day = $(target).attr('data-day');
            date = $('#month_year_calendar').calendar('get date');
            dueDate = new Date(date.getFullYear(), date.getMonth(), day);
            console.log(date);
            data = {
                due_date: dueDate.toISOString().split("T")[0],
            }
        }
        card = $(el).attr('data-card-id');
        bucket = $(el).attr('data-bucket-id');
        $.api({
            on: 'now',
            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucket}/cards/${card}/`,
            method: 'PATCH',
            stateContext: `.card-el[data-card-id=${card}]`,
            data: data,
            onSuccess: r => {
                status_changed = r.status_changed;
                timer_action = r.timer_action;
                if (status_changed || timer_action != 'none') {
                    loadBoard();
                };
            },
            onComplete: () => {
                $(el).removeClass('loading');
            }
        });
    })
    .on('drag', (el, source) => {
        cardBeingDragged = el;
    })
    .on('dragend', (el) => {
        cardBeingDragged = null;
    })
    .on('over', (el, container, source) => {
        containerCardIsOver = container;
    })
    .on('out', (el, container, source) => {
        containerCardIsOver = null;
    });

async function setWallpaper() {
    if (wallpaper) {
        $('#board').css('background-image', `url('${wallpaper}')`);
    } else {
        $('#board').css('background-image', '');
    }
}

async function setCardGlassEffect(blur = false, blurness = 5, opacity = 50) {
    if (wallpaper) {
        for (el of $('.card-el')) {
            color = $(el).css('background-color');
            if (color.split('(')[0] === 'rgb') {
                newColor = `${color.replace('rgb(', '').replace(')', '')}, ${opacity / 100}`;
                $(el).css('background-color', `rgba(${newColor})`);
                if (blur) {
                    $(el).css('backdrop-filter', `blur(${blurness}px)`);
                }
            }
        }
    }
}

function str(seconds) {
    function pad(num, size = 2) {
        num = num.toString();
        while (num.length < size) num = "0" + num;
        return num;
    }
    var h = Math.floor((seconds % 31536000) / 3600);
    var m = Math.floor((((seconds % 31536000) % 86400) % 3600) / 60);
    var s = Math.floor((((seconds % 31536000) % 86400) % 3600) % 60);
    return `${pad(h)}:${pad(m)}:${pad(s)}`;
}

function loadBoard() {
    boardTimestamp = new Date();
    getCardsNoDueDate();
    // setWallpaper();
}


async function renderCards(containerSelector, cards, dark = false, compact = true) {
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
            <div class="ui loading ${dark ? 'inverted ' : ' '}${card.is_running ? 'red ' : ''}${card.status === 'C' ? 'completed ' : ''}${overdue ? 'overdue ' : ''}card card-el" data-card-id="${card.id}" data-bucket-id="${card.bucket}" style="flex: 0 0 auto;${compact ? ' margin-bottom: -.25em;' : 'margin-bottom: .25em;'}">
                <div class="center aligned handle content" style="flex: 0 0 auto; display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move; ${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.primary}; color: ${card.color.light}` : ''};" data-card-id="${card.id}">
                    <i class="grip lines small icon"></i>
                </div>
                <div class="content" style="${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.light};` : ''};${compact ? ' padding: .5em;' : ''}">
                    <div class="header" style="display: flex; flex-flow: row nowrap; justify-content: space-between; ${card.color !== null ? `color: ${dark ? card.color.light : card.color.dark};` : ''}">
                        <div class="" style="flex: 0 1 auto; overflow-wrap: anywhere; padding-right: .5em;">
                            <i class="card-status ${dark ? 'dark ' : ' '}${status_icon} icon" data-status="${card.status}" data-card-id="${card.id}"></i>
                            <span class="${dark ? 'dark ' : ' '}card-name" data-card-id="${card.id}" style="${card.color !== null ? `color: ${dark ? card.color.light : card.color.dark};` : ''}">${card.name}</span>
                        </div>
                    </div>
                </div>
                <div data-card-id="${card.id}" class="ui bottom attached progress" data-percent="${card.checked_items > 0 ? card.checked_items / card.total_items * 100 : 0}">
                    <div class="bar"></div>
                </div>
            </div>
        `);
        $(`.ui.progress[data-card-id=${card.id}]`).progress();
        let assigneesContainer = $(containerSelector).find(`.meta .assignees[data-card-id=${card.id}]`);
        if (card.assigned_to.length > 0) {
            renderAssignees(
                assigneesContainer,
                card.assigned_to,
                card.color !== null ? dark ? card.color.dark : card.color.light : null,
                dark
            );
        };
        $(`.card-name[data-card-id=${card.id}]`).on('click', e => { showCardModal(card, card.bucket, compact); });
        $(`.card-el[data-card-id=${card.id}]`).on('dblclick', e => { showCardModal(card, card.bucket, compact); })
        $(`.card-status.icon[data-card-id=${card.id}]`).on('click', e => {
            toggleCardStatus(card.id, card.bucket, $(e.target).attr('data-status'), dark, compact);
        });
    });
    $('.card-el').removeClass('loading');
    setCardGlassEffect();
}

async function renderFiles(modal, bucketId, cardId, files) {
    for (f of files) {
        extension = f.extension;
        modal.find('.files-container').append(`
            <div class="ui special card img-card-file" data-file-id=${f.id}>
                <div class="blurring dimmable image" data-file-id=${f.id}>
                    <div class="ui dimmer">
                        <div class="content">
                            <div class="center">
                                <a href="${f.file}" target="_blank" class="ui inverted button">${gettext('Open')}</a>
                            </div>
                            <div class="center" style="margin-top: 1em;">
                                <a class="delete-file" data-file-id=${f.id}><i class="trash icon"></i>${gettext('Remove')}</a>
                            </div>
                        </div>
                    </div>
                    <img src="${f.image ? f.file : generateAvatar(extension)}" class="img-card-file">
                </div>
            </div>
        `);
        $(`.image[data-file-id=${f.id}]`).dimmer({ on: 'hover' });
        $(`.delete-file[data-file-id=${f.id}]`).off().on('click', e => {

            id = $(e.target).attr('data-file-id');
            $('body').modal({
                title: gettext('Confirmation'),
                class: 'mini',
                closeIcon: true,
                content: gettext('Delete this file?'),
                actions: [
                    {
                        text: gettext('Cancel'),
                        class: 'deny black'
                    },
                    {
                        text: gettext('Yes, delete it'),
                        class: 'approve red',
                        icon: 'delete',
                    },
                ],
                onApprove: () => {
                    $.api({
                        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/files/${id}/`,
                        on: 'now',
                        stateContext: $(`.ui.special.card.img-card-file[data-file-id=${id}]`),
                        method: 'DELETE',
                        successTest: r => r != 0,
                        onSuccess: r => {
                            $(`.ui.special.card.img-card-file[data-file-id=${id}]`).remove();
                            cardEdited = true;
                        },
                    })
                }
            }).modal('show');
        });
    }
}

function renderItems(containerSelector, items, bucketId, cardId, dark = false) {
    $(containerSelector).empty();
    items.forEach(item => {
        $(containerSelector).append(`
            <div class="checklist-item" data-item-id="${item.id}" style="display: flex; flex-flow: row nowrap; align-items: center;">
                <div class="ui ${dark ? 'inverted ' : ' '}fitted checkbox" style="flex: 0 0 auto;" data-item-id="${item.id}">
                    <input type="checkbox" ${item.checked ? 'checked' : ''}>
                    <label></label>
                </div>
                <div class="ui ${dark ? 'inverted ' : ' '}transparent input" style="flex: 1 0 auto;">
                    <input class="${item.checked ? 'item-checked' : ''}" data-item-id="${item.id}" type="text" placeholder="${gettext('Enter text here')}" data-text="${item.name}" value="${item.name}">
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
            on: 'now',
            onSuccess: r => {
                getItems(bucketId, cardId, dark);
                cardEdited = true;
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
                    on: 'now',
                    onSuccess: r => {
                        getItems(bucketId, cardId, dark);
                        cardEdited = true;
                    },
                });
            }
        })
    });
}

function renderTimeEntries(containerSelector, timeEntries, bucketId, cardId, dark = false) {
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
                    <label>${gettext('Name')}</label>
                    <input type="text" name="name" placeholder="${gettext('Name')}" value="${timeEntry.name}" data-time-entry-id="${timeEntry.id}">
                </div>
                <div class="two fields">
                    <div class="field">
                        <label>${gettext('Started at')}</label>
                        <div class="ui time-entry start-date calendar" data-time-entry-id="${timeEntry.id}">
                            <div class="ui input left icon">
                                <i class="calendar icon"></i>
                                <input type="text" placeholder="${gettext('Date/Time')}">
                            </div>
                        </div>
                    </div>
                    <div class="field">
                        <label>${gettext('Stopped at')}</label>
                        <div class="ui time-entry stop-date calendar" data-time-entry-id="${timeEntry.id}">
                            <div class="ui input left icon">
                                <i class="calendar icon"></i>
                                <input type="text" placeholder="${gettext('Date/Time')}">
                            </div>
                        </div>
                    </div>
                </div>
                <div style="height: 2.5em;">
                    <div class="ui left floated red icon labeled delete button" data-time-entry-id="${timeEntry.id}">
                        <i class="delete icon"></i>
                        ${gettext('Delete')}
                    </div>
                    <div class="ui right floated icon labeled primary save button" data-time-entry-id="${timeEntry.id}">
                        <i class="save icon"></i>
                        ${gettext('Save')}
                    </div>
                </div>
            </div>
        `);
        let startDate = $(`.time-entry.start-date[data-time-entry-id=${timeEntry.id}]`);
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
                method: 'DELETE',
                success: r => {
                    timeEntrySegment.remove();
                    $('body').toast({
                        class: 'warning',
                        message: gettext('Time entry deleted!')
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
                method: 'PATCH',
                data: {
                    name: $(`input[name=name][data-time-entry-id=${timeEntry.id}]`).val(),
                    started_at: startDate.calendar('get date').toISOString(),
                    stopped_at: stopDate.calendar('get date').toISOString(),
                },
                success: r => {
                    $('body').toast({
                        class: 'success',
                        message: gettext('Time entry successfully updated!')
                    })
                },
                complete: () => {
                    timeEntrySegment.removeClass('loading');
                }
            })
        });
    });
}

function renderComments(containerSelector, comments, bucketId, cardId, dark = false) {
    $(containerSelector).empty();
    if (dark) {
        $(containerSelector).addClass('inverted')
        $(containerSelector).parent().addClass('inverted')
    } else {
        $(containerSelector).removeClass('inverted')
        $(containerSelector).parent().removeClass('inverted')
    }
    comments.forEach(comment => {
        text = insertLinksAndMentions(comment.text);
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
                            <a class="edit-comment" data-comment-id=${comment.id}>${gettext('Edit')}</a>
                            <a class="delete-comment" data-comment-id=${comment.id}>${gettext('Delete')}</a>
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
                            success: r => {
                                editCommentTextarea.val('');
                                $('body').toast({ message: gettext("Comment edited.") });
                            },
                        })
                    },
                }).modal('show');
            });
            $(`a.delete-comment[data-comment-id=${comment.id}]`).off().click(e => {
                $(containerSelector).modal({
                    title: gettext('Deletion confirmation'),
                    class: 'mini',
                    closeIcon: true,
                    content: gettext('Are you sure you want to delete this comment?'),
                    actions: [
                        {
                            text: gettext('Cancel'),
                            class: 'deny'
                        },
                        {
                            text: gettext('Confirm'),
                            class: 'positive'
                        }
                    ],
                    onApprove: () => {
                        $.ajax({
                            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/comments/${comment.id}/`,
                            method: 'DELETE',
                            success: r => {
                                $('body').toast({ message: gettext("Comment deleted.") });
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
}

async function renderTags(container, tags, dark = false) {
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
}

async function renderAssignees(container, assignees, borderColor = null, dark = false) {
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
}

async function loadComments(card, bucketId, dark) {
    getComments(bucketId, card.id, dark);
    $('.add-reply.button').off().click(e => {
        $(this).attr("disabled", "disabled");
        $.api({
            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${card.id}/comments/`,
            method: 'POST',
            data: {
                card: card.id,
                text: $('textarea.add-reply').val(),
            },
            on: 'now',
            onSuccess: r => {
                $('textarea.add-reply').val('');
                getComments(bucketId, card.id, dark);
                cardEdited = true;
            },
            onComplete: () => { $(this).removeAttr("disabled"); },
        });
    });
}

async function loadChecklistItems(card, bucketId, dark) {
    getItems(bucketId, card.id, dark);
    $('.add-item.input input').off().on('keypress', e => {
        if (e.which == 13) {
            $(this).attr("disabled", "disabled");
            $.api({
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${card.id}/items/`,
                method: 'POST',
                data: {
                    name: e.target.value,
                    card: card.id,
                    order: 1
                },
                on: 'now',
                onSuccess: r => {
                    e.target.value = '';
                    getItems(bucketId, card.id, dark);
                    cardEdited = true;
                },
                onComplete: () => { $(this).removeAttr("disabled"); },
            });
        };
    });
}

function insertLinksAndMentions(text) {
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

async function enableProximityScroll() {
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
}


async function getItems(bucketId, cardId, dark = false) {
    $.api({
        on: 'now',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/items/`,
        method: 'GET',
        stateContext: '.checklist.segment',
        onSuccess: r => {
            renderItems(
                containerSelector = ".checklist-drake",
                items = r,
                bucketId = bucketId,
                cardId = cardId,
                dark = dark,
            );
        }
    })
}

async function getComments(bucketId, cardId, dark = false) {
    $.api({
        on: 'now',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/comments/`,
        method: 'GET',
        stateContext: '.comments-segment.segment',
        onSuccess: r => {
            renderComments(
                containerSelector = "#card-comments",
                items = r,
                bucketId = bucketId,
                cardId = cardId,
                dark = dark,
            );
        },
    })
}

function getTimeEntries(bucketId, cardId, dark = false) {
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
}

function getTags() {
    var tags = [];
    $.ajax({
        on: 'now',
        async: false,
        throttleFirstRequest: false,
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/`,
        method: 'GET',
        cache: false,
    })
        .done(r => { tags = r; })
    return tags;
}

function getBoardAllowedUsers() {
    var allowed_users = [];
    $.ajax({
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/`,
        method: 'GET',
        async: false,
    })
        .done(r => { allowed_users = r.allowed_users; })
    return allowed_users;
}

async function getFiles(modal, bucketId, cardId) {
    $.api({
        on: 'now',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/files/`,
        stateContext: '.files.segment',
        onSuccess: r => {
            renderFiles(modal, bucketId, cardId, files = r)
        }
    })
}

function generateAvatar(text, foregroundColor = "white", backgroundColor = "black") {
    const w = 200;
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    canvas.width = w;
    canvas.height = w;

    // Draw background
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw text
    var fontsize = w * 2 / text.length;
    do {
        fontsize -= w / 100;
        ctx.font = `bold ${fontsize}px Inter`;
    } while (ctx.measureText(text).width > w * .8)
    ctx.fillStyle = foregroundColor;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);


    return canvas.toDataURL("image/png");
}

async function initializeTagsDropdown(dropdown, card = undefined) {
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
        placeholder: gettext('Select tags to for card'),
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
    if (card) {
        dropdown.dropdown('set exactly', card.tag.map(tag => tag.name));
    }
}

async function initializeUsersDropdown(dropdown, card = undefined) {
    dropdown.dropdown({
        placeholder: gettext('Assign users to this card'),
        values: allowedUsers.map(user => (
            {
                value: user.username,
                name: user.username,
                image: user.profile.avatar !== null ? user.profile.avatar : PLACEHOLDER_AVATAR,
                imageClass: 'ui allowed_users avatar image',
            }
        ))
    });
    if (card) {
        dropdown.dropdown('set exactly', card.assigned_to.map(user => user.username));
    }
}

async function initializeSuggest() {
    new Suggest.LocalMulti(
        "suggest-comment",
        "suggest",
        allowedUsers.map(user => `@${user.username}`),
        {
            dispAllKey: true,
            prefix: true,
            highlight: true,
        }
    );
}

async function clearModal(modal) {
    modal.find('input[name=id]').val('');
    modal.find('input[name=name]').val('');
    modal.find('textarea[name=description]').val('');
    modal.find('.ui.status.dropdown').dropdown('set selected', 'NS');
    modal.find('.ui.card-color.dropdown').dropdown('set selected', '');
    modal.find('.extra.content .item').hide();
    modal.find('.comments-segment.segment').hide();
}

async function populateModal(modal, card) {
    modal.find('input[name=id]').val(card.id);
    modal.find('input[name=name]').val(card.name);
    modal.find('textarea[name=description]').val(card.description);
    modal.find('.ui.status.dropdown').dropdown('set selected', card.status);
    modal.find('.ui.card-color.dropdown').dropdown('set selected', card.color !== null ? card.color.id : '');
    modal.find('.extra.content .item').show();
    modal.find('.comments-segment.segment').show();
    modal.find('.ui.card-due-date.calendar').calendar('set date', card.due_date);
}

function showCardModal(card = null, bucketId, compact) {
    let create = card === null;
    const modal = $('.ui.card-form.modal');
    modal.off().form('reset');
    let dark = modal.hasClass('inverted');
    modal.find('.card-files').val('');
    modal.find('.files-container').empty();

    if (dark) {
        modal.find('.checklist.segment').addClass('inverted');
        modal.find('.files.segment').addClass('inverted');
        modal.find('.add-item.input').addClass('inverted');
        modal.find('.add-item.input').addClass('inverted');
        modal.find('.ui.dividing.header').addClass('inverted');
    } else {
        modal.find('.checklist.segment').removeClass('inverted');
        modal.find('.files.segment').removeClass('inverted');
        modal.find('.add-item.input').removeClass('inverted');
        modal.find('.ui.dividing.header').removeClass('inverted');
    };

    if (card) { populateModal(modal, card); }

    modal.modal({
        restoreFocus: false,
        autofocus: false,
        transition: 'scale',
        duration: 400,
        onShow: () => {
            cardEdited = false;
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
        },
        onHidden: () => {
            if (cardEdited) { getCards(bucketId, dark, compact); };
            $('.checklist-drake').empty();
            clearModal(modal);
        },
        onApprove: el => {
            modal.form('validate form');
            if (!modal.form('is valid')) {
                return false;
            };
            var data = {
                name: modal.find('input[name=name]').val(),
                description: modal.find('textarea[name=description]').val(),
                bucket: bucketId,
            }
            if (FEATURES.status) {
                data['status'] = modal.find('.ui.status.dropdown')?.dropdown('get value');
            }
            if (FEATURES.color) {
                data['color'] = modal.find('.ui.card-color.dropdown')?.dropdown('get value');
            }
            if (FEATURES.tags) {
                tagsString = modal.find('.ui.tags.dropdown')?.dropdown('get value');
                tags = tagsString.split(",").map(tag => ({ name: tag }));
                data['tag'] = JSON.stringify(tags);
            }
            if (FEATURES.assignees) {
                assigneesString = modal.find('.ui.assigned_to.dropdown')?.dropdown('get value');
                assignees = assigneesString?.split(",").map(username => ({ username: username }));
                data['assigned_to'] = JSON.stringify(assignees);
            }
            if (FEATURES.dueDate) {
                dueDate = modal.find('.ui.card-due-date.calendar')?.calendar('get date'); // If not null, dueDate is a Date object
                if (dueDate !== null) { data['due_date'] = dueDate.toISOString().split("T")[0] } // Convert to string in correct format
            }
            if (create) {
                method = 'POST';
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/`;
                data['order'] = 0;
            } else {
                method = 'PUT';
                id = modal.find('input[name=id]').val();
                data['order'] = $(`.card-el[data-card-id=${card.id}]`).index() + 1;
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${id}/`;
            }

            $.ajax({
                url: url,
                type: method,
                data: data,
                success: r => {
                    if (FEATURES.files) {
                        var files = modal.find('.card-files')[0]?.files;
                        if (files.length > 0) {
                            var cardId = create ? r.id : card.id;
                            for (f of files) {
                                var fd = new FormData();
                                fd.append('file', f);
                                attachFile(fd, bucketId, cardId);
                            }
                        }
                    }
                    getCards(bucketId, dark, compact);
                }
            });
        }
    }).modal('show');

    initializeTagsDropdown(modal.find('.ui.tags.dropdown'), card);
    initializeUsersDropdown(modal.find('.ui.assigned_to.dropdown'), card);

    modal.submit(e => {
        e.preventDefault();
        modal.find('.positive.button').click();
    });

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

    if (!create) {
        if (FEATURES.files) {
            getFiles(modal, bucketId, card.id);
        }
        if (FEATURES.comments) {
            modal.find('#suggest-comment').val('');
            initializeSuggest();
            loadComments(card, bucketId, dark);
        }
        if (FEATURES.checklist) {
            loadChecklistItems(card, bucketId, dark)
        }
    };
}

function attachFile(fd, bucketId, cardId) {
    $.api({
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/files/`,
        on: 'now',
        method: 'POST',
        data: fd,
        contentType: false,
        processData: false,
        successTest: r => r != 0,
        onSuccess: r => {
            console.log(r)
            $('body').toast({
                title: gettext('File upload'),
                message: `${gettext('Successfullly uploaded file')} ${r.file.split('/').at(-1)}!`,
                showProgress: 'bottom',
                classProgress: 'green',
                displayTime: 5000,
            })
        },
        onFailure: (response, element, xhr) => {
            if ('file' in response) {
                $('body').toast({
                    title: gettext('Error on file upload'),
                    message: response.file.join('\n'),
                    showProgress: 'bottom',
                    classProgress: 'red',
                    displayTime: 5000,
                })
            }
        }
    });
}

function toggleCardStatus(cardId, bucketId, currentStatus, dark, compact) {
    switch (currentStatus) {
        case 'NS':
            status = 'IP';
            status_name = gettext('In Progress');
            status_icon = 'dot circle outline';
            break;
        case 'IP':
            status = 'C';
            status_name = gettext('Completed');
            status_icon = 'check circle outline';
            break;
        case 'C':
            status = 'NS';
            status_name = gettext('Not Started');
            status_icon = 'circle outline';
            break;
    }
    $.ajax({
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/`,
        type: 'PATCH',
        data: { status: status },
    })
        .done(r => {
            $('body').toast({
                title: gettext('Card status changed'),
                message: interpolate(gettext('Card was marked as %s'), [`<strong>${status_name}<i class="${status_icon} icon"></i></strong>`]),
                showProgress: 'bottom'
            });
            getCards(bucketId, dark, compact)
        })
}

function showTimeEntriesModal(cardId, bucketId, dark, compact) {
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

function deleteCard(cardId, bucketId, dark, compact) {
    modal = $('.ui.delete.confirmation.modal')
    modal
        .modal({
            onShow: () => {
                modal.find('.header').text(gettext('Delete card'));
                modal.find('.content').text(interpolate(gettext('Are you sure you want to delete card %s?'), [cardId]));
            },
            onApprove: () => {
                $.ajax({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}`,
                    type: 'DELETE',
                    success: function (result) {
                        getCards(bucketId, dark, compact);
                    }
                });
            }
        })
        .modal('show');
}

function addNewTagInput(containerElement) {
    el = containerElement.append(`
      <form class="ui unstackable form" data-tag-id="" style="width: 100%; margin-bottom: .5em;">
        <div class="" style="display: flex; flex-flow: row nowrap;">
          <input type="hidden" name="id" value="">
          <div style="flex: 0 0 auto; width: 6em; display: flex; margin-right: .5em;">
            <select class="ui tag-icon new-tag clearable compact two column mini dropdown" data-tag-id="">
            </select>
          </div>
          <div style="flex: 0 0 auto; width: 6em; display: flex; margin-right: .5em;">
            <select class="ui tag-color new-tag clearable compact two column mini dropdown" data-tag-id="">
            </select>
          </div>
          <div class="ui mini input" style="flex: 1 1 auto; margin-right: .5em;">
            <input class="tag-name" type="text" placeholder="${gettext('Name')}" data-tag-id="">
          </div>
          <div style="">
            <div class="ui icon red delete new-tag mini button"><i class="delete icon"></i></div>
          </div>
        </div>
      </form>
    `);
    let iconDropdown = $(`.tag-icon.new-tag.dropdown`);
    iconDropdown.dropdown({
        placeholder: gettext('Icon'),
        values: ICON_VALUES,
        context: '.tags.modal .content',
    });
    let colorDropdown = $(`.tag-color.new-tag.dropdown`);
    colorDropdown.dropdown({
        placeholder: gettext('Color'),
        values: COLOR_VALUES,
        context: '.tags.modal .content',
    });
    el.find('.delete.button.new-tag').off();
    el.find('.delete.button.new-tag').click(e => {
        $(e.target).closest('form').remove();
    })
}

function renderTagForms(containerElement, tag) {
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
                    <input class="tag-name" type="text" placeholder="${gettext('Name')}" data-tag-id="${tag.id}">
                </div>
                <div style="">
                    <div class="ui icon red delete mini button" data-content="${gettext('Delete tag')}" data-tag-id="${tag.id}"><i class="delete icon"></i></div>
                </div>
            </div>
        </form>
    `);
    $(`.delete.button[data-tag-id=${tag.id}]`).popup();
    let iconDropdown = $(`.tag-icon.dropdown[data-tag-id=${tag.id}]`);
    iconDropdown.dropdown({
        placeholder: gettext('Icon'),
        values: ICON_VALUES,
        context: '.tags.modal .content'
    });
    if (tag.icon !== null) {
        iconDropdown.dropdown('set selected', tag.icon.id);
    };
    let colorDropdown = $(`.tag-color.dropdown[data-tag-id=${tag.id}]`);
    colorDropdown.dropdown({
        placeholder: gettext('Color'),
        values: COLOR_VALUES,
        context: '.tags.modal .content',
    });
    if (tag.color !== null) {
        colorDropdown.dropdown('set selected', tag.color.id);
    };
    $(`input[type=text][data-tag-id=${tag.id}]`).val(tag.name);
    $(`.delete.button[data-tag-id=${tag.id}]`).click(() => {
        $('body').modal({
            title: gettext('Deletion confirmation'),
            class: 'mini',
            closeIcon: true,
            content: interpolate(gettext('Are you sure yo want to delete tag %s?'), [tag.name]),
            allowMultiple: true,
            actions: [
                {
                    text: gettext('Yes'),
                    class: 'positive'
                },
                {
                    text: gettext('Cancel'),
                    class: 'deny'
                },
            ],
            onApprove: () => {
                $.ajax({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/${tag.id}`,
                    method: 'DELETE',
                }).done(r => {
                    $(`form[data-tag-id=${tag.id}]`).remove();
                    loadBoard();
                })
            }
        }).modal('show');
    })
}

async function showManageTagsModal(allowMultiple = false, fromCardModal = false, callback = undefined) {
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
                    ${gettext('Add new tag')}
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

function getSearchCardsDropdownValues() {
    var tags = $('.tags .label')
        .toArray()
        .map(tag => $(tag).text().trim());
    tags = [...new Set(tags)];
    tags = tags.map(tag => ({
        icon: 'hashtag',
        value: '#' + tag,
        name: tag,
    }));
    var users = $('.assignees .image')
        .toArray()
        .map(user => $(user).attr('data-username'));
    users = [...new Set(users)];
    users = users.map(user => ({
        icon: 'at',
        value: '@' + user,
        name: user,
    }))
    var values = [...new Set([...tags, ...users])]
    return values;
}

async function filterCards() {
    for (card of $('.card-el')) {
        if (!isCardOnFilter($(card))) {
            $(card).hide();
        } else {
            $(card).show();
        }
    }
}

function isCardOnFilter(cardEl, selector = '.ui.search-cards.dropdown', filterMode = 'or') {
    var name = cardEl.find('.card-name').text().trim();
    var tags = cardEl.find('.tags .label')
        .toArray()
        .map(tag => '#' + $(tag).text().trim())
    var users = cardEl.find('.assignees .image')
        .toArray()
        .map(user => '@' + $(user).attr('data-username'))
    var cardItems = [...new Set([name, ...tags, ...users])]
    var queryItems = $(selector).dropdown('get value').split(',');

    if (queryItems.length == 1 && queryItems[0] == '') { return true }

    if (filterMode.toLowerCase() === 'and') {
        result = queryItems.every(i => cardItems.includes(i));
    } else if (filterMode.toLowerCase() === 'or') {
        result = queryItems.some(i => cardItems.includes(i));
    }
    return result;
}

function initializeSearchCardsDropdown(selector = '.ui.search-cards.dropdown') {
    $(selector).dropdown({
        clearable: true,
        allowAdditions: true,
        forceSelection: false,
        match: 'value',
        direction: 'downward',
        placeholder: gettext('Filter cards'),
        onChange: (value, text, $choice) => {
            filterCards(value);
        },
        filterRemoteData: true,
        saveRemoteData: false,
        ignoreDiacritics: true,
        fullTextSearch: true,
        apiSettings: {
            cache: false,
            response: [],
            loadingDuration: 200,
            successTest: r => true,
            onResponse: r => ({ results: getSearchCardsDropdownValues() })
        }
    });
}

function renderGrid(year, month) {
    var today = new Date();
    var currentYear = today.getFullYear();
    var currentMonth = today.getMonth();
    var currentDay = today.getDate();
    var firstDay = new Date(year, month - 1, 1);
    var lastDay = new Date(year, month, 0);
    startAt = firstDay.getDay();
    lastDay = lastDay.getDate();
    rows = Math.ceil((lastDay + startAt) / 7);
    conteiner = "#calendar-grid";
    $(conteiner).empty();
    for (let i = 0; i < rows; i++) {
        var row = "";
        for (let j = 1; j <= 7; j++) {
            var day = i * 7 + j - startAt;
            if (day <= 0 || day > lastDay) {
                day = "";
            }
            var isToday = (day == currentDay && month == currentMonth + 1 && year == currentYear);
            row += `
                <div class="calendar-cell column" data-day="${day}" style="overflow-y: visible; ${isToday ? 'color: #276f86; background-color: #f8ffff; box-shadow: 0 0 0 1px #a9d5de inset,0 0 0 0 transparent;' : ''}">
                    ${day}
                    <div class="calendar-cell-content cards-drake" data-day="${day}" style="padding: .5em; height: calc(100% - 1.5em); overflow-y: auto;">
                    </div>
                </div>
            `
        }
        $(conteiner).append(`
            <div class="calendar-row" style="flex: 1 0 auto; display: flex; flex-flow: row nowrap;">
                ${row}
            </div>
        `);
    }
    $('.calendar-row').height('100px');
}

async function getCards() {
    date = $('#month_year_calendar').calendar('get date');
    getCardsCalendar(date.getFullYear(), date.getMonth() + 1);
    getCardsNoDueDate();
}

async function getCardsCalendar(year, month) {
    $.api({
        on: 'now',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/calendar/?year=${year}&month=${month}`,
        method: 'GET',
        stateContext: ".calendar.card",
        onSuccess: r => {
            days = [...new Set(r.map(c => parseInt(c.due_date.split('-').at(-1))))];
            for (day of days) {
                cards = r.filter(c => parseInt(c.due_date.split('-').at(-1)) == day);
                renderCards(
                    containerSelector = `.calendar-cell-content[data-day=${day}]`,
                    cards = cards,
                );
            }
            filterCards();
        }
    })
}

async function getCardsNoDueDate() {
    $.api({
        on: 'now',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/calendar/`,
        method: 'GET',
        stateContext: ".ui.no-due-date.card",
        onSuccess: r => {
            renderCards(
                containerSelector = "#no-due-date-cards",
                cards = r,
            );
            filterCards();
        }
    })
}

function initializeCalendar() {
    var today = new Date();
    $('#month_year_calendar').calendar({
        today: true,
        type: 'month',
        onChange: () => {
            date = $('#month_year_calendar').calendar('get date');
            renderGrid(date.getFullYear(), date.getMonth() + 1);
            getCardsCalendar(date.getFullYear(), date.getMonth() + 1);
        },
    }).calendar('set date', today);
    renderGrid(today.getFullYear(), today.getMonth() + 1);
    getCardsCalendar(today.getFullYear(), today.getMonth() + 1);
}

function nextMonth() {
    var date = $('#month_year_calendar').calendar('get date');
    date.setMonth(date.getMonth() + 1);
    $('#month_year_calendar').calendar('set date', date);
}

function previousMonth() {
    var date = $('#month_year_calendar').calendar('get date');
    date.setMonth(date.getMonth() - 1);
    $('#month_year_calendar').calendar('set date', date);
}

function initializeColorDropdown() {
    $('.ui.card-color.dropdown').dropdown({
        clearable: true,
        placeholder: gettext('Select a color theme'),
        values: colorsForDropdown,
    })
}