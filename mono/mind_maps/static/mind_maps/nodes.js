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
        this.size = [0, 30]
        this.editMode = false
        this.connector = null
        this.metadata = {}
        this.fontSize = 14
        this.padding = 10
    }
    get width() { return this.size[0] }
    get height() { return this.size[1] }
    get children() { return nodes.filter(node => node.parent === this) }
    get inputConnectors() { return this.connector ? [this.connector] : [] }
    get outputConnectors() { return this.children.map(child => child.connector) }
    get connectors() { return this.inputConnectors.concat(this.outputConnectors) }
    get selected() { return this.el.hasClass('selected') }
    get state() {
        let state = {
            id: this.id,
            name: this.name,
            parent: this.parent ? this.parent.id : null,
            position: this.position,
            size: this.size,
            fontSize: this.fontSize,
            padding: this.padding,
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
    static getSelected() {
        let f = nodes.filter(node => node.el.hasClass('selected'))
        if (f.length > 0) return f[0]
        return null
    }
    static getRoot() { return nodes.filter(node => node.isRoot()) }
    static deselectAll() { return nodes.map(node => node.deselect()) }
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
            <div id="${this.id}" draggable="true" class="node" style="height: ${this.height}px; left: ${x}px; top: ${y}px; font-size: ${this.fontSize}pt">
                <input type="text" tabindex="-1" value="${this.name}" style="width: 100%; height: 100%;">
            </div>
        `)
        this.el = nodeEl
        $(PANEL).append(nodeEl)
        this.autoSize(this.name)
        this.attachEvents()
    }
    redraw() {
        let selected = this.selected
        this.erase()
        this.draw()
        this.drawConnectors(true)
        if (selected) this?.select()
    }
    unfade() { this.el[0].style.opacity = 1 }
    fade() { this.el[0].style.opacity = 0.5 }
    drawConnectors(drawOutputConns = false) {
        if (this.parent) {
            (new Connector(this, this.parent)).draw()
        }
        if (drawOutputConns) {
            this.children.forEach(child => {
                (new Connector(child, this)).draw()
            })
        }
    }
    attachEvents() {
        let inputEl = this.el.find('input')
        inputEl.keydown(e => {
            let editModeCommands = {
                9: () => { this.leaveEditMode() },
                13: () => { this.leaveEditMode() },
                27: () => { this.leaveEditMode() },
            }
            let normalCommands = {
                9: () => { this.createChild('', e.shiftKey).enterEditMode().focus() },
                13: () => {
                    if (this.isRoot()) {
                        this.createChild('', e.shiftKey).enterEditMode().focus()
                    } else {
                        this.createSibling('', e.shiftKey).enterEditMode().focus()
                    }
                },
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
        this.el.click(e => {
            e.preventDefault()
            e.stopPropagation()
            this.deselectOthers()
            this?.select()
        })
        inputEl.on('input', e => {
            if (e.target.value.length > 90) {
                toast('Node name too long')
                e.target.value = e.target.value.slice(0, 90)
                this.autoSize(e.target.value)
            }
            this.name = e.target.value
            this.autoSize(e.target.value)
        })
        inputEl.blur(e => {
            if (!this.name) this.delete()
        })
        this.el.on('dragstart', e => {
            this.metadata = {
                pageX: e.pageX,
                pageY: e.pageY,
            }
            $(PANEL).on('drop', e => {
                e.stopPropagation()
                e.preventDefault()
                let position = [
                    this.position[0] + e.pageX - this.metadata.pageX,
                    this.position[1] + e.pageY - this.metadata.pageY,
                ]
                this.metadata = null
                this.move(position)
                $(PANEL).off('drop')
            })
        })
        this.el.on('touchstart', e => {
            this.metadata = {
                pageX: e.targetTouches[0].screenX,
                pageY: e.targetTouches[0].screenY,
            }
        })
        this.el.on('touchmove', e => {
            e.preventDefault()
            this.el[0].style.left = this.position[0] + e.targetTouches[0].pageX - this.metadata.pageX - this.size[0] / 2 + 'px'
            this.el[0].style.top = this.position[1] + e.targetTouches[0].pageY - this.metadata.pageY - this.size[1] / 2 + 'px'
        })
        this.el.on('touchend', e => {
            let position = [
                parseFloat(this.el[0].style.left.replace('px', '')) + this.size[0] / 2,
                parseFloat(this.el[0].style.top.replace('px', '')) + this.size[1] / 2,
            ]
            this.metadata = null
            this.move(position)
        })
    }
    erase() {
        this.el.remove()
        let connectors = this.inputConnectors.concat(this.outputConnectors)
        for (let connector of connectors) {
            if (connector) connector.erase()
        }
    }
    move(position) {
        this.position = position
        this.redraw()
        for (let connector of this.connectors) {
            if (connector) connector.draw()
        }
    }
    autoSize(text) {
        let textSize = getTextSize(text, `${this.fontSize}pt 'Open Sans', sans-serif`)
        let borderWidth = this.el.css("border-left-width").replace('px', '')
        let totalWidth = textSize[0] + borderWidth * 2 + this.padding * 2
        let totalHeight = textSize[1] + borderWidth * 2 + this.padding * 2
        this.size[0] = totalWidth
        this.size[1] = totalHeight
        this.el[0].style.left = `${this.position[0] - totalWidth / 2}px`
        this.el[0].style.top = `${this.position[1] - totalHeight / 2}px`
        this.el.width(totalWidth)
        this.el.height(totalHeight)
        this.el.css('border-radius', totalHeight)
    }
    createNode(name, parent, reverseNext, reverseFirst) {
        this.deselect()
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
        this.editMode = true
        this.el.removeClass('selected')
        this.el.find('input').css('caret-color', 'black')
        setSelectionRange(this.el.find('input')[0], 0, this.el.find('input').val().length)
        return this
    }
    leaveEditMode() {
        this.editMode = false
        this.el.addClass('selected')
        this.el.find('input').css('caret-color', 'transparent')
        setCaretToPos(this.el.find('input')[0], 0)  // reset caret position
        if (!this.name) this.delete()
    }
    focus() { $(`#${this.id} input`).focus() }
    blur() { $(`#${this.id} input`).blur() }
    printDetail() {
        console.log(`Node ${this.name} at (${this.position[0]}, ${this.position[1]})`)
        console.log(this)
    }
    select() {
        $(`#${this.id}`).addClass('selected')
        this.focus()
        toolbar.show()
    }
    deselect() { $(`#${this.id}`).removeClass('selected') }
    deselectOthers() {
        nodes.map(node => { if (node != this) node?.deselect() })
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
        this.deselect()
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
        closestNode?.select()
    }
    increaseFontSize() { this.fontSize += 5; this.redraw() }
    decreaseFontSize() { this.fontSize -= 5; this.redraw() }
    increasePadding() { this.padding += 5; this.redraw() }
    decreasePadding() { this.padding -= 5; this.redraw() }
}