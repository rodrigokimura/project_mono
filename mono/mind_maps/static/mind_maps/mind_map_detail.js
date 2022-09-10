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
            const MARGIN = 20
            let maxX = Math.max(...r.nodes.map(n => n.position[0]))
            let minX = Math.min(...r.nodes.map(n => n.position[0]))
            let width = maxX - minX
            let maxY = Math.max(...r.nodes.map(n => n.position[1]))
            let minY = Math.min(...r.nodes.map(n => n.position[1]))
            let height = maxY - minY
            let expandX = (width < window.innerWidth / scale) ? (window.innerWidth / scale - width) / 2 : 0
            let expandY = (height < window.innerHeight / scale) ? (window.innerHeight / scale - height) / 2 : 0
            let dX = MARGIN - minX + expandX
            let dY = MARGIN - minY + expandY
            r.nodes.forEach(n => {
                let newNode = Node.getOrCreate(n.id)
                newNode.name = n.name
                newNode.position = [n.position[0] + dX, n.position[1] + dY]
                newNode.fontSize = n.font_size
                newNode.padding = n.padding
                newNode.textStyle = {
                    bold: n.bold,
                    italic: n.italic,
                    underline: n.underline,
                    lineThrough: n.line_through,
                }
                if (n.parent) {
                    newNode.parent = Node.getOrCreate(n.parent)
                }
            })
            initializePanel(
                Math.max(window.innerWidth / scale, width) + 2 * MARGIN,
                Math.max(window.innerHeight / scale, height) + 2 * MARGIN,
            )
            renderNodes()
        }
    })
}

function renderNodes() {
    $(PANEL).find('.node,.connector').remove()
    nodes.forEach(n => {
        n.draw()
        n.drawConnectors()
    })
    centralize()
    storeState()
}

function initToolbar() {
    toolbar = new Toolbar()
}

function hideToolbar() {
    toolbar.hide()
}
