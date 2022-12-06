const CONTAINER = '#container'
const PANEL = `${CONTAINER} .panel`

let cursorPosition = { top: 0, left: 0, x: 0, y: 0 }
let selectionArea = $('<div class="selection-area"></div>')


function initializePanel(width, height) {
    $(CONTAINER).css('overflow', 'scroll')
    $(CONTAINER).empty()
    $(CONTAINER).append(`<div class="panel"></div>`)
    $(PANEL).css('height', height * scale)
    $(PANEL).css('width', width * scale)
    $(PANEL).css('background-color', panel.color)
    $(PANEL).click(e => {
        if (!$(e.target).hasClass('panel')) return
        Node.deselectAll()
    })
    $(CONTAINER).off().on('mousedown', startDrag)
    $(PANEL).on('dragover', e => {
        e.preventDefault()
        e.stopPropagation()
    })
}

function startDrag(e) {
    if (!$(e.target).hasClass('panel')) return
    if (e.button !== 0) return  // only left click can drag
    cursorPosition = {
        // The current scroll
        left: $(CONTAINER)[0].scrollLeft,
        top: $(CONTAINER)[0].scrollTop,
        // Get the current mouse position
        x: e.clientX,
        y: e.clientY,
    }
    if (!e.ctrlKey) {
        $(CONTAINER)[0].style.cursor = 'grabbing'
        $(CONTAINER)[0].style.userSelect = 'none'

        $(document).on('mousemove', scrollPanel)
    } else {
        // Draw selection area
        $(PANEL).append(selectionArea)
        $(document).on('mousemove', drawSelectionArea)
    }
    $(document).on('mouseup', resetEventHandlers)
}

function scrollPanel(e) {
    const dx = e.clientX - cursorPosition.x
    const dy = e.clientY - cursorPosition.y

    // Scroll the element
    $(CONTAINER)[0].scrollTop = cursorPosition.top - dy
    $(CONTAINER)[0].scrollLeft = cursorPosition.left - dx
}

function resetEventHandlers() {
    $(document).off('mousemove')
    $(document).off('mouseup')

    $(CONTAINER)[0].style.cursor = 'grab'
    $(CONTAINER)[0].style.removeProperty('user-select')

    selectionArea.hide()
    $(PANEL).find('.selection-area').remove()
}

function drawSelectionArea(e) {
    selectionArea.show()
    const dx = e.clientX - cursorPosition.x
    const dy = e.clientY - cursorPosition.y
    selectionArea.width(Math.abs(dx))
    selectionArea.height(Math.abs(dy))
    selectionArea.css('left', cursorPosition.left + Math.min(e.clientX, cursorPosition.x))
    selectionArea.css('top', cursorPosition.top + Math.min(e.clientY, cursorPosition.y))
    selectionArea.css('border-color', getSelectionAreaDark() ? "rgba(0, 0, 0, 1)" : "rgba(255, 255, 255, 1)")
    selectionArea.css('background-color', getSelectionAreaDark() ? "rgba(0, 0, 0, 0.5)" : "rgba(255, 255, 255, 0.5)")
    nodes.forEach(node => {
        if (
            node.x * scale > cursorPosition.left + selectionArea.position().left
            && node.x * scale < cursorPosition.left + selectionArea.position().left + selectionArea.width()
            && node.y * scale > cursorPosition.top + selectionArea.position().top
            && node.y * scale < cursorPosition.top + selectionArea.position().top + selectionArea.height()
        ) {
            node.el.addClass('selected')
        } else {
            node.el.removeClass('selected')
        }
    })
}

function getSelectionAreaDark() {
    let [r, g, b] = rgbStringToArray($(PANEL).css('background-color'))
    // https://stackoverflow.com/a/3943023/112731
    return (r * 0.299 + g * 0.587 + b * 0.114) > 186
}

function rgbStringToArray(rgba) {
    return rgba.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+\.{0,1}\d*))?\)$/).slice(1).map(
        (n, i) => (i === 3 ? Math.round(parseFloat(n) * 255) : parseFloat(n))
    ).slice(0, 3)
}