function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time))
}

function init() {
    retrieveMindMaps()
}

function retrieveMindMaps() {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/mm/api/mind_maps/`,
        stateContext: '#grid',
        onSuccess(response) {
            $('#page-content').empty()
            $('#new-mind-map-btn-row').remove()
            if (response.count > 0) {
                renderMindMaps(response.results)
                $('#page-content').parent().parent().append(`
                    <div class="row" id="new-mind-map-btn-row">
                        <div class="column">
                            <div class="ui green button" onclick="showMindMapModal()">${gettext('New mind map')}</div>
                        </div>
                    </div>
                `)
            } else {
                renderPlaceholder()
            }
        },
    })
}

function renderPlaceholder() {
    const pageContent = $('#page-content')
    pageContent.append(`
        <div class="ui placeholder segment">
            <div class="ui icon header">
                <i class="exclamation triangle icon"></i>
                ${gettext("No mind maps yet.")}
            </div>
            <div class="ui icon labeled animated large green button" onclick="showMindMapModal()">
                <div class="visible content">${gettext("Add your first mind map!")}</div>
                <div class="hidden content"><i class="plus icon"></i></div>
            </div>
        </div>
    `)
}

function renderMindMaps(mindMaps) {
    const pageContent = $('#page-content')
    pageContent.empty()
    pageContent.append(`
        <div class="ui message">
            ${interpolate(ngettext('You have only %s mind map.', 'You have %s mind maps.', mindMaps.length), [mindMaps.length])}
        </div>
        <div class="ui four stackable cards" style="margin-top: .5em; padding-top: 0;" id="mind_maps"></div>
    `)
    pageContent.ready(e => {
        let mindMapsEl = $('#mind_maps')
        mindMapsEl.empty()
        mindMaps.forEach(renderMindMap)
        mindMapsEl.ready(e => {
            initializeCardMenuDropdown()
            initializeDeleteBoardButtons()
            $('.ui.progress').progress()
            $('.ui.progress').popup()
            $('.bar').popup()
            initializeDragAndDrop()
        })
    })
}

function renderMindMap(mindMap) {
    const boardsEl = $('#mind_maps')
    boardsEl.append(`
        <div class="ui card" data-mind-map-id="${mindMap.id}" ${mindMap.background_image ? `style="background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.3)), url('${mindMap.background_image}'); background-size: cover;"` : ""}>
            <div class="center aligned handle content" style="flex: 0 0 auto; display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move;">
                <i class="grip lines icon"></i>
            </div>
            <div class="content" style="padding-bottom: 0;">
                <div class="header" style="display: flex; flex-flow: row nowrap; justify-content: space-between;">
                    <div class="" style="flex: 0 1 auto; overflow-wrap: anywhere; padding-right: .5em;">
                        <a class="mind-map-link" href="/mm/${mindMap.id}/">${mindMap.name}</a>
                    </div>
                    <div class="ui basic icon top right pointing card-menu dropdown button" style="flex: 0 0 auto; align-self: flex-start;">
                        <i class="ellipsis horizontal icon"></i>
                        <div class="menu">
                            <a class="item" href="/mm/${mindMap.id}/"><i class="eye icon"></i>${gettext("Open")}</a>
                            <div class="item" onclick="showMindMapModal('${mindMap.id}')"><i class="edit icon"></i>${gettext("Edit")}</div>
                            <div class="divider"></div>
                            <a class="delete-board item" data-mind-map-id="${mindMap.id}"><i class="delete icon"></i>${gettext("Delete")}</a>
                        </div>
                    </div>
                </div>
                <div class="meta">
                    <p>${interpolate(gettext("Created at %s"), [stringToLocalDatetime(mindMap.created_at, languageCode)])}</p>
                </div>
            </div>
        </div>
    `)
    $('.profile-pic').popup()
}

function showMindMapModal(mindMapId = null) {
    const MODAL = $('#mind-map-modal')
    let method, url
    if (!mindMapId) {
        method = 'POST'
        url = '/mm/api/mind_maps/'
        MODAL.find('input[name="name"]').val('')
    } else {
        method = 'PATCH'
        url = `/mm/api/mind_maps/${mindMapId}/`
        let mindMapName = $(`.ui.card[data-mind-map-id='${mindMapId}'] .mind-map-link`).text()
        MODAL.find('input[name="name"]').val(mindMapName)
    }
    MODAL.modal({
        onApprove() {
            $.api({
                on: 'now',
                method: method,
                url: url,
                data: {
                    name: MODAL.find('input[name="name"]').val(),
                },
                stateContext: '#grid',
                onSuccess(response) {
                    retrieveMindMaps()
                },
            })
        },
    }).modal('show')
}

function initializeDeleteBoardButtons() {
    $('.delete-board').click(e => {
        let mindMapId = $(e.target).attr('data-mind-map-id');
        $('body').modal({
            title: gettext('Confirm deletion'),
            class: 'mini',
            closeIcon: true,
            content: gettext('Delete this mind map?'),
            actions: [
                { text: 'Cancel', class: 'secondary' },
                { text: 'Delete', class: 'red approve' },
            ],
            onApprove: () => {
                $.api({
                    on: 'now',
                    method: 'DELETE',
                    url: `/mm/api/mind_maps/${mindMapId}/`,
                    onSuccess(r) { retrieveMindMaps() },
                    onFailure: (response, element, xhr) => { console.log("Something went wrong.") },
                    onError: (errorMessage, element, xhr) => { console.log(`Request error: ${errorMessage}`) },
                });
            }
        }).modal('show');
    })
}

function initializeCardMenuDropdown() {
    $('.ui.card-menu.dropdown').dropdown({
        action: 'hide'
    })
}

function initializeDragAndDrop() {
    dragula(
        [...document.querySelectorAll('.boards-container'), document.querySelector('#spaceless-boards')],
        {
            direction: 'horizontal',
            moves: (el, source, handle, sibling) =>
                $(el).hasClass('card')
                && (
                    $(handle).hasClass('handle') // use button as handle
                    || $(handle).parent().hasClass('handle') // also accept i tag (icon) as handle
                ),
        }
    )
        .on('drop', (el, target, source, sibling) => {
            board = $(el).attr('data-board-id')
            order = $(target).children().toArray().findIndex(e => e == el) + 1
            space = $(target).attr('data-space-id')
            $.api({
                on: 'now',
                url: `/pm/api/board-move/`,
                method: 'POST',
                stateContext: '#boards',
                data: {
                    project: PROJECT_ID,
                    board: board,
                    order: order,
                    space: space == '' ? null : space,
                },
                onSuccess: r => {
                    $('body').toast({
                        title: 'Success',
                        message: 'Board order updated successfully',
                        class: 'success',
                    })
                },
                onFailure(response) {
                    $('body').toast({
                        title: 'Failure',
                        message: 'A problem occurred while updating board order',
                        class: 'error',
                    })
                    renderBoards()
                },
            });
        })
    disableDragOnTouchScreen()
}

function disableDragOnTouchScreen() {
    $('.handle').off().on(
        'touchmove', e => {
            e.preventDefault();
        }
    )
}
