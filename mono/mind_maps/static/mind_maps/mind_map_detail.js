var toolbar

function init() {
    loadMindMap()
    startSyncer()
    initToolbar()
}

function loadMindMap() {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/mm/api/mind_maps/${MIND_MAP_ID}/`,
        onSuccess(r) {
            nodes = []
            if (!r.nodes.length) {
                let node = new Node(MIND_MAP_NAME)
                node.autoStyle()
                nodes.push(node)
                reposition(nodes)
                centralize()
            }
            r.nodes.forEach(n => {
                let newNode = Node.getOrCreate(n.id)
                newNode.name = n.name
                newNode.position = n.position
                newNode.fontSize = n.font_size
                newNode.padding = n.padding
                newNode.borderSize = n.border_size
                newNode.textStyle = {
                    bold: n.bold,
                    italic: n.italic,
                    underline: n.underline,
                    lineThrough: n.line_through,
                }
                newNode.colors = {
                    background: n.background_color,
                    border: n.border_color,
                    font: n.font_color,
                }
                if (n.parent) {
                    newNode.parent = Node.getOrCreate(n.parent)
                }
            })
            reposition(nodes)
            centralize()
        }
    })
}

function reposition(nodes) {
    const MARGIN = 20
    let maxX = Math.max(...nodes.map(n => n.position[0]))
    let minX = Math.min(...nodes.map(n => n.position[0]))
    let width = maxX - minX
    let maxY = Math.max(...nodes.map(n => n.position[1]))
    let minY = Math.min(...nodes.map(n => n.position[1]))
    let height = maxY - minY
    let expandX = (width < window.innerWidth / scale) ? (window.innerWidth / scale - width) / 2 : 0
    let expandY = (height < window.innerHeight / scale) ? (window.innerHeight / scale - height) / 2 : 0
    let dX = MARGIN - minX + expandX
    let dY = MARGIN - minY + expandY
    nodes.forEach(n => {
        n.position = [n.position[0] + dX, n.position[1] + dY]
    })
    initializePanel(
        Math.max(window.innerWidth / scale, width) + 2 * MARGIN,
        Math.max(window.innerHeight / scale, height) + 2 * MARGIN,
    )
    renderNodes()
}

function renderNodes() {
    $(PANEL).find('.node,.connector').remove()
    nodes.forEach(n => {
        n.draw()
        n.drawConnectors()
    })
    storeState()
}

function initToolbar() {
    toolbar = new Toolbar()
}

function hideToolbar() {
    toolbar.hide()
}
