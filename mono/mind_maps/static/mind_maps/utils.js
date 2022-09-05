async function toast(message) {
    $('body').toast({
        message: message,
        showProgress: 'bottom',
        closeIcon: true,
    })
}

function createPanel() {
    $(CONTAINER).css('overflow', 'scroll')
    $(CONTAINER).empty()
    $(CONTAINER).append(`
        <div class="panel" style="height: ${panel.height}px; width: ${panel.width}px;">
        </div>
    `)
}

function centralize() {
    let maxX = Math.max(...nodes.map(n => n.position[0]))
    let minX = Math.min(...nodes.map(n => n.position[0]))
    let maxY = Math.max(...nodes.map(n => n.position[1]))
    let minY = Math.min(...nodes.map(n => n.position[1]))
    let dx = (maxX + minX) / 2 - panel.width / 2
    let dy = (maxY + minY) / 2 - panel.height / 2
    $(CONTAINER).animate({
        scrollLeft: (panel.width - $(CONTAINER)[0].clientWidth) / 2 + dx,
        scrollTop: (panel.height - $(CONTAINER)[0].clientHeight) / 2 + dy,
    }, 500)
}

function getConfigAttr(config, attr, fallback) {
    try {
        return config[attr] || fallback
    }
    catch (err) {
        return fallback
    }
}

function setSelectionRange(input, selectionStart, selectionEnd) {
    if (input.setSelectionRange) {
        input.focus()
        input.setSelectionRange(selectionStart, selectionEnd)
    }
    else if (input.createTextRange) {
        var range = input.createTextRange()
        range.collapse(true)
        range.moveEnd('character', selectionEnd)
        range.moveStart('character', selectionStart)
        range.select()
    }
}

function setCaretToPos(input, pos) {
    setSelectionRange(input, pos, pos)
}