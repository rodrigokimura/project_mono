class Display {
    constructor(elementId, text) {
        this.elementId = elementId
        this.text = text
        this.render()
        this.chars = ""
        this.curIndex = 0
    }
    render() {
        const DISPLAY = $(this.elementId)

        DISPLAY.append(`<div class="line">${this.text.split("").map((s, i) => `<span class="display-char" data-index="${i}">${s}</span>`).join("")}</div>`)

    }
    push(correct = true) {
        $(`span[data-index="${this.curIndex}"]`).addClass(correct ? "correct" : "incorrect")
        this.curIndex++
    }
    pop() {
        let charEl = $(`span[data-index="${this.curIndex - 1}"]`)
        charEl?.removeClass("correct")
        charEl?.removeClass("incorrect")
        if (this.curIndex > 0) this.curIndex--
    }
}
