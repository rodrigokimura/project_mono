async function initializeBucketDragAndDrop() {
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

async function initializeCardDragAndDrop() {
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

async function initializeSearchCardsDropdown(selector = '.ui.search-cards.dropdown') {
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

async function initializeColorDropdown() {
    $('.ui.card-color.dropdown').dropdown({
        clearable: true,
        placeholder: gettext('Select a color theme'),
        values: colorsForDropdown,
    })
}

async function initializeDarkModeCheckbox() {
    $('.board-dark.checkbox').checkbox({
        onChecked: () => { setDarkMode(true) },
        onUnchecked: () => { setDarkMode(false) },
    })
    if (getDarkMode()) {
        $('.board-dark.checkbox').checkbox('set checked')
    }
}

async function initializeCompactModeCheckbox() {
    $('.board-compact.checkbox').checkbox({
        onChecked: () => { setCompactMode(true) },
        onUnchecked: () => { setCompactMode(false) },
    })
    if (getCompactMode()) {
        $('.board-compact.checkbox').checkbox('set checked')
    }
}

async function initializeBucketWidthSlider() {
    $('.ui.width.slider').slider({ 
        min: 100, 
        max: 500, 
        step: 100,
        onChange: changeBucketWidth,
    })
    $('.ui.width.slider').slider(
        'set value',
        getBucketWidth(),
        false,
    )
}

async function initializeBucketButtons(bucket) {
    $(`.ui.dropdown[data-bucket-id=${bucket.id}]`).dropdown({ action: 'hide' })
    $(`.add.card.item[data-bucket-id=${bucket.id}]`).on('click', e => { showCardModal(card = null, bucket.id) })
    $(`#bucket-${bucket.id}`).on('dblclick', e => {
        const isCard = $(e.target).parents('.card-el').length > 0
        if (!isCard) { showCardModal(card = null, bucket.id) }
    })
    $(`.edit.bucket.item[data-bucket-id=${bucket.id}]`).on('click', e => { showBucketModal(bucket) })
    $(`.delete.bucket.item[data-bucket-id=${bucket.id}]`).on('click', e => { deleteBucket(bucket.id) })
}

async function initializeCardButtons(bucketId, card) {
    $(`.ui.progress[data-card-id=${card.id}]`).progress()
    $('.cardlet').popup()
    $(`.ui.dropdown[data-card-id=${card.id}]`).dropdown({ action: 'hide' })
    $(`.card-name[data-card-id=${card.id}]`).on('click', e => { showCardModal(card, bucketId) })
    $(`.edit.card.item[data-card-id=${card.id}]`).on('click', e => { showCardModal(card, bucketId) })
    $(`.card-el[data-card-id=${card.id}]`).on('dblclick', e => { showCardModal(card, bucketId) })
    $(`.delete.card.item[data-card-id=${card.id}]`).on('click', e => { deleteCard(card.id, bucketId) })
    $(`.start-stop-timer[data-card-id=${card.id}]`).on('click', e => { startStopTimer(card.id, bucketId) })
    $(`.edit-time-entries[data-card-id=${card.id}]`).on('click', e => { showTimeEntriesModal(card.id, bucketId) })
    $(`.card-status.icon[data-card-id=${card.id}]`).on('click', e => {
        toggleCardStatus(card.id, bucketId, $(e.target).attr('data-status'))
    })
}

function initializeTagsDropdown(dropdown, card = undefined) {
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
        placeholder: gettext('Select tags for card'),
        values: tags,
        clearable: true,
        allowAdditions: false,
        forceSelection: false,
        inverted: true, 
        onLabelCreate(value, text) {
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