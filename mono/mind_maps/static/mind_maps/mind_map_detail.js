function init() {
    createPanel()
    loadMindMap()
    startSyncer()
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
                if (n.parent) {
                    newNode.parent = Node.getOrCreate(n.parent)
                }
            })
            renderNodes()
        }
    })
}

function renderNodes() {
    $(PANEL).empty()
    nodes.forEach(n => {
        n.draw()
        // n.autoWidth(n.name)
        n.drawConnectors()
    })
    centralize()
    storeState()
}