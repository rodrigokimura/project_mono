function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}


function exportMindMap() {
    let ns = nodes.map(
        n => {
            return {
                'id': n.id,
                'mind_map': MIND_MAP_ID,
                'name': n.name,
                'parent': n.parent ? n.parent.id : null,
                'x': n.position[0],
                'y': n.position[1],
                'font_size': n.fontSize,
                'padding': n.padding,
                'border_size': n.borderSize,
                'bold': n.textStyle.bold,
                'italic': n.textStyle.italic,
                'underline': n.textStyle.underline,
                'line_through': n.textStyle.lineThrough,
                'font_color': n.colors.font,
                'border_color': n.colors.border,
                'background_color': n.colors.background,
                'collapsed': n.collapsed,
            }
        }
    )
    let mindMap = {
        "id": MIND_MAP_ID,
        "name": MIND_MAP_NAME,
        "backgroundColor": panel.color,
        "scale": scale,
        "nodes": ns,
    }
    download(MIND_MAP_NAME + '.json', JSON.stringify(mindMap, null, 4))
}

