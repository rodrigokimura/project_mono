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

function getActiveCard() {
    let result = sessionStorage.getItem('activeCard')
    if (result === null) return null
    return JSON.parse(result)
}

function setActiveCard(cardId, bucketId) {
    sessionStorage.setItem(
        'activeCard',
        JSON.stringify(
            {
                card: cardId,
                bucket: bucketId,
            }
        )
    )
}
