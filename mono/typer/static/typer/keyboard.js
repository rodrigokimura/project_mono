class StaggeredLayout {
    constructor(elementId) {
        this.element = $(elementId)
        this.rows = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ç'],
            ['\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.']
        ]
        this.staggering = [
            0, .4, .8, .1
        ]
    }
    render() {
        let html = ``
        this.rows.forEach((row, i) => {
            html += `<div class="kb-row">`
            html += `<div class="kb-stagger" style="width: ${this.staggering[i] * 3}em"></div>`
            row.forEach(key => {
                html += `<div class="kb-key">${key}</div>`
            })
            html += `</div>`
        })
        this.element.html(`<div class="kb-container">${html}</div>`)
    }
}

class Keyboard {
    constructor(elementId) {
        this.elementId = elementId
        this.render()
    }
    render() {
        (new StaggeredLayout(this.elementId)).render()
    }
    async press(key) {
        $(`.kb-key:contains(${key})`).addClass("pressed")
    }
    async release(key) {
        $(`.kb-key:contains(${key})`).removeClass("pressed")
    }
}