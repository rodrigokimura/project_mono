class Positioner {
    constructor(node, reverseNext, reverseFirst) {
        this.node = node
        this.reverseNext = reverseNext  // offers alternative position for next guess
        this.reverseFirst = reverseFirst  // offers alternative position for first guess
        this.getReference = getReferenceForPositioningByAlwaysAbove
    }

    find() {
        const INITIAL_OFFSET = 120 / scale
        const BACKOFF = 10 / scale
        const ANGLE = this.reverseNext ? 45 : -45
        const MAX_CHILDREN = 200

        var node = this.node
        if (node.parent === null) {
            var x = panel.width / 2
            var y = panel.height / 2
            return [x, y]
        }
        var distance = INITIAL_OFFSET
        const nodesByLayer = 360 / ANGLE
        for (i = 0; i < MAX_CHILDREN; i++) {

            if (i % nodesByLayer === 0) {
                var referenceX, referenceY
                [referenceX, referenceY] = this.getReference(node, distance, this.reverseFirst)
                var x = (node.parent.position[0] - referenceX) * ((i / 8) + 1) + node.parent.position[0]
                var y = (node.parent.position[1] - referenceY) * ((i / 8) + 1) + node.parent.position[1]
                // Decrease offset for next layer iteration
                distance -= BACKOFF
                // Add rotation every two layer iterations
                if ((i / nodesByLayer) & 1) {
                    [x, y] = rotate(node.parent.position[0], node.parent.position[1], x, y, ANGLE / 2)
                }
            }

            if (isPositionAvailable(node, x, y)) {
                return [x, y]
            }
            let position = getNextPosition(node, x, y, ANGLE)
            x = position[0]
            y = position[1]
        }
    }
}

function getReferenceForPositioningByOpposite(node, distance, reverseFirst) {
    // reverseFirst is invalid for this strategy
    var parentHasParent = node.parent.parent !== null
    if (parentHasParent) {
        var referenceX = node.parent.parent.position[0]
        var referenceY = node.parent.parent.position[1]
    } else {
        var referenceX = node.parent.position[0]
        var referenceY = node.parent.position[1] - distance
    }
    return [referenceX, referenceY]
}

function getReferenceForPositioningByAlwaysAbove(node, distance, reverseFirst) {
    var referenceX = node.parent.position[0]
    var referenceY = node.parent.position[1] - distance * (reverseFirst ? -1 : 1)
    return [referenceX, referenceY]
}

function isPositionAvailable(node, x, y) {
    for (let other of nodes) {
        if (other === node) {
            continue
        }
        if (other.covers(x, y)) {
            return false
        }
    }
    return true
}

function rotate(cx, cy, x, y, angle) {
    var radians = (Math.PI / 180) * angle
    var cos = Math.cos(radians)
    var sin = Math.sin(radians)
    var nx = (cos * (x - cx)) - (sin * (y - cy)) + cx
    var ny = (cos * (y - cy)) + (sin * (x - cx)) + cy
    return [Math.round(nx), Math.round(ny)]
}

function getNextPosition(node, x, y, angle) {
    let cx = node.parent.position[0]
    let cy = node.parent.position[1]
    return rotate(cx, cy, x, y, angle)
}