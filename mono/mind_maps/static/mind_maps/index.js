const CONTAINER = '#container'
const PANEL = '#container .panel'

var panel = {
    height: 1200,
    width: 1200,
}
var nodes = []


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
    node.draw()
    if (parent) {
        connector = new Connector(node, parent)
        connector.draw()
    }
    toast('Node', `Node ${node.name} created`)
}

function createRoot() {
    createNode('Root')
}
function createChild() {
    let n = nodes.length
    createNode(`Child ${n}`, nodes[0])
}
function swarm(n) {
    createRoot()
    for (let i = 0; i < n; i++) {
        createChild()
    }
}