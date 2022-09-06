class Button {
    constructor(text, icon, action) {
        this.text = text;
        this.icon = icon;
        this.action = action;
    }
    html() {
        return `<div class="ui icon button" onclick="${this.action.name}()" title="${this.text}">${this.icon}</div>`
    }
}

class Toolbar {
    constructor() {
        this._render()
        this.x = 1
        this.y = 5
    }
    get innerContent() {
        var html
        var buttons = [
            new Button("Increase font size", '<i class="font icon"></i>+', increaseFontSize),
            new Button("Decrease font size", '<i class="font icon"></i>-', decreaseFontSize),
        ]
        html = wrapRow(buttons.map(b => b.html()).join(''))
        buttons = [
            new Button("Increase padding", '<i class="font icon"></i>+', increasePadding),
            new Button("Decrease padding", '<i class="font icon"></i>-', decreasePadding),
        ]
        html += wrapRow(buttons.map(b => b.html()).join(''))
        return html
    }
    _render() {
        if ($('#toolbar').length > 0) {
            this.el = $('#toolbar')
            this.rendered = true
        } else {
            this.el = $(`<div class="ui segment toolbar" id="toolbar" style="padding: .5em;">${this.innerContent}</div>`)
            this.el.css('left', `${this.x}em`)
            this.el.css('top', `${this.y}em`)
            $(PANEL).append(this.el)
            this.rendered = true
        }
    }
    hide() { this.el.hide() }
    show() { this.el.show() }
}

function wrapRow(text) {
    return `<div class="toolbar-row" style="display: flex; flex-flow: row nowrap;">${text}</div>`
}

var increaseFontSize = () => Node.getSelected()?.increaseFontSize()
var decreaseFontSize = () => Node.getSelected()?.decreaseFontSize()
var increasePadding = () => Node.getSelected()?.increasePadding()
var decreasePadding = () => Node.getSelected()?.decreasePadding()