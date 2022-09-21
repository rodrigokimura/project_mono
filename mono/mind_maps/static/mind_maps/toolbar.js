class Toolbar {
    constructor() {
        this._render()
    }
    _render() {
        this.el = $('#toolbar')
        this.rendered = true
        initializeColorPicker(
            'change-background-color',
            function () {
                showBackgroundColor(this.toHEXString())
            },
            function () {
                changeBackgroundColor(this.toHEXString())
            }
        )
        initializeNodeColorPicker('border')
        initializeNodeColorPicker('background')
        initializeNodeColorPicker('font')
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

var red = () => { Node.getSelected()?.setColor('red') }
var orange = () => { Node.getSelected()?.setColor('orange') }
var yellow = () => { Node.getSelected()?.setColor('yellow') }
var olive = () => { Node.getSelected()?.setColor('olive') }
var green = () => { Node.getSelected()?.setColor('green') }
var teal = () => { Node.getSelected()?.setColor('teal') }
var blue = () => { Node.getSelected()?.setColor('blue') }
var violet = () => { Node.getSelected()?.setColor('violet') }
var purple = () => { Node.getSelected()?.setColor('purple') }
var pink = () => { Node.getSelected()?.setColor('pink') }
var brown = () => { Node.getSelected()?.setColor('brown') }
var grey = () => { Node.getSelected()?.setColor('grey') }
var black = () => { Node.getSelected()?.setColor('black') }

function showBackgroundColor(color) {
    $(PANEL).css('background-color', color)
}

function initializeColorPicker(id, onInput, onChange) {
    $(`#${id}`).off().click(e => {
        delete $(`#${id}`)[0].jscolor
        let inputTimeout
        let picker = new JSColor(
            $(`#${id}`)[0],
            {
                onInput: function () {
                    let t = this
                    clearTimeout(inputTimeout)
                    inputTimeout = setTimeout(function () {
                        onInput.call(t)
                    }, 100)
                },
                onChange: onChange,
                previewElement: null,
                valueElement: null,
                required: false,
                palette: [
                    "#f44336",
                    "#ff9800",
                    "#ffeb3b",
                    "#cddc39",
                    "#4caf50",
                    "#009688",
                    "#2196f3",
                    "#673ab7",
                    "#9c27b0",
                    "#e91e63",
                    "#795548",
                    "#9e9e9e",
                    "#263238",

                    "#b71c1c",
                    "#e65100",
                    "#f57f17",
                    "#827717",
                    "#1b5e20",
                    "#004d40",
                    "#2185d0",
                    "#311b92",
                    "#a333c8",
                    "#880e4f",
                    "#3e2723",
                    "#212121",
                    "#000a12",

                    "#ffebee",
                    "#fff3e0",
                    "#fffde7",
                    "#f9fbe7",
                    "#e8f5e9",
                    "#e0f2f1",
                    "#e3f2fd",
                    "#ede7f6",
                    "#f3e5f5",
                    "#fce4ec",
                    "#efebe9",
                    "#fafafa",
                    "#eceff1",
                ],
                paletteCols: 13,
            },
        )
        picker.show()
    })
    $(`#${id} i.icon`).off().click(e => {
        $(e.target).parent().click()
    })
}

function initializeNodeColorPicker(type) {
    initializeColorPicker(
        `change-node-${type}-color`,
        function () {
            let node = Node.getSelected()
            if (node) {
                Node.getSelected()?.setCustomColor(type, this.toHEXString())
            } else {
                nodes.forEach(
                    node => node.setCustomColor(type, this.toHEXString())
                )
            }
        },
        function () {
            let node = Node.getSelected()
            if (node) {
                Node.getSelected()?.setCustomColor(type, this.toHEXString())
            } else {
                nodes.forEach(
                    node => node.setCustomColor(type, this.toHEXString())
                )
            }
        }
    )
}