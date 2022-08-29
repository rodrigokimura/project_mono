async function collapseAll(tableId) {
    $(`#${tableId} tbody tr[data-folder]`).each((i, el) => {
        let file = $(el).data('folder')
        let caret = $(el).find('.caret.icon')

        caret.removeClass('down').addClass('right')
        $(`#${tableId} tbody`).find(`tr[data-parent='${file}']`).hide()
    })
}

async function toast(msg) {
    $('body').toast({
        title: msg,
        class: 'black',
        showProgress: 'bottom',
        position: 'right bottom',
    })
}