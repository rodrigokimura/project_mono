class Display {
    constructor(elementId, text) {
        this.elementId = elementId
        this.text = text
        this.render()
        this.chars = ""
        this.currentIndex = 0
    }
    render() {
        const DISPLAY = $(this.elementId)
        DISPLAY.append(
            this.text
                .split("")
                .map(
                    (s, i) => `<span class="${s === '\n' ? 'invisible' : ''} display-char" data-index="${i}">${s}</span>`
                )
                .join("")
        )
        this.#adjustHeight()
    }
    #adjustHeight() {
        const rowCount = this.text.split("\n").length
        const DISPLAY = $(this.elementId)
        DISPLAY.parent().css("margin", 0)
        DISPLAY.parent().css("height", DISPLAY.height() / rowCount * 4)
    }
    push(correct = true) {
        $(`span[data-index="${this.currentIndex}"]`).addClass(correct ? "correct" : "incorrect")
        this.currentIndex++
        this.#scrollToCurrent()
        this.#updateCursor()
    }
    pop() {
        let charEl = $(`span[data-index="${this.currentIndex - 1}"]`)
        charEl?.removeClass("correct")
        charEl?.removeClass("incorrect")
        if (this.currentIndex > 0) this.currentIndex--
        this.#scrollToCurrent()
        this.#updateCursor()
    }
    #getCurrentRow() {
        let rowCount = 1
        for (var i = 0; i < this.currentIndex; i++) {
            if (this.text[i] === "\n") rowCount++
        }
        return rowCount
    }
    #scrollToCurrent() {
        let currentRow = this.#getCurrentRow()
        let DISPLAY = $(this.elementId)
        let displayContainer = DISPLAY.parent()
        let rowHeight = DISPLAY.height() / this.text.split("\n").length
        let displayHeight = displayContainer.height()
        let scrollTop = displayContainer.scrollTop()
        let scrollBottom = scrollTop + displayHeight
        let rowTop = rowHeight * (currentRow - 1)
        let rowBottom = rowHeight * currentRow
        if (rowTop < scrollTop) {
            displayContainer.scrollTop(rowTop - rowHeight)
        } else if (rowBottom > scrollBottom) {
            displayContainer.scrollTop(rowBottom - displayHeight + rowHeight)
        }
    }
    #updateCursor() {
        $(`span.display-char`).removeClass("cursor")
        let charEl = $(`span.display-char[data-index="${this.currentIndex}"]`)
        charEl?.addClass("cursor")
    }
}
