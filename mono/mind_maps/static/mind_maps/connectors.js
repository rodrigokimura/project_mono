class BaseConnector {
    constructor(node1, node2) {
        this.node1 = node1
        this.node2 = node2
    }
    get relX() { return this.node1.x - this.node2.x }
    get relY() { return this.node1.y - this.node2.y }
    get color() { return this.node1.colors.border }
    get borderSize() { return this.node1.borderSize }
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
        let angle = Math.atan2(this.relY, this.relX) * 180 / Math.PI
        let length = Math.sqrt(Math.pow(this.relX, 2) + Math.pow(this.relY, 2))
        this.node1.connector = this
        this.el = $(`
            <div class="connector" data-nodes="${this.node1.id}|${this.node2.id}" style="width: ${length * scale}px; left: ${this.node2.x * scale}px; top: ${this.node2.y * scale}px; transform: rotate(${angle}deg);">
            </div>
        `)
        this.el.height(this.borderSize * scale)
        this.el.css('background-color', this.color)
        $(PANEL).append(this.el)
    }
}

class SvgCurvedConnector extends BaseConnector {
    draw() {
        let points = {
            x1: this.node1.x,
            y1: this.node1.y,
            x2: this.node2.x,
            y2: this.node2.y,
        }
        let cond = Math.abs(this.relX) >= Math.abs(this.relY)
        let posIdx = cond ? 0 : 1
        let sign = (cond ? this.relX : this.relY) >= 0 ? 1 : -1
        let cx = sign * (cond ? (Math.abs(this.relX) / 4) : 0)
        let cy = sign * (cond ? 0 : (Math.abs(this.relY) / 4))
        points[`${cond ? 'x' : 'y'}1`] = sign * -1 * (this.node1.size[posIdx] + this.borderSize) / 2 + this.node1.position[posIdx]
        points[`${cond ? 'x' : 'y'}2`] = sign * +1 * (this.node2.size[posIdx] + this.borderSize) / 2 + this.node2.position[posIdx]
        this.node1.connector = this
        this.el = $(`
            <svg class="connector" data-nodes="${this.node1.id}|${this.node2.id}" style="left: ${points.x2 * scale}px; top: ${points.y2 * scale}px; background-color: transparent;" width="10" height="10" overflow="visible" pointer-events="none" version="1.1" xmlns="http://www.w3.org/2000/svg">
                <circle cx="0" cy="0" r="${this.borderSize * scale * 1.5}" fill="${this.color}"/>
                <path d="M 0 0 Q ${cx * scale} ${cy * scale} ${(points.x1 - points.x2) / 2 * scale} ${(points.y1 - points.y2) / 2 * scale} T ${(points.x1 - points.x2) * scale} ${(points.y1 - points.y2) * scale}" stroke-width="${this.borderSize * scale}" fill="transparent"/>
                <circle cx="${(points.x1 - points.x2) * scale}" cy="${(points.y1 - points.y2) * scale}" r="${this.borderSize * scale * 1.5}" fill="${this.color}"/>
            </svg>
        `)
        this.el.css('stroke', this.color)
        $(PANEL).append(this.el)
    }
}

var Connector = SvgCurvedConnector