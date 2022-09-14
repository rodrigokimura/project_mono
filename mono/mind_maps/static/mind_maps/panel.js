let pos = { top: 0, left: 0, x: 0, y: 0 };

const CONTAINER = '#container'
const PANEL = `${CONTAINER} .panel`

function initializePanel(width, height) {
    $(CONTAINER).css('overflow', 'scroll')
    $(CONTAINER).empty()
    $(CONTAINER).append(`<div class="panel"></div>`)
    $(PANEL).css('height', height * scale)
    $(PANEL).css('width', width * scale)
    $(PANEL).click(e => {
        if (!$(e.target).hasClass('panel')) return
        Node.deselectAll()
    })
    $(CONTAINER).on('mousedown', mouseDownHandler);
    $(PANEL).on('dragover', e => {
        e.preventDefault()
        e.stopPropagation()
    })
}

const mouseDownHandler = function (e) {
    if (!$(e.target).hasClass('panel')) return
    if (e.button !== 0) return  // only left click can drag
    pos = {
        // The current scroll
        left: $(CONTAINER)[0].scrollLeft,
        top: $(CONTAINER)[0].scrollTop,
        // Get the current mouse position
        x: e.clientX,
        y: e.clientY,
    }
    $(CONTAINER)[0].style.cursor = 'grabbing'
    $(CONTAINER)[0].style.userSelect = 'none'

    document.addEventListener('mousemove', mouseMoveHandler)
    document.addEventListener('mouseup', mouseUpHandler)
}

const mouseMoveHandler = function (e) {
    // How far the mouse has been moved
    const dx = e.clientX - pos.x
    const dy = e.clientY - pos.y

    // Scroll the element
    $(CONTAINER)[0].scrollTop = pos.top - dy
    $(CONTAINER)[0].scrollLeft = pos.left - dx
}

const mouseUpHandler = function () {
    document.removeEventListener('mousemove', mouseMoveHandler)
    document.removeEventListener('mouseup', mouseUpHandler)

    $(CONTAINER)[0].style.cursor = 'grab'
    $(CONTAINER)[0].style.removeProperty('user-select')
}
