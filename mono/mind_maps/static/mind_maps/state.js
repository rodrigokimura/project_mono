var syncer = null

function fullSync() {
    let ns = nodes.map(
        n => {
            return {
                'id': n.id,
                'mind_map': MIND_MAP_ID,
                'name': n.name,
                'parent': n.parent ? n.parent.id : null,
                'x': n.position[0],
                'y': n.position[1],
                'font_size': n.fontSize,
                'padding': n.padding,
                'border_size': n.borderSize,
                'bold': n.textStyle.bold,
                'italic': n.textStyle.italic,
                'underline': n.textStyle.underline,
                'line_through': n.textStyle.lineThrough,
                'font_color': n.colors.font,
                'border_color': n.colors.border,
                'background_color': n.colors.background,
                'collapsed': n.collapsed,
            }
        }
    )
    $.api({
        on: 'now',
        method: 'POST',
        url: `/mm/${MIND_MAP_ID}/sync/`,
        data: JSON.stringify(ns),
        contentType: 'application/json',
        stateContext: '#save-button',
        onSuccess(r) {
            storeState()
        }
    })
}

function storeState() {
    var nodesState = nodes.map(n => n.state)
    sessionStorage.setItem('nodes', JSON.stringify(nodesState))
}

function getState() {
    return JSON.parse(sessionStorage.getItem('nodes'))
}

function compareState() {
    return equalSets(
        new Set(getState()),
        new Set(nodes.filter(n => n.name).map(n => n.state))
    )
}

function equalSets(xs, ys) {
    return xs.size === ys.size && [...xs].every((x) => ys.has(x))
}

function syncIfNecessary() {
    if (!compareState()) {
        fullSync()
    }
}

function startSyncer() {
    syncer = setInterval(syncIfNecessary, 3000)
    window.onbeforeunload = () => {
        if (!compareState()) return "You have unsaved changes. Are you sure you want to leave?"
        return null
    }
}
