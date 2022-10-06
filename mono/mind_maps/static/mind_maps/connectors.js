class BaseConnector {
    constructor(node1, node2) {
        this.node1 = node1
        this.node2 = node2
    }
    static get() {
        return $(`#${this.id} input`)[0], $(`#${this.id} input`)
    }
    redraw() {
        this.erase()
        this.draw()
    }
    erase() {
        this.el.remove()
    }
    delete() {
        this.erase()
    }
    show() { this.el.show() }
    hide() { this.el.hide() }
}
class DivLinearConnector extends BaseConnector {
    draw() {
        let x1 = this.node1.position[0]
        let y1 = this.node1.position[1]
        let x2 = this.node2.position[0]
        let y2 = this.node2.position[1]
        let angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI
        let length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))

        this.node1.connector = this
        this.el = $(`
            <div class="connector" data-nodes="${this.node1.id}|${this.node2.id}" style="width: ${length * scale}px; left: ${x1 * scale}px; top: ${y1 * scale}px; transform: rotate(${angle}deg);">
            </div>
        `)
        this.el.height(this.node1.borderSize * scale)
        this.el.css('background-color', this.node1.colors.border)
        $(PANEL).append(this.el)
    }
}

class SvgLinearConnector extends BaseConnector {
    draw() {
        let x1 = this.node1.position[0]
        let y1 = this.node1.position[1]
        let x2 = this.node2.position[0]
        let y2 = this.node2.position[1]
    
        let _x = x1 - x2
        let _y = y1 - y2
        let cx = 0
        let cy = 0

        if (_x >= 0) {
            if (_x >= Math.abs(_y)) {
                console.log('right')
                x2 = this.node2.position[0] + (this.node2.size[0] + this.node1.borderSize) / 2
                x1 = this.node1.position[0] - (this.node1.size[0] + this.node1.borderSize) / 2
                cx = Math.abs(x2 - x1) / 4
                cy = 0
            }
        } else {
            if (Math.abs(_x) >= Math.abs(_y)) {
                console.log('left')
                x2 = this.node2.position[0] - (this.node2.size[0] + this.node1.borderSize) / 2
                x1 = this.node1.position[0] + (this.node1.size[0] + this.node1.borderSize) / 2
                cx = - Math.abs(x2 - x1) / 4
                cy = 0
            }
        }
        if (_y >= 0) {
            if (_y >= Math.abs(_x)) {
                console.log('bottom')
                y2 = this.node2.position[1] + (this.node2.size[1] + this.node1.borderSize) / 2
                y1 = this.node1.position[1] - (this.node1.size[1] + this.node1.borderSize) / 2
                cx = 0
                cy = Math.abs(y2 - y1) / 4
            }
        } else {
            if (Math.abs(_y) >= Math.abs(_x)) {
                console.log('top')
                y2 = this.node2.position[1] - (this.node2.size[1] + this.node1.borderSize) / 2
                y1 = this.node1.position[1] + (this.node1.size[1] + this.node1.borderSize) / 2
                cx = 0
                cy = - Math.abs(y2 - y1) / 4
            }
        }

        this.node1.connector = this
        this.el = $(`
            <svg class="connector" data-nodes="${this.node1.id}|${this.node2.id}" style="left: ${x2 * scale}px; top: ${y2 * scale}px; background-color: transparent;" width="10" height="10" overflow="visible" pointer-events="none" version="1.1" xmlns="http://www.w3.org/2000/svg">
                <circle cx="0" cy="0" r="${this.node1.borderSize * scale * 1.5}" fill="${this.node1.colors.border}"/>
                <path d="M 0 0 Q ${cx * scale} ${cy * scale} ${(x1 - x2) / 2 * scale} ${(y1 - y2) / 2 * scale} T ${(x1 - x2) * scale} ${(y1 - y2) * scale}" stroke-width="${this.node1.borderSize * scale}" fill="transparent"/>
                <circle cx="${(x1 - x2) * scale}" cy="${(y1 - y2) * scale}" r="${this.node1.borderSize * scale * 1.5}" fill="${this.node1.colors.border}"/>
            </svg>
        `)
        this.el.css('stroke', this.node1.colors.border)
        $(PANEL).append(this.el)
    }
}

var Connector = SvgLinearConnector