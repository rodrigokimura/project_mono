function updateText() {
    $.api({
        on: 'now',
        url: `/nt/api/notes/${NOTE_ID}/`,
        method: 'PATCH',
        data: {
            text: $('textarea[name=text]').val(),
        },
        stateContext: '.green.button',
        successTest: r => true,
        onSuccess: r => {
            $('body').toast({
                title: gettext('Note saved!'),
                position: 'bottom right',
                class: 'black',
                displayTime: 750,
            })
        }
    })
}

function initializeTextarea() {
    $('textarea[name=text]').on('input', e => {
        clearTimeout(updateTextTimeout)
        updateTextTimeout = setTimeout(function () {
            updateText()
        }, 1000)
    })
}

function autoFormatTable() {
    function formatTable() {
        $('table').addClass('ui table')
        setTimeout(formatTable, 200)
    }
    setTimeout(formatTable, 200)
    $('textarea[name=text]').change(() => {
        $('table').addClass('ui table')
    })
}