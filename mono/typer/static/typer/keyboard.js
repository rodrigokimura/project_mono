class StaggeredLayout {
    constructor(elementId) {
        this.element = $(elementId)
        this.rows = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ç'],
            ['\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.'],
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
                key = key.toString()
                html += `<div class="kb-key" data-key="${key}">${key.toUpperCase()}</div>`
            })
            html += `</div>`
        })
        this.element.html(
            `<div class="kb-container">
                <div class="kb-column">
                    ${html}
                </div>
            </div>`
        )
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
        key = key.toString().toLowerCase()
        $(`.kb-key[data-key="${key}"]`).addClass("pressed")
    }
    async release(key) {
        key = key.toString().toLowerCase()
        $(`.kb-key[data-key="${key}"]`).removeClass("pressed")
    }
    async releaseAll() {
        $(`.kb-key`).removeClass("pressed")
    }
}