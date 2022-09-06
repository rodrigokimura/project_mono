const CONTAINER = '#container'
const PANEL = '#container .panel'

var panel = {
    height: 1200,
    width: 2400,
}
var nodes = []

class Node {
    constructor(name, parent = null) {
        this.id = self.crypto.randomUUID()
        this.name = name
        this.parent = parent
        this.position = [0, 0]
        this.size = [100, 30]
        this.editMode = false
        this.connector = null
        this.metadata = {}
    }
    get width() { return this.size[0] }
    get height() { return this.size[1] }
    get children() {
        return nodes.filter(node => node.parent === this)
    }
    get inputConnectors() {
        return this.connector ? [this.connector] : []
    }
    get outputConnectors() {
        return this.children.map(child => child.connector)
    }
    get state() {
        let state = {
            id: this.id,
            name: this.name,
            parent: this.parent ? this.parent.id : null,
            position: this.position,
            size: this.size,
        }
        var st = JSON.stringify(state)
        var hash = 0, i, chr;
        if (st.length === 0) return hash
        for (i = 0; i < st.length; i++) {
            chr = st.charCodeAt(i)
            hash = ((hash << 5) - hash) + chr
            hash |= 0
        }
        return hash
    }
    static get(id) {
        for (let node of nodes) {
            if (node.id === id) {
                return node
            }
        }
        return null
    }
    static getOrCreate(id) {
        let node = Node.get(id)
        if (node) return node
        node = (new Node(''))
        node.id = id
        nodes.push(node)
        return node
    }
    static getRoot() {
        return nodes.filter(node => node.isRoot())
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
    autoPosition(reverseNext, reverseFirst) {
        this.position = (new Positioner(this, reverseNext, reverseFirst)).find()
    }
    draw() {
        var x = this.position[0] - this.width / 2
        var y = this.position[1] - this.height / 2
        let nodeEl = $(`
            <div id="${this.id}" draggable="true" class="node" style="width: ${this.width}px; height: ${this.height}px; left: ${x}px; top: ${y}px;">
                <input type="text" tabindex="-1"  placeholder="<No name>" value="${this.name}" style="width: 100%; height: 100%;">
            </div>
        `)
        $(PANEL).append(nodeEl)
        this.attachEvents(nodeEl)
        if (this.name) {
            this.autoWidth(this.name)
        }
    }
    drawConnectors() {
        if (this.parent) {
            (new Connector(this, this.parent)).draw()
        }
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
                13: () => { this.createChild('', e.shiftKey).enterEditMode().focus() },
                9: () => { this.createSibling('', e.shiftKey).enterEditMode().focus() },
                46: () => { if (e.shiftKey) this.delete(!e.ctrlKey) },
                37: () => { this.selectNext('l') },
                38: () => { this.selectNext('u') },
                39: () => { this.selectNext('r') },
                40: () => { this.selectNext('d') },
                27: () => { this.blur() },
                113: () => { this.enterEditMode() },
            }
            if (this.editMode) {
                if (e.keyCode === 9) e.preventDefault()  // avoid tabbing out of the input
                if (!(e.keyCode in editModeCommands)) return
                editModeCommands[e.keyCode]()
                return
            } else {
                e.preventDefault()
                if (!(e.keyCode in normalCommands)) return
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
            if (e.target.value.length > 90) {
                toast('Node name too long')
                e.target.value = e.target.value.slice(0, 90)
                this.autoWidth(e.target.value)
            }
            this.name = e.target.value
            toast(`Node ${this.name} updated`)
        })
        inputEl.on('input', e => {
            this.autoWidth(e.target.value)
        })
        inputEl.blur(e => {
            if (!this.name) this.delete()
            this.unselect()
        })
        nodeEl.on('dragstart', e => {
            e.target.style.opacity = '0.4'
            this.metadata = {
                offsetX: e.offsetX,
                offsetY: e.offsetY,
            }
        })
        nodeEl.on('dragend', e => {
            e.target.style.opacity = '1'
            let position = [
                this.position[0] + e.offsetX - this.metadata.offsetX,
                this.position[1] + e.offsetY - this.metadata.offsetY,
            ]
            this.metadata = null
            this.move(position)
        })
    }
    erase() {
        $(`#${this.id}`).remove()
        let connectors = this.inputConnectors.concat(this.outputConnectors)
        for (let connector of connectors) {
            if (connector) connector.erase()
        }
    }
    move(position) {
        this.position = position
        this.erase()
        this.draw()
        let connectors = this.inputConnectors.concat(this.outputConnectors)
        for (let connector of connectors) {
            if (connector) connector.draw()
        }
    }
    autoWidth(text) {
        const INTERNAL_PADDING = 10
        let textWidth = getTextWidth(text, "14pt Lato,'Helvetica Neue',Arial,Helvetica,sans-serif")
        let totalWidth = textWidth + 6 + INTERNAL_PADDING  // fix for border
        this.size[0] = totalWidth
        $(`#${this.id}`)[0].style.left = `${this.position[0] - totalWidth / 2}px`
        $(`#${this.id} input`).parent()[0].style.width = `${totalWidth}px`
    }
    createNode(name, parent, reverseNext, reverseFirst) {
        let node = new Node(name, parent)
        nodes.push(node)
        node.autoPosition(reverseNext, reverseFirst)
        node.draw()
        if (parent) {
            var connector = new Connector(node, parent)
            connector.draw()
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
        return this
    }
    leaveEditMode() {
        toast('Leaving edit mode')
        this.editMode = false
        $(`#${this.id}`).addClass('selected')
        $(`#${this.id} input`).css('caret-color', 'transparent')
        setCaretToPos($(`#${this.id} input`)[0], $(`#${this.id} input`).val().length)
        return this
    }
    focus() {
        $(`#${this.id} input`).focus()
    }
    blur() {
        $(`#${this.id} input`).blur()
    }
    printDetail() {
        console.log(`Node ${this.name} at (${this.position[0]}, ${this.position[1]})`)
        console.log(this)
    }
    select() {
        $(`#${this.id}`).addClass('selected')
        this.focus()
        this.printDetail()
    }
    unselect() {
        $(`#${this.id}`).removeClass('selected')
    }
    delete(cascade = true) {
        if (this.isRoot()) {
            toast('Cannot delete root node')
            return
        }
        this.erase()
        nodes = nodes.filter(node => node.id !== this.id)
        toast(`Node ${this.name} deleted`)
        this.connector.delete()
        delete this.connector
        this.parent.focus()
        if (cascade) this.deleteChildren(cascade)
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