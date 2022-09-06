var toolbar

function init() {
    createPanel()
    loadMindMap()
    startSyncer()
    initToolbar()
}

function loadMindMap() {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/mm/api/mind_maps/${MIND_MAP_ID}/`,
        onSuccess: function (response) {
            nodes = []
            response.nodes.forEach(n => {
                let newNode = Node.getOrCreate(n.id)
                newNode.name = n.name
                newNode.position = n.position
                newNode.fontSize = n.font_size
                newNode.padding = n.padding
                if (n.parent) {
                    newNode.parent = Node.getOrCreate(n.parent)
                }
            })
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
    toolbar.hide()
}

function hideToolbar() {
    toolbar.hide()
}

function initializePanel() {

}
