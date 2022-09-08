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
var increaseZoom = () => { scale++; changeScale(scale); centralize() }
var decreaseZoom = () => { scale--; changeScale(scale); centralize() }
var toggleBold = () => Node.getSelected()?.toggleTextStyle('bold')
var toggleItalic = () => Node.getSelected()?.toggleTextStyle('italic')
var toggleUnderline = () => Node.getSelected()?.toggleTextStyle('underline')
var toggleLineThrough = () => Node.getSelected()?.toggleTextStyle('lineThrough')
