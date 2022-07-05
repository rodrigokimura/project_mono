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
                        compactMode = $('.ui.slider.board-compact').checkbox('is checked')
                        bucketTimestampDOM = new Date(bucketEl.attr('data-bucket-updated-at'))
                        if (bucketTimestamp > bucketTimestampDOM) {
                            bucketEl.attr('data-bucket-updated-at', b.ts)
                            getCards(b.id, compactMode)
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

function setCompact(bool) {
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

function initializeBucketDragAndDrop() {
    bucketsDrake = dragula({
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
    bucketsDrake.on('drop', (el, target, source, sibling) => {
        $(el).removeClass('card').addClass('loading card')
        bucket = $(el).attr('data-bucket-id')
        order = $(target).children().toArray().findIndex(e => e == el) + 1
        $.api({
            on: 'now',
            method: 'POST',
            url: `/pm/api/bucket-move/`,
            data: {
                bucket: bucket,
                board: BOARD_ID,
                order: order,
            },
            onSuccess(r) { },
            onComplete() { $(el).removeClass('loading') }
        })
    })
    bucketsDrake.on('drag', (el, source) => {
        bucketBeingDragged = el
    })
    bucketsDrake.on('dragend', (el) => {
        bucketBeingDragged = null
        stopElementScroll(scrollIntervalID)
    })
    bucketsDrake.on('over', (el, container, source) => {
        containerBucketIsOver = container
    })
    bucketsDrake.on('out', (el, container, source) => {
        containerBucketIsOver = null
    })
}

function initializeCardDragAndDrop() {
    cardsDrake = dragula({
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
    cardsDrake.on('drop', (el, target, source, sibling) => {
        source_bucket = $(source).attr('id').replace('bucket-', '')
        target_bucket = $(target).attr('id').replace('bucket-', '')
        card = $(el).attr('data-card-id')
        order = $(target).children().toArray().findIndex(e => e == el) + 1
        $.api({
            on: 'now',
            method: 'POST',
            url: `/pm/api/card-move/`,
            stateContext: `.card-el[data-card-id=${card}]`,
            data: {
                source_bucket: source_bucket,
                target_bucket: target_bucket,
                card: card,
                order: order,
            },
            onSuccess(r) {
                status_changed = r.status_changed
                timer_action = r.timer_action
                if (status_changed || timer_action != 'none') {
                    loadBoard()
                }
                updateBucketTimetamp(target_bucket)
            },
            onFailure() {
                loadBoard()
            },
            onComplete() {
                $('.cardlet').popup()
            }
        })
    })
    cardsDrake.on('drag', (el, source) => {
        cardBeingDragged = el
    })
    cardsDrake.on('dragend', (el) => {
        cardBeingDragged = null
        stopElementScroll(scrollIntervalID)
    })
    cardsDrake.on('over', (el, container, source) => {
        containerCardIsOver = container
    })
    cardsDrake.on('out', (el, container, source) => {
        containerCardIsOver = null
    })
}

function str(seconds) {
    function pad(num, size = 2) {
        num = num.toString()
        while (num.length < size) num = "0" + num
        return num
    }
    var h = Math.floor((seconds % 31536000) / 3600)
    var m = Math.floor((((seconds % 31536000) % 86400) % 3600) / 60)
    var s = Math.floor((((seconds % 31536000) % 86400) % 3600) % 60)
    return `${pad(h)}:${pad(m)}:${pad(s)}`
}

function incrementSecond(cardId) {
    element = $(`.total-time[data-card-id=${cardId}]`)
    time = element.attr('data-time')
    start = new Date(element.data('start'))
    now = new Date()
    element.text(
        str(
            (now - start) / 1000 + parseFloat(time)
        )
    )
}

async function clearIntervals() {
    intervals.forEach(i => { clearInterval(i.interval) })
    intervals = []
}

function loadBoard() {
    let compact = $('.board-compact.checkbox').checkbox('is checked')
    let width = $('.ui.width.slider').slider('get value')
    boardTimestamp = new Date()
    clearIntervals()
    getBuckets(compact, width)
    enableProximityScroll()
    setWallpaper()
}

async function renderBuckets(containerSelector, buckets, compact = false, width) {
    let dark = getDarkMode()
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
        $(containerSelector).append(`
            <div class="ui ${dark ? 'inverted ' : ' '}card bucket-el" data-bucket-id="${bucket.id}" data-bucket-updated-at="${bucket.updated_at}" style="width: ${width}px; flex: 0 0 auto; display: flex; flex-flow: column nowrap; overflow-y: visible; scroll-snap-align: start;${compact ? ' margin-right: .25em; margin-top: .5em; margin-bottom: .5em;' : ''}">
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
                                <div class="add card item" data-bucket-id="${bucket.id}"><i class="add icon"></i>${gettext('Add new card')}</div>
                                <div class="divider"></div>
                                <div class="edit bucket item" data-bucket-id="${bucket.id}"><i class="edit icon"></i>${gettext('Edit this bucket')}</div>
                                <div class="delete bucket item" data-bucket-id="${bucket.id}"><i class="delete icon"></i>${gettext('Delete this bucket')}</div>
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
        `)
        attachBucketTouchEvent(bucket)
        initializeBucketButtons(bucket, compact)
        $(containerSelector).ready(e => { getCards(bucket.id, compact) })
    })
    $(containerSelector).append(`<div class="ui add bucket basic ${dark ? 'inverted ' : ' '}button" style="flex: 0 0 auto">${gettext('Add new bucket')}</div>`)
    $(`.add.bucket.button`).off().click(e => { showBucketModal() })
    e = $('.add.bucket.button').siblings().last()
    $('.add.bucket.button').css('marginTop', e.css('marginTop'))
    $('.add.bucket.button').css('marginBottom', e.css('marginBottom'))
    setBucketGlassEffect()
}

function setBoardDarkMode(containerSelector, bool) {
    if (bool) {
        $('.form').addClass('inverted')
        $('.modal').addClass('inverted')
        $('.dropdown').addClass('inverted')
        $('.calendar').addClass('inverted')
        $(containerSelector).parents().first().addClass('dark')
        
    } else {
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

async function initializeBucketButtons(bucket, compact) {
    $(`.ui.dropdown[data-bucket-id=${bucket.id}]`).dropdown({ action: 'hide' })
    $(`.add.card.item[data-bucket-id=${bucket.id}]`).on('click', e => { showCardModal(card = null, bucket.id, compact) })
    $(`#bucket-${bucket.id}`).on('dblclick', e => {
        const isCard = $(e.target).parents('.card-el').length > 0
        if (!isCard) { showCardModal(card = null, bucket.id, compact) }
    })
    $(`.edit.bucket.item[data-bucket-id=${bucket.id}]`).on('click', e => { showBucketModal(bucket) })
    $(`.delete.bucket.item[data-bucket-id=${bucket.id}]`).on('click', e => { deleteBucket(bucket.id) })
}

async function renderCards(containerSelector, cards, bucketId, compact = false) {
    let dark = getDarkMode()
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
                                <div class="edit card item" data-card-id="${card.id}"><i class="edit icon"></i>${gettext('Edit this card')}</div>
                                <div class="delete card item" data-card-id="${card.id}"><i class="delete icon"></i>${gettext('Delete this card')}</div>
                                ${FEATURES.time_entries ? `<div class="divider"></div>
                                <div class="start-stop-timer card item" data-card-id="${card.id}"><i class="stopwatch icon"></i>${gettext('Start/stop timer')}</div>
                                <div class="edit-time-entries card item" data-card-id="${card.id}"><i class="history icon"></i>${gettext('Edit time entries')}</div>` : ''}
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
        `)
        let extraContent = $(containerSelector).find(`.extra.content[data-card-id=${card.id}]`)
        let tagsContainer = $(containerSelector).find(`.meta .tags[data-card-id=${card.id}]`)
        if (card.total_time > 0 && FEATURES.time_entries) {
            extraContent.append(`
                <span class="ui right floated ${card.is_running ? 'red ' : ''} text" style="font-size: 85%;">
                    <a class="start-stop-timer cardlet" data-card-id="${card.id}" data-content="${card.is_running ? gettext('Stop timer') : gettext('Start timer')}" data-variation="tiny basic">
                        ${card.is_running ? '<i class="stop circle icon"></i>' : '<i class="play circle icon"></i>'}
                    </a>
                    <span class="total-time noselect cardlet" data-card-id="${card.id}" data-time="${card.total_time}" data-start="${new Date()}" data-content="${gettext('Total tracked time.')}" data-variation="tiny basic">
                        ${str(card.total_time)}
                    </span>
                </span>
            `)
        }
        if (card.comments > 0) {
            extraContent.prepend(`
                <span class="ui left floated text noselect cardlet" style="font-size: 85%; margin-right: .5em;" data-title="${gettext('Comments')}" data-content="${card.comments}" data-variation="tiny basic">
                    <i class="comment icon"></i>${card.comments}
                </span>
            `)
        }
        if (card.total_files > 0) {
            extraContent.prepend(`
                <span class="ui left floated text noselect cardlet" style="font-size: 85%; margin-right: .5em;" data-title="${gettext('Attached files')}" data-content="${card.total_files}" data-variation="tiny basic">
                    <i class="paperclip icon"></i>${card.total_files}
                </span>
            `)
        }
        if (card.total_items > 0) {
            extraContent.prepend(`
                <span class="ui left floated text noselect cardlet" style="font-size: 85%; margin-right: .5em;" data-title="${gettext('Checklist items')}" data-content="${interpolate(ngettext('%s checked, %s in total.', '%s checked, %s in total.', card.checked_items), [card.checked_items, card.total_items])}" data-variation="tiny basic">
                    <i class="tasks icon"></i>${card.checked_items}/${card.total_items}
                </span>
            `)
        }
        if (card.due_date !== null) {
            extraContent.prepend(`
                <span class="ui left floated${overdue ? ' red' : ''} text noselect cardlet" style="font-size: 85%; margin-right: .5em;" data-title="Due date" data-content="${dueDate.toLocaleDateString(LANGUAGE_CODE)}${overdue ? gettext(' - This card is overdue!') : ''}" data-variation="tiny red basic"><i class="calendar day icon"></i></span>
            `)
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
        initializeCardButtons(bucketId, card, compact)
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

async function initializeCardButtons(bucketId, card, compact) {
    $(`.ui.progress[data-card-id=${card.id}]`).progress()
    $('.cardlet').popup()
    $(`.ui.dropdown[data-card-id=${card.id}]`).dropdown({ action: 'hide' })
    $(`.card-name[data-card-id=${card.id}]`).on('click', e => { showCardModal(card, bucketId, compact) })
    $(`.edit.card.item[data-card-id=${card.id}]`).on('click', e => { showCardModal(card, bucketId, compact) })
    $(`.card-el[data-card-id=${card.id}]`).on('dblclick', e => { showCardModal(card, bucketId, compact) })
    $(`.delete.card.item[data-card-id=${card.id}]`).on('click', e => { deleteCard(card.id, bucketId, compact) })
    $(`.start-stop-timer[data-card-id=${card.id}]`).on('click', e => { startStopTimer(card.id, bucketId, compact) })
    $(`.edit-time-entries[data-card-id=${card.id}]`).on('click', e => { showTimeEntriesModal(card.id, bucketId, compact) })
    $(`.card-status.icon[data-card-id=${card.id}]`).on('click', e => {
        toggleCardStatus(card.id, bucketId, $(e.target).attr('data-status'), compact)
    })
}

async function startTimerAnimation(cardId) {
    if (intervals.map(e => e.card).includes(cardId)) { return }
    intervals.push(
        {
            card: cardId,
            interval: setInterval(() => { incrementSecond(cardId) }, 1000)
        }
    )
}

async function stopTimerAnimation(cardId) {
    intervalIndex = intervals.findIndex(i => i.card == cardId)
    if (intervalIndex > -1) {
        clearInterval(intervals[intervalIndex].interval)
        intervals.splice(intervalIndex, 1)
    }
}

async function renderFiles(modal, bucketId, cardId, files) {
    for (f of files) {
        extension = f.extension
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
        `)
        $(`.image[data-file-id=${f.id}]`).dimmer({ on: 'hover' })
        $(`.delete-file[data-file-id=${f.id}]`).off().on('click', e => {
            id = $(e.target).attr('data-file-id')
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
                        on: 'now',
                        method: 'DELETE',
                        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/files/${id}/`,
                        stateContext: $(`.ui.special.card.img-card-file[data-file-id=${id}]`),
                        successTest: r => r != 0,
                        onSuccess(r) {
                            $(`.ui.special.card.img-card-file[data-file-id=${id}]`).remove()
                            cardEdited = true
                        },
                    })
                }
            }).modal('show')
        })
    }
}

function renderItems(containerSelector, items, bucketId, cardId) {
    let dark = getDarkMode()
    $(containerSelector).empty()
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
        `)
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
        $(containerSelector).append(`
            <div class="ui header">
                ${gettext('No time entries for this card.')}
            </div>
        `)
        return
    }
    timeEntries.forEach(timeEntry => {
        $(containerSelector).append(`
            <div data-time-entry-id="${timeEntry.id}" class="ui form ${dark ? 'inverted' : ''} segment">
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
        `)
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
            $(containerSelector).append(`
                <div class="${dark ? 'inverted' : ''} comment">
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
            `)
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
            $(containerSelector).append(`
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
            `)
        }
        $(`.mention`).popup()
    })
}

async function renderTags(container, tags) {
    for (tag of tags) {
        if (tag.icon !== null) {
            container.append(`
                <span class="ui mini ${tag.color ? tag.color.name.toLowerCase() : ''} label"><i class="${tag.icon.markup} icon"></i> ${tag.name}</span>
            `)
        } else {
            container.append(`
                <span class="ui mini ${tag.color ? tag.color.name.toLowerCase() : ''} label">${tag.name}</span>
            `)
        }
    }
}

async function renderAssignees(container, assignees, borderColor = null) {
    let dark = getDarkMode()
    if (borderColor === null) {
        for (user of assignees) {
            container.append(`
                <img data-username="${user.username}" data-content="${user.username}" data-variation="basic" class="ui avatar mini image assignee${dark ? ' dark' : ''}" src="${user.profile.avatar === null ? PLACEHOLDER_AVATAR : user.profile.avatar}"">
            `)
            $(`img[data-username='${user.username}']`).popup()
        }
    } else {
        for (user of assignees) {
            container.append(`
                <img data-username="${user.username}" data-content="${user.username}" data-variation="basic" class="ui avatar mini image assignee${dark ? ' dark' : ''}" src="${user.profile.avatar === null ? PLACEHOLDER_AVATAR : user.profile.avatar}" style="border-color: ${borderColor}">
            `)
            $(`img[data-username='${user.username}']`).popup()
        }
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

function insertLinksAndMentions(text) {
    function getIndicesOf(searchStr, str, caseSensitive) {
        var searchStrLen = searchStr.length
        if (searchStrLen == 0) {
            return []
        }
        var startIndex = 0, index, indices = []
        if (!caseSensitive) {
            str = str.toLowerCase()
            searchStr = searchStr.toLowerCase()
        }
        while ((index = str.indexOf(searchStr, startIndex)) > -1) {
            indices.push(index)
            startIndex = index + searchStrLen
        }
        return indices
    }
    text = text.replace(
        /(https?:\/\/)([^ ]+)/g,
        '<a target="_blank" href="$&">$2</a>'
    )
    var newText = text
    for (user of allowedUsers) {
        username = `@${user.username}`
        usernameIndices = getIndicesOf(username, text)
        validIndices = []
        offset = 0
        for (index of usernameIndices) {
            nextChar = text.substr(index + username.length, 1)
            if (",.!? ".includes(nextChar)) {
                validIndices.push(index - offset)
                newText = newText.substr(0, index - offset) + newText.substr(index - offset + username.length)
                offset += username.length
            }
        }
        offset = 0
        for (index of validIndices) {
            avatar = user.profile.avatar !== null ? user.profile.avatar : PLACEHOLDER_AVATAR
            span = `<span class="mention" data-html="<img class='ui avatar image' src='${avatar}'><span><b>${user.username}</b></span><p>${user.email}</p>" data-variation="tiny">@${user.username}</span>`
            newText = newText.substr(0, index + offset)
                + span
                + newText.substr(index + offset)
            offset += span.length
        }
        text = newText
    }
    return newText
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

async function getBuckets(compact = false, width) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/`,
        onSuccess(r) {
            renderBuckets(
                containerSelector = '#board',
                buckets = r,
                compact = compact,
                width = width
            )
        }
    })
}

async function getCards(bucketId, compact = false) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/`,
        stateContext: `.bucket-el[data-bucket-id=${bucketId}]`,
        onSuccess: r => {
            updateBucketTimetamp(bucketId)
            renderCards(
                containerSelector = `#bucket-${bucketId}`,
                cards = r,
                bucketId = bucketId,
                compact = compact
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
    var tags = []
    $.ajax({
        on: 'now',
        async: false,
        throttleFirstRequest: false,
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/`,
        method: 'GET',
        cache: false,
    })
        .done(r => { tags = r })
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

function generateAvatar(text, foregroundColor = "white", backgroundColor = "black") {
    const w = 200
    const canvas = document.createElement("canvas")
    const ctx = canvas.getContext("2d")

    canvas.width = w
    canvas.height = w

    // Draw background
    ctx.fillStyle = backgroundColor
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // Draw text
    var fontsize = w * 2 / text.length
    do {
        fontsize -= w / 100
        ctx.font = `bold ${fontsize}px Lato,'Helvetica Neue',Arial,Helvetica,sans-serif`
    } while (ctx.measureText(text).width > w * .8)
    ctx.fillStyle = foregroundColor
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.fillText(text, canvas.width / 2, canvas.height / 2)

    return canvas.toDataURL("image/png")
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
    })
    dropdown.dropdown('refresh').dropdown({
        placeholder: gettext('Select tags to for card'),
        values: tags,
        clearable: true,
        allowAdditions: false,
        forceSelection: false,
        inverted: true, 
        onLabelCreate: (value, text) => {
            var el = $(text)
            el.append('<i class="delete icon"></i>')
            return el
        },
    })
    if (card) {
        dropdown.dropdown('set exactly', card.tag.map(tag => tag.name))
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
    })
    if (card) {
        dropdown.dropdown('set exactly', card.assigned_to.map(user => user.username))
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
    )
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

function showCardModal(card = null, bucketId, compact) {
    let create = card === null
    let dark = getDarkMode()
    const modal = $('.ui.card-form.modal')
    modal.off().form('reset')
    modal.find('.card-files').val('')
    modal.find('.files-container').empty()

    if (dark) {
        modal.find('.comments-segment.segment').addClass('inverted')
        modal.find('#card-comments').addClass('inverted')
        modal.find('.checklist.segment').addClass('inverted')
        modal.find('.files.segment').addClass('inverted')
        modal.find('.add-item.input').addClass('inverted')
        modal.find('.add-item.input').addClass('inverted')
        modal.find('.ui.dividing.header').addClass('inverted')
    } else {
        modal.find('.comments-segment.segment').removeClass('inverted')
        modal.find('#card-comments').removeClass('inverted')
        modal.find('.checklist.segment').removeClass('inverted')
        modal.find('.files.segment').removeClass('inverted')
        modal.find('.add-item.input').removeClass('inverted')
        modal.find('.ui.dividing.header').removeClass('inverted')
    }

    if (card) { populateModal(modal, card) }

    modal.modal({
        restoreFocus: false,
        autofocus: false,
        transition: 'scale',
        duration: 400,
        onShow: () => {
            cardEdited = false
            modal.find('.scrolling.content').animate({ scrollTop: 0 })
            modal.find('.ui.card-due-date.calendar').calendar({
                type: 'date',
                today: true,
                formatInput: true,
                formatter: {
                    date: (date, settings) => {
                        if (!date) return ''
                        return date.toLocaleDateString(LANGUAGE_CODE)
                    }
                }
            })
        },
        onHidden: () => {
            if (cardEdited) { getCards(bucketId, compact) }
            $('.checklist-drake').empty()
            clearModal(modal)
        },
        onApprove: el => {
            modal.form('validate form')
            if (!modal.form('is valid')) {
                return false
            }
            var data = {
                name: modal.find('input[name=name]').val(),
                description: modal.find('textarea[name=description]').val(),
                bucket: bucketId,
            }
            if (FEATURES.status) {
                data['status'] = modal.find('.ui.status.dropdown')?.dropdown('get value')
            }
            if (FEATURES.color) {
                data['color'] = modal.find('.ui.card-color.dropdown')?.dropdown('get value')
            }
            if (FEATURES.tags) {
                tagsString = modal.find('.ui.tags.dropdown')?.dropdown('get value')
                tags = tagsString.split(",").map(tag => ({ name: tag }))
                data['tag'] = JSON.stringify(tags)
            }
            if (FEATURES.assignees) {
                assigneesString = modal.find('.ui.assigned_to.dropdown')?.dropdown('get value')
                assignees = assigneesString?.split(",").map(username => ({ username: username }))
                data['assigned_to'] = JSON.stringify(assignees)
            }
            if (FEATURES.dueDate) {
                dueDate = modal.find('.ui.card-due-date.calendar')?.calendar('get date') // If not null, dueDate is a Date object
                if (dueDate !== null) { data['due_date'] = dueDate.toISOString().split("T")[0] } // Convert to string in correct format
            }
            if (create) {
                method = 'POST'
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/`
                data['order'] = 0
            } else {
                method = 'PUT'
                id = modal.find('input[name=id]').val()
                data['order'] = $(`.card-el[data-card-id=${card.id}]`).index() + 1
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${id}/`
            }

            $.api({
                on: 'now',
                url: url,
                method: method,
                data: data,
                onSuccess(r) {
                    if (FEATURES.files) {
                        var files = modal.find('.card-files')[0]?.files
                        if (files.length > 0) {
                            var cardId = create ? r.id : card.id
                            for (f of files) {
                                var fd = new FormData()
                                fd.append('file', f)
                                attachFile(fd, bucketId, cardId)
                            }
                        }
                    }
                    getCards(bucketId, compact)
                }
            })
        }
    }).modal('show')

    initializeTagsDropdown(modal.find('.ui.tags.dropdown'), card)
    initializeUsersDropdown(modal.find('.ui.assigned_to.dropdown'), card)

    modal.submit(e => {
        e.preventDefault()
        modal.find('.positive.button').click()
    })

    modal.find('.manage-tags').off().on('click', e => {
        selectedTags = modal.find('.ui.tags.dropdown').dropdown('get value').split(',')
        showManageTagsModal(
            true,
            true,
            () => {
                initializeTagsDropdown(modal.find('.ui.tags.dropdown'))
                modal.find('.ui.tags.dropdown').dropdown('set exactly', selectedTags)
            },
        )
    })

    if (!create) {
        if (FEATURES.files) {
            getFiles(modal, bucketId, card.id)
        }
        if (FEATURES.comments) {
            modal.find('#suggest-comment').val('')
            initializeSuggest()
            loadComments(card, bucketId)
        }
        if (FEATURES.checklist) {
            loadChecklistItems(card, bucketId)
        }
    }
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

function toggleCardStatus(cardId, bucketId, currentStatus, compact) {
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
        type: 'PATCH',
        url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/`,
        data: { status: code },
        onSuccess(r) {
            $('body').toast({
                title: gettext('Card status changed'),
                message: interpolate(gettext('Card was marked as %s'), [`<strong>${text}<i class="${icon} icon"></i></strong>`]),
                showProgress: 'bottom'
            })
            getCards(bucketId, compact)
        },
    })
}

function showBucketModal(bucket = null) {
    var create
    const modal = $('.ui.bucket-form.modal')
    modal.form('reset')
    modal.off()
    if (bucket != null) {
        create = false
        modal.find('input[name=id]').val(bucket.id)
        modal.find('input[name=name]').val(bucket.name)
        modal.find('textarea[name=description]').val(bucket.description)
        modal.find('.ui.auto-status.dropdown').dropdown('set selected', bucket.auto_status)
        modal.find('.ui.color.dropdown').dropdown('set selected', bucket.color !== null ? bucket.color.id : '')
    } else {
        create = true
        modal.find('input[name=id]').val('')
        modal.find('input[name=name]').val('')
        modal.find('textarea[name=description]').val('')
        modal.find('.ui.auto-status.dropdown').dropdown('set selected', 'N')
        modal.find('.ui.color.dropdown').dropdown('clear')
    }
    modal.modal({
        restoreFocus: false,
        autofocus: false,
        transition: 'scale',
        duration: 400,
        onApprove(el) {
            modal.form('validate form')
            if (!modal.form('is valid')) {
                return false
            }
            name = modal.find('input[name=name]').val()
            description = modal.find('textarea[name=description]').val()
            autoStatus = modal.find('.ui.auto-status.dropdown').dropdown('get value')
            color = modal.find('.ui.color.dropdown').dropdown('get value')
            if (create === true) {
                method = 'POST'
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/`
                order = 0
            } else {
                id = modal.find('input[name=id]').val()
                order = $(`.bucket-el[data-bucket-id=${bucket.id}]`).index() + 1
                method = 'PUT'
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${id}/`
            }
            $.api({
                on: 'now',
                method: method,
                url: url,
                data: {
                    name: name,
                    board: BOARD_ID,
                    description: description,
                    auto_status: autoStatus,
                    color: color,
                    order: order,
                },
                onSuccess(r) {
                    loadBoard()
                }
            })
        }
    })
    modal.submit(e => {
        e.preventDefault()
        modal.find('.positive.button').click()
    })
    modal.modal('show')
}

function showTimeEntriesModal(cardId, bucketId, compact) {
    const modal = $('#time-entries.modal')
    modal.modal({
        autofocus: false,
        onShow() {
            modal.addClass('loading')
            getTimeEntries(bucketId, cardId)
        },
        onVisible() {
            modal.removeClass('loading')
        },
        onHidden() {
            getCards(bucketId, compact)
            modal.find('.content').empty()
        },
    }).modal('show')
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

function deleteCard(cardId, bucketId, compact) {
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
                        getCards(bucketId, compact)
                    }
                })
            }
        })
        .modal('show')
}

function startStopTimer(cardId, bucketId, compact) {
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
            getCards(bucketId, compact)
        }
    })
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
    `)
    let iconDropdown = $(`.tag-icon.new-tag.dropdown`)
    iconDropdown.dropdown({
        placeholder: gettext('Icon'),
        values: ICON_VALUES,
        context: '.tags.modal .content',
    })
    let colorDropdown = $(`.tag-color.new-tag.dropdown`)
    colorDropdown.dropdown({
        placeholder: gettext('Color'),
        values: COLOR_VALUES,
        context: '.tags.modal .content',
    })
    el.find('.delete.button.new-tag').off().click(e => {
        $(e.target).closest('form').remove()
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
    `)
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
        }).modal('show')
    })
}

async function showManageTagsModal(allowMultiple = false, fromCardModal = false, callback = undefined) {
    $('.ui.sidebar').sidebar('hide')
    let tagsModal = $('.ui.tags.modal')
    tagsModal.modal({
        autofocus: false,
        allowMultiple: false,
        onShow() {
            var el = tagsModal.find('.content')
            el.empty()
            el.append(`
                <div class="ui new-tag icon labeled green button" style="margin-bottom: 1em;">
                    <i class="add icon"></i>
                    ${gettext('Add new tag')}
                </div>
            `)
            el.find('.new-tag').off().click(() => {
                addNewTagInput(el)
            })
            $.api({
                on: 'now',
                method: 'GET',
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/tags/`,
                onSuccess(r) {
                    for (tag of r) {
                        renderTagForms(el, tag)
                    }
                }
            })
        },
        onApprove() {
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
                    }
                })
            })
            if (fromCardModal) {
                callback()
            }
            loadBoard()
        },
    })
    tagsModal.modal('show')
}

function getSearchCardsDropdownValues() {
    var tags = $('.tags .label').toArray().map(tag => $(tag).text().trim())
    tags = [...new Set(tags)]
    tags = tags.map(tag => ({
        icon: 'hashtag',
        value: '#' + tag,
        name: tag,
    }))
    var users = $('.assignees .image').toArray().map(user => $(user).attr('data-username'))
    users = [...new Set(users)]
    users = users.map(user => ({
        icon: 'at',
        value: '@' + user,
        name: user,
    }))
    var values = [...new Set([...tags, ...users])]
    return values
}

async function filterCards() {
    for (card of $('.card-el')) {
        if (!isCardOnFilter($(card))) {
            $(card).hide()
        } else {
            $(card).show()
        }
    }
}

function isCardOnFilter(cardEl, selector = '.ui.search-cards.dropdown', filterMode = 'or') {
    var name = cardEl.find('.card-name').text().trim()
    var tags = cardEl.find('.tags .label')
        .toArray()
        .map(tag => '#' + $(tag).text().trim())
    var users = cardEl.find('.assignees .image')
        .toArray()
        .map(user => '@' + $(user).attr('data-username'))
    var cardItems = [...new Set([name, ...tags, ...users])]
    var queryItems = $(selector).dropdown('get value').split(',')

    if (queryItems.length == 1 && queryItems[0] == '') { return true }

    if (filterMode.toLowerCase() === 'and') {
        result = queryItems.every(i => cardItems.includes(i))
    } else if (filterMode.toLowerCase() === 'or') {
        result = queryItems.some(i => cardItems.includes(i))
    }
    return result
}

function initializeSearchCardsDropdown(selector = '.ui.search-cards.dropdown') {
    $(selector).dropdown({
        clearable: true,
        allowAdditions: true,
        forceSelection: false,
        match: 'value',
        direction: 'downward',
        placeholder: gettext('Filter cards'),
        onChange(value, text, $choice) {
            filterCards(value)
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
    })
}

function initializeColorDropdown() {
    $('.ui.card-color.dropdown').dropdown({
        clearable: true,
        placeholder: gettext('Select a color theme'),
        values: colorsForDropdown,
    })
}