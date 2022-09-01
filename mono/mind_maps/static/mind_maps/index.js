async function toast() {
    $('body').toast({
        title: 'Test',
        message: 'Test',
        class: 'success',
        className: { toast: 'ui message' },
        showProgress: 'bottom',
        closeIcon: true,
    })
}

function createNode() {
    toast()
    let el = $('#panel')
    el.append(`
        <div class="node" draggable=true>
            Node
        </div>
    `)
}