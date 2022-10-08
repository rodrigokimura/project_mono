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

        let _x = this.node1.position[0] - this.node2.position[0]
        let _y = this.node1.position[1] - this.node2.position[1]
        let _sg, _p, _axis
        let _points = {x1: this.node1.position[0], x2: this.node2.position[0], y1: this.node1.position[1], y2: this.node2.position[1]}
        if (Math.abs(_x) >= Math.abs(_y)) {
            _sg = _x >= 0 ? 1 : -1
            _p = 0
            _axis = 'x'
        } else {
            _sg = _y >= 0 ? 1 : -1
            _p = 1
            _axis = 'y'
        }
        _points[`${_axis}1`] = _sg * -1 * (this.node1.size[_p] + this.node1.borderSize) / 2 + this.node1.position[_p]
        _points[`${_axis}2`] = _sg * +1 * (this.node2.size[_p] + this.node1.borderSize) / 2 + this.node2.position[_p]
        let cx = _sg * +1 * (Math.abs(_x) >= Math.abs(_y) ? (Math.abs(_x) / 4) : 0)
        let cy = _sg * +1 * (Math.abs(_y) >= Math.abs(_x) ? (Math.abs(_y) / 4) : 0)

        this.node1.connector = this
        this.el = $(`
            <svg class="connector" data-nodes="${this.node1.id}|${this.node2.id}" style="left: ${_points.x2 * scale}px; top: ${_points.y2 * scale}px; background-color: transparent;" width="10" height="10" overflow="visible" pointer-events="none" version="1.1" xmlns="http://www.w3.org/2000/svg">
                <circle cx="0" cy="0" r="${this.node1.borderSize * scale * 1.5}" fill="${this.node1.colors.border}"/>
                <path d="M 0 0 Q ${cx * scale} ${cy * scale} ${(_points.x1 - _points.x2) / 2 * scale} ${(_points.y1 - _points.y2) / 2 * scale} T ${(_points.x1 - _points.x2) * scale} ${(_points.y1 - _points.y2) * scale}" stroke-width="${this.node1.borderSize * scale}" fill="transparent"/>
                <circle cx="${(_points.x1 - _points.x2) * scale}" cy="${(_points.y1 - _points.y2) * scale}" r="${this.node1.borderSize * scale * 1.5}" fill="${this.node1.colors.border}"/>
            </svg>
        `)
        this.el.css('stroke', this.node1.colors.border)
        $(PANEL).append(this.el)
    }
}

var Connector = SvgLinearConnector