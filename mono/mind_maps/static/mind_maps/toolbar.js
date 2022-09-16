class Toolbar {
    constructor() {
        this._render()
    }
    _render() {
        this.el = $('#toolbar')
        this.rendered = true
    }
    hide() {
        let icon = $(`
            <a id="icon-toolbar" class="ui toolbar icon-toolbar segment" onclick="openToolbar()" style="display: none;">
                <i class="bars icon"></i>
            </a>
        `)
        this.el.parent().append(icon)
        this.el.find('.floating.label').hide()
        this.el.hide('swing')
        icon.show('swing')
    }
    show() {
        this.el.show('swing')
        this.el.find('.floating.label').show()
        $('.icon-toolbar').remove()
    }
}

var closeToolbar = () => { (new Toolbar()).hide() }
var openToolbar = () => { (new Toolbar()).show() }

var increaseFontSize = () => Node.getSelected()?.incrementFontSize(true)
var decreaseFontSize = () => Node.getSelected()?.incrementFontSize(false)
var increasePadding = () => Node.getSelected()?.incrementPadding(true)
var decreasePadding = () => Node.getSelected()?.incrementPadding(false)
var increaseBorder = () => Node.getSelected()?.incrementBorder(true)
var decreaseBorder = () => Node.getSelected()?.incrementBorder(false)

var increaseZoom = () => { scale++; changeScale(scale) }
var decreaseZoom = () => { scale--; changeScale(scale) }

var toggleBold = () => Node.getSelected()?.toggleTextStyle('bold')
var toggleItalic = () => Node.getSelected()?.toggleTextStyle('italic')
var toggleUnderline = () => Node.getSelected()?.toggleTextStyle('underline')
var toggleLineThrough = () => Node.getSelected()?.toggleTextStyle('lineThrough')

var autoStyle = () => { Node.getSelected()?.autoStyle().redraw() }

var red = () => { Node.getSelected()?.setColor('red').redraw() }
var orange = () => { Node.getSelected()?.setColor('orange').redraw() }
var yellow = () => { Node.getSelected()?.setColor('yellow').redraw() }
var olive = () => { Node.getSelected()?.setColor('olive').redraw() }
var green = () => { Node.getSelected()?.setColor('green').redraw() }
var teal = () => { Node.getSelected()?.setColor('teal').redraw() }
var blue = () => { Node.getSelected()?.setColor('blue').redraw() }
var violet = () => { Node.getSelected()?.setColor('violet').redraw() }
var purple = () => { Node.getSelected()?.setColor('purple').redraw() }
var pink = () => { Node.getSelected()?.setColor('pink').redraw() }
var brown = () => { Node.getSelected()?.setColor('brown').redraw() }
var grey = () => { Node.getSelected()?.setColor('grey').redraw() }
var black = () => { Node.getSelected()?.setColor('black').redraw() }

function changeBackgroundColor() {
    $(PANEL).css('background-color', this.toHEXAString())
}

jscolor.presets.default = {
    previewElement: null, valueElement: null, required: false
}