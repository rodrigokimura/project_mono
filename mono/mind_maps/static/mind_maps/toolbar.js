class Toolbar {
    constructor() {
        this._render()
    }
    _render() {
        this.el = $('#toolbar')
        this.rendered = true
    }
    hide() { this.el.hide() }
    show() { this.el.show() }
}

var increaseFontSize = () => Node.getSelected()?.increaseFontSize()
var decreaseFontSize = () => Node.getSelected()?.decreaseFontSize()
var increasePadding = () => Node.getSelected()?.increasePadding()
var decreasePadding = () => Node.getSelected()?.decreasePadding()
var increaseZoom = () => { scale += 1; changeScale(scale); centralize() }
var decreaseZoom = () => { scale -= 1; changeScale(scale); centralize() }
