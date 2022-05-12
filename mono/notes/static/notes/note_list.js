function deleteNote(id) {
    $('body').modal({
        title: gettext('Confirmation'),
        class: 'mini',
        closeIcon: true,
        content: gettext('Are you sure you want to delete this note?'),
        actions: [
            {
                text: gettext('Cancel'),
                class: 'black deny'
            },
            {
                text: gettext('Yes, delete it.'),
                class: 'red approve'
            },
        ],
        onApprove: () => {
            let url = `/nt/api/notes/${id}`;
            $.api({
                on: 'now',
                url: url,
                method: 'DELETE',
                headers: { 'X-CSRFToken': csrftoken },
                stateContext: '.delete.button',
                onSuccess: r => {
                    $('body').toast({
                        title: gettext('Deletion'),
                        message: gettext('Note deleted successfully.'),
                        onHidden: () => {
                            location.reload();
                        }
                    })
                }
            });
        }
    }).modal('show');
}

function getNote(id) {
    noteSegment = $('.ui.note.segment')
    noteSegment.removeClass('hidden')
    $.api({
        on: 'now',
        method: 'GET',
        url: `/nt/api/notes/${id}/`,
        stateContext: noteSegment,
        successTest: r => r.id,
        onSuccess: r => {
            $("#note-html").html(r.html);
            $("#note-title").text(r.title);
            $('.ui.edit.button')
                .attr('href', r.url);
            $('.ui.delete.button')
                .off('click')
                .on('click', () => { deleteNote(id) });
            $('.file-item').removeClass('selected')
            $(`.file-item[data-id=${id}]`).addClass('selected')
        }
    })
}


function initializeFiles() {
    $('.file-item').click(function(e) {
        fileItemElement = $(e.target).closest('.file-item')
        getNote(fileItemElement.attr('data-id'))
    })
}
function initializeFolders() {
    $('.folder-item').click(function() {
        $(this).siblings('.list').toggle({ duration: 200, easing: 'swing' });
        $(this).children('.icon').toggleClass('open');
    })
}
function initializeSidebar() {
    $('.ui.sidebar')
        .sidebar({
            scrollLock: false,
            returnScroll: false,
            exclusive: false,
            transition: 'overlay',
            mobileTransition: 'overlay',
        })
        .sidebar('attach events', '.toc.item');
}

MutationObserver = window.MutationObserver || window.WebKitMutationObserver;
var observer = new MutationObserver(function(mutations, observer) {
    $('table').addClass('ui table');
});
observer.observe(document, {
    subtree: true,
    attributes: true
});