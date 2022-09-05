class Node {
    constructor(name, parent = null) {
        this.id = self.crypto.randomUUID()
        this.name = name
        this.parent = parent
        this.position = [0, 0]
        this.size = [100, 30]
        this.editMode = false
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
    isRoot() {
        return this.parent === null && this === nodes[0]
    }
    covers(x, y) {
        return [
            x >= (this.position[0] - this.width / 2),
            x <= (this.position[0] + this.width / 2),
            y <= (this.position[1] + this.height / 2),
            y >= (this.position[1] - this.height / 2),
        ].every(v => v === true)
    }
    draw(reverseNext, reverseFirst) {
        this.position = (new Positioner(this, reverseNext, reverseFirst)).find()
        var x = this.position[0] - this.width / 2
        var y = this.position[1] - this.height / 2
        let nodeEl = $(`
            <div id="${this.id}" class="node" style="display: inline; position: absolute; width: ${this.width}px; height: ${this.height}px; left: ${x}px; top: ${y}px;">
                <input type="text" tabindex="-1"  placeholder="<No name>" value="${this.name}" style="width: 100%; height: 100%;">
            </div>
        `)
        $(PANEL).append(nodeEl)
        this.attachEvents(nodeEl)
    }
    attachEvents(nodeEl) {
        let inputEl = nodeEl.find('input')
        inputEl.keydown(e => {
            let editModeCommands = {
                13: () => { this.leaveEditMode() },
                9: () => { this.leaveEditMode() },
                27: () => { this.leaveEditMode() },
            }
            let normalCommands = {
                13: () => { this.createChild('', e.shiftKey).focus() },
                9: () => { this.createSibling('', e.shiftKey).focus() },
                46: () => { if (e.shiftKey) this.delete(!e.ctrlKey) },
                37: () => { this.selectNext('l') },
                38: () => { this.selectNext('u') },
                39: () => { this.selectNext('r') },
                40: () => { this.selectNext('d') },
                27: () => { this.blur() },
                113: () => { this.enterEditMode() },
            }
            if (this.editMode) {
                if (!e.keyCode in editModeCommands) return
                editModeCommands[e.keyCode]()
                return
            } else {
                if (!e.keyCode in normalCommands) return
                e.stopPropagation()
                e.preventDefault()
                normalCommands[e.keyCode]()
                return
            }
        })
        nodeEl.click(e => {
            e.preventDefault()
            e.stopPropagation()
            this.select()
        })
        inputEl.change(e => {
            this.name = e.target.value
            toast(`Node ${this.name} updated`)
        })
        inputEl.blur(e => {
            if (!this.name) this.delete()
            this.unselect()
        })
        nodeEl.on('dragstart', e => {
            console.log(e)
        })
    }
    createNode(name, parent, reverseNext, reverseFirst) {
        let node = new Node(name, parent)
        nodes.push(node)
        node.draw(reverseNext, reverseFirst)
        if (parent) {
            var connector = new Connector(node, parent)
            connector.draw()
            node.connector = connector
        }
        toast(`Node ${node.name} created`)
        return node
    }
    createChild(name, alt = false) {
        return this.createNode(name, this, false, alt)
    }
    createSibling(name, alt = false) {
        return this.createNode(name, this.parent, alt, false)
    }
    enterEditMode() {
        toast('Entering edit mode')
        this.editMode = true
        $(`#${this.id}`).removeClass('selected')
        $(`#${this.id} input`).css('caret-color', 'black')
        setCaretToPos($(`#${this.id} input`)[0], $(`#${this.id} input`).val().length)
    }
    leaveEditMode() {
        toast('Leaving edit mode')
        this.editMode = false
        $(`#${this.id}`).addClass('selected')
        $(`#${this.id} input`).css('caret-color', 'transparent')
        setCaretToPos($(`#${this.id} input`)[0], $(`#${this.id} input`).val().length)
    }
    focus() {
        $(`#${this.id} input`).focus()
    }
    blur() {
        $(`#${this.id} input`).blur()
    }
    select() {
        $(`#${this.id}`).addClass('selected')
        this.focus()
    }
    unselect() {
        $(`#${this.id}`).removeClass('selected')
    }
    delete(cascade = true) {
        if (this.isRoot()) {
            toast('Cannot delete root node')
            return
        }
        $(`#${this.id}`).remove()
        nodes = nodes.filter(node => node.id !== this.id)
        toast(`Node ${this.name} deleted`)
        this.connector.delete()
        delete this.connector
        this.parent.focus()
        if (cascade) {
            this.deleteChildren(cascade)
        }
    }
    deleteChildren(cascade = true) {
        for (let node of nodes) {
            if (node.parent === this) {
                node.delete(cascade)
            }
        }
    }
    distanceFrom(node) {
        return Math.round(Math.sqrt(
            Math.pow(this.position[0] - node.position[0], 2) +
            Math.pow(this.position[1] - node.position[1], 2)
        ))
    }
    selectNext(direction) {
        this.unselect()
        var attrMap = {
            l: [0, 'width', (a, b) => a - b, (a, b) => a < b],
            r: [0, 'width', (a, b) => a + b, (a, b) => a > b],
            u: [1, 'height', (a, b) => a - b, (a, b) => a < b],
            d: [1, 'height', (a, b) => a + b, (a, b) => a > b],
        }
        var positionIndex, attr, edgeFunc, comparisonFunc
        [positionIndex, attr, edgeFunc, comparisonFunc] = attrMap[direction]

        // filter nodes after the edge of this node
        var edge = edgeFunc(this.position[positionIndex], this[attr] / 2)
        var filteredNodes = nodes.filter(
            node => comparisonFunc(node.position[positionIndex], edge)
        )
        if (filteredNodes.length === 0) this.select()
        if (filteredNodes.length === 1) {
            filteredNodes[0].select()
            return
        }
        // find the closest node
        var closestNode = filteredNodes.sort(
            (a, b) => this.distanceFrom(a) - this.distanceFrom(b)
        )[0]
        closestNode.select()
    }
}