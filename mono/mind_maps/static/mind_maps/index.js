const CONTAINER = '#container'
const PANEL = '#container .panel'

var panel = {
    height: 1200,
    width: 1200,
}
var nodes = []


class Vector {
    constructor(...components) {
      this.components = components
    }
  
    add({ components }) {
      return new Vector(
        ...components.map((component, index) => this.components[index] + component)
      )
    }
    subtract({ components }) {
      return new Vector(
        ...components.map((component, index) => this.components[index] - component)
      )
    }
  }
  


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
}


function createPanel() {
    $(CONTAINER).css('overflow', 'scroll')
    $(CONTAINER).empty()
    $(CONTAINER).append(`
        <div class="panel" style="height: ${panel.height}px; width: ${panel.width}px;">
        </div>
    `)
    $(CONTAINER).animate({
        scrollTop: (panel.height - $(CONTAINER).height()) / 2,
        scrollLeft: (panel.width - $(CONTAINER).width()) / 2,
    }, 500)
}

function createNode(name, parent = null) {
    let node = new Node(name, parent)
    nodes.push(node)
    drawNode(node)
    toast('Node', `Node ${node.name} created`)
}

function drawNode(node) {
    let nodeEl = $(`
        <div class="node" style="display: inline; position: absolute; width: ${node.width}px; height: ${node.height}px;">
            <input type="text" placeholder="Node name" value="${node.name}" style="width: 100%; height: 100%;">
        </div>
    `)
    $(PANEL).append(nodeEl)
    if (node.parent === null) {
        let top = panel.height / 2
        let left = panel.width / 2
        node.position = [left, top]
        nodeEl.css('top', top - nodeEl.height() / 2)
        nodeEl.css('left', left - nodeEl.width() / 2)
    } else {
        let x = node.parent.position[0]
        let y = node.parent.position[1] + 150

        for (i = 0; i < 8; i++) {
            if (isPositionAvailable(node, x, y)) {
                node.position = [x, y]
                nodeEl.css('top', y - nodeEl.height() / 2)
                nodeEl.css('left', x - nodeEl.width() / 2)
            } else {
                let position = getNextPosition(i, node, x, y)
                console.log(position)
                x = position[0]
                y = position[1]
            }
        }
    }
}

function isPositionAvailable(node, x, y) {
    for (let other of nodes) {
        if (other === node) {
            continue
        }
        if (other.covers(x, y)) {
            return false
        }
    }
    return true
}

function getFirstPosition() {

}

function rotate(cx, cy, x, y, angle) {
    var radians = (Math.PI / 180) * angle
    var cos = Math.cos(radians)
    var sin = Math.sin(radians)
    var nx = (cos * (x - cx)) - (sin * (y - cy)) + cx
    var ny = (cos * (y - cy)) + (sin * (x - cx)) + cy
    return [Math.round(nx), Math.round(ny)];
}

function getNextPosition(i, node, x, y) {
    let cx = node.parent.position[0]
    let cy = node.parent.position[1]
    return rotate(cx, cy, x, y, 45)
}

function script() {
    createNode('Root')
    createNode('First child', nodes[0])
    createNode('Second child', nodes[0])
}