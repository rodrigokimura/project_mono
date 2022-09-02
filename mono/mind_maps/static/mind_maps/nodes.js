class Node {
    constructor(name, parent = null) {
        this.id = self.crypto.randomUUID()
        this.name = name
        this.parent = parent
        this.position = [0, 0]
        this.size = [100, 30]
    }
    get width() { return this.size[0] }
    get height() { return this.size[1] }

    static get(id) {
        for (let node of nodes) {
            if (node.id === id) {
                return node
            }
        }
        return null
    }
    covers(x, y) {
        return [
            x >= (this.position[0] - this.width / 2),
            x <= (this.position[0] + this.width / 2),
            y <= (this.position[1] + this.height / 2),
            y >= (this.position[1] - this.height / 2),
        ].every(v => v === true)
    }
    draw() {
        this.position = (new Positioner(this)).find()
        var x = this.position[0] - this.width / 2
        var y = this.position[1] - this.height / 2
        let nodeEl = $(`
            <div class="node" style="display: inline; position: absolute; width: ${this.width}px; height: ${this.height}px; left: ${x}px; top: ${y}px;">
                <input type="text" placeholder="Node name" value="${this.name}" style="width: 100%; height: 100%;">
            </div>
        `)
        $(PANEL).append(nodeEl)
    }
}