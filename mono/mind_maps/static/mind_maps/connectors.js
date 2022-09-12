class Connector {
    constructor(node1, node2) {
        this.node1 = node1
        this.node2 = node2
    }
    static get() {
        return $(`#${this.id} input`)[0], $(`#${this.id} input`)
    }
    draw() {
        let x1 = this.node1.position[0]
        let y1 = this.node1.position[1]
        let x2 = this.node2.position[0]
        let y2 = this.node2.position[1]
        let angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI
        let length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))

        this.node1.connector = this
        this.el = $(`
            <div class="connector" data-nodes="${this.node1.id}|${this.node2.id}" style="width: ${length * scale}px; left: ${x1 * scale}px; top: ${y1 * scale}px; transform: rotate(${angle}deg);">
            </div>
        `)
        this.el.height(this.node1.borderSize * scale)
        this.el.css('background-color', this.node1.colors.border)
        $(PANEL).append(this.el)
    }
    redraw() {
        this.erase()
        this.draw()
    }
    erase() {
        this.el.remove()
    }
    delete() {
        this.erase()
    }
    show() { this.el.show() }
    hide() { this.el.hide() }
}