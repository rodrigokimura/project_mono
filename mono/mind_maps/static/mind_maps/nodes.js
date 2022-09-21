var nodes = []

class Node {
    constructor(name, parent = null) {
        this.id = self.crypto.randomUUID()
        this.name = name
        this.parent = parent
        this.position = [0, 0]
        this.size = [0, 3 * scale]
        this.editMode = false
        this.connector = null
        this.metadata = {}
        this.fontSize = 1
        this.padding = 1
        this.borderSize = .3
        this.textStyle = {
            bold: false,
            italic: false,
            underline: false,
            lineThrough: false,
        }
        this.colors = {
            background: '#ffffff',
            border: '#000000',
            font: '#000000',
        }
        this.buttonSize = 2.5
        this.collapsed = false
    }
    get visible() { return this.el.is(":visible") }
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
            borderSize: this.borderSize,
            textStyle: this.textStyle,
            colors: this.colors,
            collapsed: this.collapsed,
        }
        let st = JSON.stringify(state)
        let hash = 0, i, chr;
        if (st.length === 0) return hash
        for (i = 0; i < st.length; i++) {
            chr = st.charCodeAt(i)
            hash = ((hash << 5) - hash) + chr
            hash |= 0
        }
        return hash
    }
    get level() {
        let level = 0
        let node = this
        while (node.parent) {
            node = node.parent
            level++
        }
        return level
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
    static deselectAll() {
        nodes.map(
            node => {
                if (node.editMode) node.leaveEditMode()
                node.deselect()
            }
        )
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
    isOutOfBoundaries() {
        return [
            this.position[0] < 0,
            this.position[0] * scale > $(PANEL).width(),
            this.position[1] < 0,
            this.position[1] * scale > $(PANEL).height(),
        ].some(v => v === true)
    }
    autoPosition(reverseNext, reverseFirst) {
        this.position = (new Positioner(this, reverseNext, reverseFirst)).find()
    }
    draw() {
        let x = this.position[0] - this.width / 2
        let y = this.position[1] - this.height / 2
        let nodeEl = $(`
            <div id="${this.id}" draggable="true" class="node" style="height: ${this.height * scale}px; left: ${x * scale}px; top: ${y * scale}px">
                <input type="text" tabindex="-1" value="${this.name}" style="width: 100%; height: 100%;">
            </div>
        `)
        this.el = nodeEl
        this.el.css('border-width', this.borderSize * scale)
        this.el.css('font-size', `${this.fontSize * scale}pt`)
        this.el.find('input').css('color', this.colors.font)
        this.el.css('border-color', this.colors.border)
        this.el.css('background-color', this.colors.background)
        this.applyTextStyle()
        this.el.find('input').css('caret-color', 'transparent')
        $(PANEL).append(nodeEl)
        if (this.children.length > 0) this._appendCollapseButton(this.collapsed)
        this._appendDeleteButton()
        this._appendAddChildButton()
        this.autoSize(this.name)
        this.attachEvents()
    }
    _appendButton(className, icon, attrName, onClick) {
        this.el.find(className).remove()
        let btn = $(`<div class="${className} button"><i class="${icon} icon"></i></div>`)
        this[attrName] = btn
        this.el.append(this[attrName])
        btn.css('position', 'absolute')
        btn.css('font-size', .6 * this.buttonSize * scale)
        btn.css('color', this.colors.border)
        btn.css('height', this.buttonSize * scale)
        btn.css('width', this.buttonSize * scale)
        btn.css('outline-color', this.colors.border)
        btn.css('outline-width', .3 * scale)
        btn.css('outline-style', 'solid')
        btn.css('border-radius', this.buttonSize * scale)
        btn.css('background-color', this.colors.background)
        btn.click(e => {
            e.stopPropagation()
            e.preventDefault()
            if ($(e.target).closest(`.${className}`).length == 0) return
            onClick.bind(this)()
        })
    }
    _updateButtonPosition(attrName, left, top) {
        this[attrName]?.css('left', (left - this.buttonSize / 2) * scale)
        this[attrName]?.css('top', (top - this.buttonSize / 2) * scale)
    }
    _appendCollapseButton(collapsed = false) {
        if (!collapsed) {
            this._appendButton('collapse-button', 'compress', 'collapseButton', this.collapse)
        } else {
            this._appendButton('collapse-button', 'expand', 'collapseButton', this.expand)
        }
    }
    _appendDeleteButton() {
        this._appendButton('delete-button', 'delete', 'deleteButton', this.delete)
    }
    _appendAddChildButton() {
        this._appendButton(
            'add-child-button', 'plus', 'addChildButton',
            () => { this.createChild('').enterEditMode().focus() }
        )
    }
    _updateCollapseButtonPosition() {
        this._updateButtonPosition('collapseButton', this.width - this.padding, - this.borderSize / 2)
    }
    _updateDeleteButtonPosition() {
        this._updateButtonPosition('deleteButton', this.padding, - this.borderSize / 2)
    }
    _updateAddChildButtonPosition() {
        this._updateButtonPosition('addChildButton', this.width / 2, this.height + this.borderSize / 2)
    }
    redraw() {
        let selected = this.selected
        this.erase()
        this.draw()
        this.drawConnectors(true)
        if (selected) this?.select()
    }
    collapse() {
        if (this.children.length === 0) return
        this.collapsed = true
        this.children.forEach(child => {
            child.el.hide()
            child.connector?.hide()
            child.collapse()
        })
        this.collapseButton.find('i').removeClass('compress').addClass('expand')
        this.collapseButton.off().click(e => {
            e.stopPropagation()
            e.preventDefault()
            if ($(e.target).closest(`.collapse-button`).length == 0) return
            this.expand.bind(this)()
        })
    }
    expand() {
        if (this.children.length === 0) return
        this.collapsed = false
        this.children.forEach(child => {
            child.el.show()
            child.connector?.show()
            child.expand()
        })
        this.collapseButton.find('i').removeClass('expand').addClass('compress')
        this.collapseButton.off().click(e => {
            e.stopPropagation()
            e.preventDefault()
            if ($(e.target).closest(`.collapse-button`).length == 0) return
            this.collapse.bind(this)()
        })
    }
    applyTextStyle() {
        let input = this.el.find('input')
        input.css('font-weight', this.textStyle.bold ? 'bold' : 'normal')
        input.css('font-style', this.textStyle.italic ? 'italic' : 'normal')
        let textDecoration = ''
        if (this.textStyle.underline) textDecoration += 'underline '
        if (this.textStyle.lineThrough) textDecoration += 'line-through '
        input.css('text-decoration', textDecoration)
    }
    unfade() { this.el[0].style.opacity = 1 }
    fade() { this.el[0].style.opacity = 0.5 }
    drawConnectors(drawOutputConns = false) {
        if (this.parent) {
            (new Connector(this, this.parent)).draw()
        }
        if (drawOutputConns) {
            this.children.forEach(child => {
                let conn = new Connector(child, this)
                conn.draw()
                if (!child.visible) conn.hide()
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
                    this.position[0] * scale + e.pageX - this.metadata.pageX,
                    this.position[1] * scale + e.pageY - this.metadata.pageY,
                ]
                this.metadata = null
                this.move(position)
                $(PANEL).off('drop')
            })
        })
        this.el.on('touchstart', e => {
            this.connectors.forEach(c => c.erase())
            this.metadata = {
                pageX: e.targetTouches[0].pageX,
                pageY: e.targetTouches[0].pageY,
            }
        })
        this.el.on('touchmove', e => {
            e.preventDefault()
            this.el[0].style.left = this.position[0] * scale + e.targetTouches[0].pageX - this.metadata.pageX - (this.size[0] / 2 + this.borderSize) * scale + 'px'
            this.el[0].style.top = this.position[1] * scale + e.targetTouches[0].pageY - this.metadata.pageY - (this.size[1] / 2 + this.borderSize) * scale + 'px'
        })
        this.el.on('touchend', e => {
            let position = [
                parseFloat(this.el[0].style.left.replace('px', '')) + (this.size[0] / 2 + this.borderSize) * scale,
                parseFloat(this.el[0].style.top.replace('px', '')) + (this.size[1] / 2 + this.borderSize) * scale,
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
    move(positionInPixels) {
        let deltaX = positionInPixels[0] - this.position[0] * scale
        let deltaY = positionInPixels[1] - this.position[1] * scale
        let nodes = [this]
        nodes.push(...this.children)
        nodes.forEach(node => {
            node.position[0] += deltaX / scale
            node.position[1] += deltaY / scale
            if (this.isOutOfBoundaries()) {
                reposition(nodes)
            } else {
                node.redraw()
            }
        })
    }
    autoSize(text) {
        let textSize = getTextSize(text, `${this.fontSize * scale}pt 'Open Sans', sans-serif`)
        let borderWidth = this.el.css("border-left-width").replace('px', '') / scale
        let totalWidth = textSize[0] + borderWidth * 2 + this.padding * 2
        let totalHeight = textSize[1] + borderWidth * 2 + this.padding * 2
        this.size[0] = totalWidth
        this.size[1] = totalHeight
        this.el[0].style.left = `${(this.position[0] - totalWidth / 2 - this.borderSize) * scale}px`
        this.el[0].style.top = `${(this.position[1] - totalHeight / 2 - this.borderSize) * scale}px`
        this.el.width(totalWidth * scale)
        this.el.height(totalHeight * scale)
        this.el.css('border-radius', totalHeight * scale)
        this._updateCollapseButtonPosition()
        this._updateDeleteButtonPosition()
        this._updateAddChildButtonPosition()
    }
    createNode(name, parent, reverseNext, reverseFirst) {
        this.deselect()
        let node = new Node(name, parent)
        nodes.push(node)
        node.autoPosition(reverseNext, reverseFirst)
        node.colors = this.colors
        node.autoStyle()
        node.draw()
        if (parent) {
            let connector = new Connector(node, parent)
            connector.draw()
        }
        toast(`Node ${node.name} created`)
        return node
    }
    createChild(name, alt = false) {
        if (!this.collapseButton) this._appendCollapseButton()
        this._updateCollapseButtonPosition()
        return this.createNode(name, this, false, alt)
    }
    createSibling(name, alt = false) {
        return this.createNode(name, this.parent, alt, false)
    }
    enterEditMode() {
        let backdrop = $(`
            <div class="backdrop" style="background-color: rgba(0, 0, 0, 0.2); z-index: 1000; width: 100%; height: 100%; position: relative;"></div>
        `)
        this.el.parent().append(backdrop)
        backdrop.click(e => { this.leaveEditMode() })
        $('.node').css('z-index', 20)
        this.el.css('z-index', 200)
        backdrop.css('z-index', 100)
        this.editMode = true
        this.el.removeClass('selected')
        this.el.find('input').css('caret-color', '')
        setSelectionRange(this.el.find('input')[0], 0, this.el.find('input').val().length)
        return this
    }
    leaveEditMode() {
        $('.backdrop').remove()
        this.el.css('z-index', 20)
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
        this.el.addClass('selected')
        this.focus()
        toolbar.show()
        // this.printDetail()
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
        this.connector?.delete()
        delete this.connector

        // remove parent's collapse button if it has no children
        if (this.parent.children.length == 0) {
            this.parent.collapseButton?.remove()
            delete this.parent.collapseButton
        }
        this.parent.select()
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
        let attrMap = {
            l: [0, 'width', (a, b) => a - b, (a, b) => a < b],
            r: [0, 'width', (a, b) => a + b, (a, b) => a > b],
            u: [1, 'height', (a, b) => a - b, (a, b) => a < b],
            d: [1, 'height', (a, b) => a + b, (a, b) => a > b],
        }
        let positionIndex, attr, edgeFunc, comparisonFunc
        [positionIndex, attr, edgeFunc, comparisonFunc] = attrMap[direction]

        // filter nodes after the edge of this node
        let edge = edgeFunc(this.position[positionIndex], this[attr] / 2)
        let filteredNodes = nodes.filter(n => n.visible === true).filter(
            node => comparisonFunc(node.position[positionIndex], edge)
        )
        if (filteredNodes.length === 0) this.select()
        if (filteredNodes.length === 1) {
            filteredNodes[0].select()
            return
        }
        // find the closest node
        let closestNode = filteredNodes.sort(
            (a, b) => this.distanceFrom(a) - this.distanceFrom(b)
        )[0]
        closestNode?.select()
    }
    _incrementAttr(attr, inc, positive) {
        if (!this.hasOwnProperty(attr)) return
        if (positive) {
            this[attr] += inc
        } else {
            if (this[attr] <= inc) return
            this[attr] -= inc
        }
        this.redraw()
    }
    incrementFontSize(positive = true) { this._incrementAttr('fontSize', .5, positive) }
    incrementPadding(positive = true) { this._incrementAttr('padding', 1, positive) }
    incrementBorder(positive = true) { this._incrementAttr('borderSize', .1, positive) }
    toggleTextStyle(attr) {
        if (!this.textStyle.hasOwnProperty(attr)) return
        this.textStyle[attr] = !this.textStyle[attr]
        this.redraw()
    }
    autoStyle() {
        if (!self.style) {
            if (this.level in STYLES) {
                this._applyStyle(STYLES[this.level])
            }
        }
        return this
    }
    _applyStyle(style) {
        this.fontSize = style.fontSize
        this.padding = style.padding
        this.borderSize = style.borderSize
        this.textStyle = style.textStyle
    }
    setColor(color) {
        if (color in PRESET_COLORS) {
            this.colors = PRESET_COLORS[color]
            this.redraw()
        }
        return this
    }
    setCustomColor(type, color) {
        if (!['background', 'border', 'font'].includes(type)) return
        this.colors[type] = color
        this.redraw()
        return this
    }
}