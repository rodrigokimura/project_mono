class Toolbar {
    constructor() {
        this._render()
        this.x = 1
        this.y = 5
    }
    _render() {
        this.el = $('#toolbar')
        $(PANEL).append(this.el)
        if (!this.rendered) {
            this.el[0].style.left = this.x
            this.el[0].style.top = this.y
        }
        this.rendered = true
    }
    hide() { this.el.hide() }
    show() { this.el.show() }
}

var increaseFontSize = () => Node.getSelected()?.increaseFontSize()
var decreaseFontSize = () => Node.getSelected()?.decreaseFontSize()
var increasePadding = () => Node.getSelected()?.increasePadding()
var decreasePadding = () => Node.getSelected()?.decreasePadding()
