const PLACEHOLDER_AVATAR = '/static/image/avatar-1577909.svg'
const allowedUsers = getBoardAllowedUsers()
var intervals = []
var cardBeingDragged
var containerCardIsOver
var bucketBeingDragged
var containerBucketIsOver
var scrollIntervalID
var isScrolling = false
var cardEdited = false
var boardTimestamp = new Date()
var autoRefresh = null
var bucketsDrake
var cardsDrake

async function setWallpaper() {
    if (wallpaper) {
        $('#board').css('background-image', `url('${wallpaper}')`)
    } else {
        $('#board').css('background-image', '')
    }
}

async function setCardGlassEffect(blur = false, blurness = 5, opacity = 50) {
    if (wallpaper) {
        for (el of $('.card-el')) {
            color = $(el).css('background-color')
            if (color.split('(')[0] === 'rgb') {
                newColor = `${color.replace('rgb(', '').replace(')', '')}, ${opacity / 100}`
                $(el).css('background-color', `rgba(${newColor})`)
                if (blur) {
                    $(el).css('backdrop-filter', `blur(${blurness}px)`)
                }
            }
        }
    }
}

async function setBucketGlassEffect(blur = false, blurness = 5, opacity = 50) {
    if (wallpaper) {
        for (el of $('.bucket-el')) {
            color = $(el).css('background-color')
            if (color.split('(')[0] === 'rgb') {
                newColor = `${color.replace('rgb(', '').replace(')', '')}, ${opacity / 100}`
                $(el).css('background-color', `rgba(${newColor})`)
                if (blur) {
                    $(el).css('backdrop-filter', `blur(${blurness}px)`)
                }
            }
        }
    }
}

function startAutoRefresh(period = 5000) {
    if (autoRefresh !== null) { clearInterval(autoRefresh) }
    autoRefresh = setInterval(checkUpdates, period)
}

async function updateBucketTimetamp(bucketId) {
    bucketEl = $(`.bucket-el[data-bucket-id=${bucketId}]`)
    now = new Date()
    now = new Date(now.getTime() + 1000)
    bucketEl.attr('data-bucket-updated-at', now)
}

function checkUpdates() {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/last-updated/`,
        onSuccess(r) {
            // handle board
            currentBoardTimestamp = new Date(r.board)
            if (currentBoardTimestamp > boardTimestamp) {
                loadBoard()
                return
            }
            // handle buckets
            bucketIds = r.buckets.map(b => b.id)
            // Is there any bucket in DOM not in response?
            for (b of $('.bucket-el')) {
                bucketIdDOM = parseInt($(b).attr('data-bucket-id'))
                if (!bucketIds.includes(bucketIdDOM)) {
                    loadBoard()
                    return
                }
            }
            for (b of r.buckets) {
                bucketTimestamp = new Date(b.ts)
                // Check if bucket exists in DOM
                bucketEl = $(`.bucket-el[data-bucket-id=${b.id}]`)
                if (bucketEl.length) {
                    bucketIdDOM = parseInt(bucketEl.attr('data-bucket-id'))
                    if (b.id === bucketIdDOM) {
                        // Compare timestamps
                        bucketTimestampDOM = new Date(bucketEl.attr('data-bucket-updated-at'))
                        if (bucketTimestamp > bucketTimestampDOM) {
                            bucketEl.attr('data-bucket-updated-at', b.ts)
                            getCards(b.id)
                        }
                    }
                } else {
                    // If bucket not in DOM
                    loadBoard()
                }
            }
        },
        onError: r => { console.error(JSON.stringify(r)) },
    })
}

function changeBucketWidth(width) {
    updateConfig({bucket_width: width})
}

function setCompactMode(bool) {
    updateConfig({compact: bool})
}

function setDarkMode(bool) {
    updateConfig({dark: bool})
}

function getConfig() {
    config = sessionStorage.getItem('config')
    if (config == null) {
        $.ajax({
            async: false,
            method: 'GET',
            url: `/pm/api/config/`,
            success(r) {
                sessionStorage.setItem('config', JSON.stringify(r))
                config = r
            },
        })
        return config
    } else {
        return JSON.parse(config)
    }
}

function updateConfig(data) {
    $.api({
        on: 'now',
        method: 'PATCH',
        url: `/pm/api/config/`,
        data: data,
        onSuccess(r) {
            sessionStorage.setItem('config', JSON.stringify(r))
            config = r
            loadBoard()
        },
    })
}

function getDarkMode() {
    config = getConfig()
    return config.dark
}

function getCompactMode() {
    config = getConfig()
    return config.compact
}

function getBucketWidth() {
    config = getConfig()
    return config.bucket_width
}

function startElementScroll(directionX, directionY, elementToScroll, increment, delay) {
    let scroll = () => {
        elementToScroll.scrollBy(directionX * increment, directionY * increment)
    }
    if (!isScrolling) {
        scrollIntervalID = setInterval(scroll, delay)
        isScrolling = true
    }
}

function stopElementScroll(intID) {
    clearInterval(intID)
    isScrolling = false
}

function loadBoard() {
    boardTimestamp = new Date()
    clearIntervals()
    getBuckets()
    enableProximityScroll()
    setWallpaper()
}

async function getActivities(bucketId, cardId) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/activities/`,
        onSuccess(r) {
            console.table(r)
        },
    })
}

async function renderBuckets(containerSelector, buckets) {
    let dark = getDarkMode()
    let compact = getCompactMode()
    let width = getBucketWidth()
    $(containerSelector).empty()
    if (compact) {
        $(containerSelector).css('padding-left', '.25em')
        $(containerSelector).css('padding-right', '.5em')
    } else {
        $(containerSelector).css('padding-left', '.25em')
        $(containerSelector).css('padding-right', '.75em')
    }
    setBoardDarkMode(containerSelector, dark)
    buckets.forEach(bucket => {
        $(containerSelector).append(getBucketHTML(bucket, dark, compact, width))
        attachBucketTouchEvent(bucket)
        initializeBucketButtons(bucket)
        $(containerSelector).ready(e => { getCards(bucket.id) })
    })
    $(containerSelector).append(getAddBucketButtonHTML(dark))
    $(`.add.bucket.button`).off().click(e => { showBucketModal() })
    e = $('.add.bucket.button').siblings().last()
    $('.add.bucket.button').css('marginTop', e.css('marginTop'))
    $('.add.bucket.button').css('marginBottom', e.css('marginBottom'))
    setBucketGlassEffect()
}

function setBoardDarkMode(containerSelector, bool) {
    if (bool) {
        $('html').addClass('dark')
        $('body').addClass('dark')
        $('.form').addClass('inverted')
        $('.modal').addClass('inverted')
        $('.dropdown').addClass('inverted')
        $('.calendar').addClass('inverted')
        $(containerSelector).parents().first().addClass('dark')
        
    } else {
        $('body').removeClass('dark')
        $('html').removeClass('dark')
        $('.form').removeClass('inverted')
        $('.modal').removeClass('inverted')
        $('.dropdown').removeClass('inverted')
        $('.calendar').removeClass('inverted')
        $(containerSelector).parents().first().removeClass('dark')
    }
}

async function attachBucketTouchEvent(bucket) {
    document.querySelectorAll(`.handle[data-bucket-id='${bucket.id}']`)[0].addEventListener(
        'touchmove', e => {
            e.preventDefault()
            const board = document.getElementById('board')
            if (bucketsDrake.dragging && containerBucketIsOver !== null && bucketBeingDragged !== null) {
                var threshold = 50
                if ((e.touches[0].pageY - threshold) < containerBucketIsOver.getBoundingClientRect().top) {
                    startElementScroll(0, -1, containerBucketIsOver, 50, 100)
                } else if ((e.touches[0].pageY + threshold) > containerBucketIsOver.getBoundingClientRect().bottom) {
                    startElementScroll(0, 1, containerBucketIsOver, 50, 100)
                } else if ((e.touches[0].pageX + threshold) > board.getBoundingClientRect().right) {
                    startElementScroll(1, 0, board, 50, 100)
                } else if ((e.touches[0].pageX - threshold) < board.getBoundingClientRect().left) {
                    startElementScroll(-1, 0, board, 50, 100)
                } else {
                    stopElementScroll(scrollIntervalID)
                }
            } else {
                stopElementScroll(scrollIntervalID)
            }
        },
        { passive: false }
    )
}

async function renderCards(containerSelector, cards, bucketId) {
    let dark = getDarkMode()
    let compact = getCompactMode()
    $(containerSelector).empty()
    cards.forEach(card => {
        switch (card.status) {
            case 'NS':
                status_icon = 'circle outline'
                break
            case 'IP':
                status_icon = 'dot circle outline'
                break
            case 'C':
                status_icon = 'check circle outline'
                break
        }
        var overdue = false
        var dueDate = null
        if (card.due_date !== null) {
            var now = new Date()
            dueDate = card.due_date.split('-')
            dueDate = new Date(dueDate[0], dueDate[1] - 1, dueDate[2])
            overdue = now > dueDate
        }
        $(containerSelector).append(getCardHTML(card, dark, compact, overdue))
        let extraContent = $(containerSelector).find(`.extra.content[data-card-id=${card.id}]`)
        let tagsContainer = $(containerSelector).find(`.meta .tags[data-card-id=${card.id}]`)
        if (card.total_time > 0 && FEATURES.time_entries) {
            extraContent.append(getTimeEntryCardletHTML(card))
        }
        if (card.comments > 0 && FEATURES.comments) {
            extraContent.prepend(getCommentCardletHTML(card))
        }
        if (card.total_files > 0 && FEATURES.files) {
            extraContent.prepend(getFileCardletHTML(card))
        }
        if (card.total_items > 0 && FEATURES.checklist) {
            extraContent.prepend(getChecklistCardletHTML(card))
        }
        if (card.due_date !== null && FEATURES.dueDate) {
            extraContent.prepend(getDueDateCardletHTML(overdue, dueDate))
        }
        if (card.tag.length > 0) {
            renderTags(tagsContainer, card.tag)
        }
        let assigneesContainer = $(containerSelector).find(`.meta .assignees[data-card-id=${card.id}]`)
        if (card.assigned_to.length > 0) {
            renderAssignees(
                assigneesContainer,
                card.assigned_to,
                card.color !== null ? dark ? card.color.dark : card.color.light : null,
            )
        }
        if (extraContent.html().trim() === '') {
            // If no extra content is found, remove the element
            extraContent.remove()
        }
        attachCardTouchEvent(card)
        initializeCardButtons(bucketId, card)
        if (card.is_running) { startTimerAnimation(card.id) }
    })
    $('.card-el').removeClass('loading')
    setCardGlassEffect()
}

async function attachCardTouchEvent(card) {
    document.querySelectorAll(`.handle[data-card-id='${card.id}']`)[0].addEventListener(
        'touchmove', e => {
            e.preventDefault()
            const board = document.getElementById('board')
            if (cardsDrake.dragging && containerCardIsOver !== null && cardBeingDragged !== null) {
                var threshold = 50
                if ((e.touches[0].pageY - threshold) < containerCardIsOver.getBoundingClientRect().top) {
                    startElementScroll(0, -1, containerCardIsOver, 50, 100)
                } else if ((e.touches[0].pageY + threshold) > containerCardIsOver.getBoundingClientRect().bottom) {
                    startElementScroll(0, 1, containerCardIsOver, 50, 100)
                } else if ((e.touches[0].pageX + threshold) > board.getBoundingClientRect().right) {
                    startElementScroll(1, 0, board, 50, 100)
                } else if ((e.touches[0].pageX - threshold) < board.getBoundingClientRect().left) {
                    startElementScroll(-1, 0, board, 50, 100)
                } else {
                    stopElementScroll(scrollIntervalID)
                }
            } else {
                stopElementScroll(scrollIntervalID)
            }
        },
        { passive: false }
    )
}

async function renderFiles(modal, bucketId, cardId, files) {
    for (f of files) {
        modal.find('.files-container').append(getFileHTML(f))
        $(`.image[data-file-id=${f.id}]`).dimmer({ on: 'hover' })
        $(`.delete-file[data-file-id=${f.id}]`).off().on('click', e => {
            fileId = $(e.target).attr('data-file-id')
            showDeleteFileModal(bucketId, cardId, fileId)
        })
    }
}

function renderItems(containerSelector, items, bucketId, cardId) {
    let dark = getDarkMode()
    $(containerSelector).empty()
    items.forEach(item => {
        $(containerSelector).append(getChecklistItemHTML(item, dark))
    })
    $('.checklist-item input').on('keypress', e => {
        if (e.keycode === 13 || e.which === 13) {
            let index = $(e.target).parent().parent().index() + 1
            let nextElement = $(e.target).parent().parent().parent().children().toArray()[index]
            if (nextElement !== undefined) {
                $(nextElement).find('input[type=text]').focus()
            }
        }
    })
    $('.checklist-item input').blur(e => {
        if (e.target.value != $(e.target).attr('data-text')) {
            let itemId = $(e.target).attr('data-item-id')
            $(this).attr("disabled", "disabled")
            $.api({
                on: 'now',
                method: 'PATCH',
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/items/${itemId}/`,
                data: {
                    name: e.target.value,
                },
                onSuccess(r) {
                    getItems(bucketId, cardId)
                },
                onComplete() { $(this).removeAttr("disabled") },
            })
        }
    })
    $('.delete-item.button').click(e => {
        let itemId = $(e.target).attr('data-item-id')
        $.api({
            on: 'now',
            method: 'DELETE',
            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/items/${itemId}/`,
            onSuccess(r) {
                getItems(bucketId, cardId)
                cardEdited = true
            },
        })
    })

    $('.checklist-item .checkbox').toArray().forEach(el => {
        $(el).checkbox({
            onChange() {
                let itemId = $(el).attr('data-item-id')
                let checked = $(el).checkbox('is checked')
                $.api({
                    on: 'now',
                    method: 'POST',
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/items/${itemId}/check/`,
                    data: { checked: checked },
                    onSuccess(r) {
                        getItems(bucketId, cardId)
                        cardEdited = true
                    },
                })
            }
        })
    })
}

function renderTimeEntries(containerSelector, timeEntries, bucketId, cardId) {
    let dark = getDarkMode()
    $(containerSelector).empty()
    if (timeEntries.length == 0) {
        $(containerSelector).append(getNoTimeEntryPlaceholderHTML())
        return
    }
    timeEntries.forEach(timeEntry => {
        $(containerSelector).append(getTimeEntryHTML(timeEntry, dark))
        let startDate = $(`.time-entry.start-date[data-time-entry-id=${timeEntry.id}]`)
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
                    if (!date) return ''
                    return date.toLocaleDateString(LANGUAGE_CODE)
                }
            }
        })
        let stopDate = $(`.time-entry.stop-date[data-time-entry-id=${timeEntry.id}]`)
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
                    if (!date) return ''
                    return date.toLocaleDateString(LANGUAGE_CODE)
                }
            }
        })

        if (timeEntry.started_at !== null) {
            let startedAt = new Date(timeEntry.started_at)
            startDate.calendar('set date', startedAt)
        }

        if (timeEntry.stopped_at !== null) {
            let stoppedAt = new Date(timeEntry.stopped_at)
            stopDate.calendar('set date', stoppedAt)
        }
        let timeEntrySegment = $(`.ui.form.segment[data-time-entry-id=${timeEntry.id}]`)
        $(`.delete.button[data-time-entry-id=${timeEntry.id}]`).click(e => {
            timeEntrySegment.addClass('loading')
            $.api({
                on: 'now',
                method: 'DELETE',
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/time-entries/${timeEntry.id}/`,
                onSuccess(r) {
                    timeEntrySegment.remove()
                    $('body').toast({
                        class: 'warning',
                        message: gettext('Time entry deleted!'),
                    })
                },
                onComplete() {
                    timeEntrySegment.removeClass('loading')
                }
            })
        })
        $(`.save.button[data-time-entry-id=${timeEntry.id}]`).click(e => {
            $.api({
                on: 'now',
                method: 'PATCH',
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/time-entries/${timeEntry.id}/`,
                data: {
                    name: $(`input[name=name][data-time-entry-id=${timeEntry.id}]`).val(),
                    started_at: startDate.calendar('get date').toISOString(),
                    stopped_at: stopDate.calendar('get date').toISOString(),
                },
                stateContext: timeEntrySegment,
                onSuccess(r) {
                    $('body').toast({
                        class: 'success',
                        message: gettext('Time entry successfully updated!'),
                    })
                },
            })
        })
    })
}

function renderComments(containerSelector, comments, bucketId, cardId) {
    let dark = getDarkMode()
    $(containerSelector).empty()
    comments.forEach(comment => {
        text = insertLinksAndMentions(comment.text)
        if (comment.created_by.username === USERNAME) {
            $(containerSelector).append(getCommentHTML(comment, text, dark, true))
            $(`a.edit-comment[data-comment-id=${comment.id}]`).off().click(e => {
                editCommentTextarea = $('textarea.comment-edit')
                $('.comment-edit.modal').modal({
                    onShow() {
                        editCommentTextarea.val(comment.text)
                    },
                    onApprove() {
                        $.api({
                            on: 'now',
                            method: 'PATCH',
                            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/comments/${comment.id}/`,
                            data: { text: editCommentTextarea.val() },
                            onSuccess(r) {
                                editCommentTextarea.val('')
                                $('body').toast({ message: gettext("Comment edited.") })
                            },
                        })
                    },
                }).modal('show')
            })
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
                    onApprove() {
                        $.api({
                            on: 'now',
                            method: 'DELETE',
                            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/comments/${comment.id}/`,
                            onSuccess(r) {
                                $('body').toast({ message: gettext("Comment deleted.") })
                            },
                        })
                    }
                }).modal('show')
            })
        } else {
            $(containerSelector).append(getCommentHTML(comment, text, dark, false))
        }
        $(`.mention`).popup()
    })
}

async function renderTags(container, tags) {
    for (tag of tags) {
        container.append(getTagHTML(tag))
    }
}

async function renderAssignees(container, assignees, borderColor = null) {
    let dark = getDarkMode()
    container.ready(e => { $(`img[data-username='${user.username}']`).popup() })
    for (user of assignees) {
        container.append(getAssigneeHTML(borderColor, user, dark))
    }
    
}

async function loadComments(card, bucketId) {
    getComments(bucketId, card.id)
    $('.add-reply.button').off().click(e => {
        $(this).attr("disabled", "disabled")
        $.api({
            on: 'now',
            method: 'POST',
            url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${card.id}/comments/`,
            data: {
                card: card.id,
                text: $('textarea.add-reply').val(),
            },
            onSuccess(r) {
                $('textarea.add-reply').val('')
                getComments(bucketId, card.id)
                cardEdited = true
            },
            onComplete() { $(this).removeAttr("disabled") },
        })
    })
}

async function loadChecklistItems(card, bucketId) {
    getItems(bucketId, card.id)
    $('.add-item.input input').off().on('keypress', e => {
        if (e.keycode === 13 || e.which === 13) {
            $(this).attr("disabled", "disabled")
            $.api({
                on: 'now',
                method: 'POST',
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${card.id}/items/`,
                data: {
                    name: e.target.value,
                    card: card.id,
                    order: 1
                },
                onSuccess(r) {
                    e.target.value = ''
                    getItems(bucketId, card.id)
                    cardEdited = true
                },
                onComplete() { $(this).removeAttr("disabled") },
            })
        }
    })
}

async function enableProximityScroll() {
    function proximityScroll(e) {
        if (cardsDrake.dragging && containerCardIsOver !== null && cardBeingDragged !== null) {
            var boardBody = document.getElementById("board")
            var threshold = 50
            if ((e.pageY - threshold) < containerCardIsOver.getBoundingClientRect().top) {
                startElementScroll(0, -1, containerCardIsOver, 50, 100)
            } else if ((e.pageY + threshold) > containerCardIsOver.getBoundingClientRect().bottom) {
                startElementScroll(0, 1, containerCardIsOver, 50, 100)
            } else if ((e.pageX + threshold) > boardBody.getBoundingClientRect().right) {
                startElementScroll(1, 0, boardBody, 50, 100)
            } else if ((e.pageX - threshold) < boardBody.getBoundingClientRect().left) {
                startElementScroll(-1, 0, boardBody, 50, 100)
            } else {
                stopElementScroll(scrollIntervalID)
            }
        } else if (bucketsDrake.dragging && containerBucketIsOver !== null && bucketBeingDragged !== null) {
            var threshold = 50
            if ((e.pageX - threshold) < containerBucketIsOver.getBoundingClientRect().left) {
                startElementScroll(-1, 0, containerBucketIsOver, 50, 100)
            } else if ((e.pageX + threshold) > containerBucketIsOver.getBoundingClientRect().right) {
                startElementScroll(1, 0, containerBucketIsOver, 50, 100)
            } else {
                stopElementScroll(scrollIntervalID)
            }
        } else {
            stopElementScroll(scrollIntervalID)
        }
    }
    document.addEventListener("mousemove", proximityScroll)
}

async function getBuckets() {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/`,
        onSuccess(r) {
            renderBuckets(
                containerSelector = '#board',
                buckets = r,
            )
        }
    })
}

async function getCards(bucketId) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/`,
        stateContext: `.bucket-el[data-bucket-id=${bucketId}]`,
        onSuccess(r) {
            updateBucketTimetamp(bucketId)
            renderCards(
                containerSelector = `#bucket-${bucketId}`,
                cards = r,
                bucketId = bucketId,
            )
            filterCards()
        }
    })
}

async function getItems(bucketId, cardId) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/items/`,
        stateContext: '.checklist.segment',
        onSuccess: r => {
            renderItems(
                containerSelector = ".checklist-drake",
                items = r,
                bucketId = bucketId,
                cardId = cardId,
            )
        }
    })
}

async function getComments(bucketId, cardId) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/comments/`,
        stateContext: '.comments-segment.segment',
        onSuccess: r => {
            renderComments(
                containerSelector = "#card-comments",
                items = r,
                bucketId = bucketId,
                cardId = cardId,
            )
        },
    })
}

function getTimeEntries(bucketId, cardId) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/time-entries/`,
        onSuccess(r) {
            renderTimeEntries(
                containerSelector = "#time-entries .content",
                timeEntryes = r,
                bucketId = bucketId,
                cardId = cardId,
            )
        }
    })
}

function getTags() {
    let tags = sessionStorage.getItem('tags')
    if (tags != null) {
        tags = JSON.parse(tags)
        return tags
    }
    $.ajax({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/`,
        async: false,
        throttleFirstRequest: false,
        cache: false,
    })
    .done(r => {
        tags = r
        sessionStorage.setItem('tags', JSON.stringify(tags))
    })
    return tags
}

function getBoardAllowedUsers() {
    var allowed_users = []
    $.ajax({
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/`,
        method: 'GET',
        async: false,
    })
    .done(r => { allowed_users = r.allowed_users })
    return allowed_users
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

async function clearModal(modal) {
    modal.find('input[name=id]').val('')
    modal.find('input[name=name]').val('')
    modal.find('textarea[name=description]').val('')
    modal.find('.ui.status.dropdown').dropdown('set selected', 'NS')
    modal.find('.ui.card-color.dropdown').dropdown('set selected', '')
    modal.find('.extra.content .item').hide()
    modal.find('.comments-segment.segment').hide()
}

async function populateModal(modal, card) {
    modal.find('input[name=id]').val(card.id)
    modal.find('input[name=name]').val(card.name)
    modal.find('textarea[name=description]').val(card.description)
    modal.find('.ui.status.dropdown').dropdown('set selected', card.status)
    modal.find('.ui.card-color.dropdown').dropdown('set selected', card.color !== null ? card.color.id : '')
    modal.find('.extra.content .item').show()
    modal.find('.comments-segment.segment').show()
    modal.find('.ui.card-due-date.calendar').calendar('set date', card.due_date)
}

function attachFile(fd, bucketId, cardId) {
    $.api({
        on: 'now',
        method: 'POST',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/files/`,
        data: fd,
        contentType: false,
        processData: false,
        successTest: r => r != 0,
        onSuccess(r) {
            $('body').toast({
                title: gettext('File upload'),
                message: interpolate(gettext('Successfullly uploaded file %s!'), [r.file.split('/').at(-1)]),
                showProgress: 'bottom',
                classProgress: 'green',
                displayTime: 5000,
            })
        },
        onFailure(response, element, xhr) {
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
    })
}

function toggleCardStatus(cardId, bucketId, currentStatus) {
    switch (currentStatus) {
        case 'NS':
            code = 'IP'
            text = gettext('In Progress')
            icon = 'dot circle outline'
            break
        case 'IP':
            code = 'C'
            text = gettext('Completed')
            icon = 'check circle outline'
            break
        case 'C':
            code = 'NS'
            text = gettext('Not Started')
            icon = 'circle outline'
            break
    }
    $.api({
        on: 'now',
        method: 'PATCH',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/`,
        data: { status: code },
        onSuccess(r) {
            $('body').toast({
                title: gettext('Card status changed'),
                message: interpolate(gettext('Card was marked as %s'), [`<strong>${text}<i class="${icon} icon"></i></strong>`]),
                showProgress: 'bottom'
            })
            getCards(bucketId)
        },
    })
}

function deleteBucket(bucketId) {
    modal = $('.ui.delete.confirmation.modal')
    modal
    .modal({
        onShow() {
            modal.find('.header').text(gettext('Delete bucket'))
            modal.find('.content').text(interpolate(gettext('Are you sure you want to delete bucket %s?'), [bucketId]))
        },
        onApprove() {
            $.api({
                on: 'now',
                method: 'DELETE',
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/`,
                onSuccess(result) { loadBoard() },
            })
        }
    })
    .modal('show')
}

function deleteCard(cardId, bucketId) {
    modal = $('.ui.delete.confirmation.modal')
    modal
    .modal({
        onShow() {
            modal.find('.header').text('Delete card')
            modal.find('.content').text(interpolate(gettext('Are you sure you want to delete card %s?'), [cardId]))
        },
        onApprove() {
            $.api({
                on: 'now',
                method: 'DELETE',
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}`,
                onSuccess(result) {
                    getCards(bucketId)
                }
            })
        }
    })
    .modal('show')
}

function startStopTimer(cardId, bucketId) {
    $.api({
        on: 'now',
        method: 'POST',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/timer/`,
        onSuccess(result) {
            if (result.action == 'start') {
                $('body').toast({
                    message: interpolate(gettext('Timer started for card %s.'), [cardId])
                })
                el = $(`.total-time[data-card-id=${cardId}]`)
                el.data('start', new Date())
                startTimerAnimation(cardId)
            } else if (result.action == 'stop') {
                $('body').toast({
                    message: interpolate(gettext('Timer stopped for card %s.'), [cardId])
                })
                stopTimerAnimation(cardId)
            }
            getCards(bucketId)
        }
    })
}

function addNewTagInput(containerElement) {
    el = $(getTagFormHTML("", getDarkMode()))
    el.ready(() => {
        let iconDropdown = el.find(`.tag-icon.dropdown`)
        iconDropdown.dropdown({
            placeholder: gettext('Icon'),
            values: ICON_VALUES,
            context: '.tags.modal .content',
        })
        let colorDropdown = el.find(`.tag-color.dropdown`)
        colorDropdown.dropdown({
            placeholder: gettext('Color'),
            values: COLOR_VALUES,
            context: '.tags.modal .content',
        })
        el.find('.delete.button').off().click(e => {
            $(e.target).closest('form').remove()
        })
    })
    containerElement.append(el)
}

function renderTagForms(containerElement, tag) {
    let dark = getDarkMode()
    containerElement.append(getTagFormHTML(tag.id, dark))
    $(`.delete.button[data-tag-id=${tag.id}]`).popup()
    let iconDropdown = $(`.tag-icon.dropdown[data-tag-id=${tag.id}]`)
    iconDropdown.dropdown({
        placeholder: gettext('Icon'),
        values: ICON_VALUES,
        context: '.tags.modal .content'
    })
    if (tag.icon !== null) {
        iconDropdown.dropdown('set selected', tag.icon.id)
    }
    let colorDropdown = $(`.tag-color.dropdown[data-tag-id=${tag.id}]`)
    colorDropdown.dropdown({
        placeholder: gettext('Color'),
        values: COLOR_VALUES,
        context: '.tags.modal .content',
    })
    if (tag.color !== null) {
        colorDropdown.dropdown('set selected', tag.color.id)
    }
    $(`input[type=text][data-tag-id=${tag.id}]`).val(tag.name)
    $(`.delete.button[data-tag-id=${tag.id}]`).click(deleteTag)
}

function deleteTag() {
    confirmationModal = $('body').modal({
        title: gettext('Deletion confirmation'),
        class: 'mini' + getDarkMode() ? ' inverted' : '',
        closeIcon: true,
        inverted: false,
        blurring: true,
        context: '.tags.modal',
        content: interpolate(gettext('Are you sure yo want to delete tag %s?'), [tag.name]),
        allowMultiple: true,
        actions: [
            {
                text: gettext('Cancel'),
                icon: 'close',
                click() {}
            },
            {
                text: gettext('Yes'),
                class: 'green',
                icon: 'save',
                click() {
                    $.api({
                        on: 'now',
                        method: 'DELETE',
                        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/${tag.id}`,
                        onSuccess(r) {
                            $(`form[data-tag-id=${tag.id}]`).remove()
                            loadBoard()
                        }
                    })
                }
            },
        ],
    })
    confirmationModal.modal('show')
}

async function hideManageTagsModal() {
    $('.ui.tags.modal').modal('hide')
}

function saveTagsOnManageTagsModal(tagsModal, callback) {
    var el = tagsModal.find('.content')
    el.find('.ui.form').each((index, form) => {
        id = $(form).find('input[name=id]').val()
        if (id == '') {
            method = 'POST'
            url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/`
        } else {
            method = 'PUT'
            url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/${id}/`
        }
        $.api({
            on: 'now',
            url: url,
            method: method,
            data: {
                icon: $(form).find('.tag-icon').dropdown('get value'),
                color: $(form).find('.tag-color').dropdown('get value'),
                name: $(form).find('.tag-name').val(),
            },
            onSuccess(r) {
                if (callback) {
                    callback()
                }
            }
        })
    })
    loadBoard()
    hideManageTagsModal()
}
