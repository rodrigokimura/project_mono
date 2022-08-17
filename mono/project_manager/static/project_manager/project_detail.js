function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function showSharingModal() {
    $('#sharing-modal').modal({
        onShow: () => {
            $('.ui.button').popup();
        },
    }).modal('show');
}

function renderPage() {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/spaces/`,
        stateContext: '#grid',
        onSuccess(response) {
            retrieveBoards(response)
        },
    })
}

function retrieveBoards(spaces) {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/boards/`,
        stateContext: '#grid',
        onSuccess(response) {
            renderSpaces(spaces, response)
        },
    })
}

function renderPlaceholder() {
    const pageContent = $('#page-content')
    pageContent.append(`
        <div class="ui placeholder segment">
            <div class="ui icon header">
                <i class="exclamation triangle icon"></i>
                ${gettext("No boards are listed for this project yet.")}
            </div>
            <a href="/pm/project/${PROJECT_ID}/board/" class="ui icon labeled animated large green button">
                <div class="visible content">${gettext("Add your first board!")}</div>
                <div class="hidden content"><i class="plus icon"></i></div>
            </a>
        </div>
    `)
}

function renderBoards(boards) {
    const pageContent = $('#page-content')
    pageContent.empty()
    pageContent.append(`
        <div class="ui message">
            ${interpolate(ngettext('You have only %s board in project <strong>%s</strong>.', 'You have %s boards in project <strong>%s</strong>.', boards.length), [boards.length, PROJECT_NAME ])}
        </div>
        <div class="ui four stackable cards" style="margin-top: .5em; padding-top: 0;" id="boards"></div>
    `)
    pageContent.ready(e => {
        boardsEl = $('#boards')
        boardsEl.empty()
        boards.forEach(renderBoard)
        boardsEl.ready(e => {
            initializeCardMenuDropdown()
            initializeDeleteBoardButtons()
            $('.ui.progress').progress()
            $('.ui.progress').popup()
            $('.bar').popup()
            $('.ui.avatar.image').popup()
            initializeDragAndDrop()
        })
    })
}


function renderSpaces(spaces, boards) {
    const pageContent = $('#page-content')
    pageContent.empty()
    pageContent.append(`
        <div class="" style="margin-top: .5em; padding-top: 0;" id="spaces">
        </div>
        <div class="ui four stackable cards segment stripes" style="margin: 1em 0 0 0;" id="spaceless-boards" data-space-id="">
        </div>
    `)
    pageContent.ready(e => {
        if (boards.length == 0) {
            renderPlaceholder()
            return
        }
        spacesEl = $('#spaces')
        spacesEl.empty()
        spaces.forEach(
            space => {
                filteredBoards = boards.filter(
                    i => { return space.id == i.space }
                )
                renderSpace(space, filteredBoards)
            }
        )
        spacelessBoards = boards.filter(i => i.space == null)
        spacelessBoards.forEach(b => {
            renderBoard(b, $('#spaceless-boards'))
        })
        spacesEl.ready(e => {
            initializeCardMenuDropdown()
            initializeDeleteBoardButtons()
            $('.ui.progress').progress()
            $('.ui.progress').popup()
            $('.bar').popup()
            $('.ui.avatar.image').popup()
            initializeDragAndDrop()
        })
    })
}

function renderSpace(space, boards) {
    spacesEl = $('#spaces')
    spacesEl.append(`
        <div class="ui fluid space segments" data-space-id="${space.id}">
            <div class="ui segment" style="display: flex; flex-flow: row nowrap; align-items: center;">
                <div style="flex: 1 0 auto; padding-left: .5em;">
                    <span class="space-name">${space.name.toUpperCase()}</span>
                </div>
                <div style="flex: 0 1 auto;" class="ui icon button" onclick="editSpace(${space.id})">
                    <i class="edit icon"></i>
                </div>
                <div style="flex: 0 1 auto;" class="ui red icon button"  onclick="deleteSpace(${space.id})">
                    <i class="delete icon"></i>
                </div>
            </div>
            <div class="ui segment">
                <div class="boards-container ui four stackable cards" style="min-height: 100px;" data-space-id="${space.id}">
                </div>
            </div>
        </div>
    `)
    spacesEl.ready(() => {
        boards.forEach(b => {
            el = $(`.boards-container[data-space-id=${space.id}]`)
            renderBoard(b, el)
        })
    })
}

function createSpace() {
    $('#space-modal').modal({
        onApprove() {
            $.api({
                on: 'now',
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
                url: `/pm/api/projects/${PROJECT_ID}/spaces/`,
                data: {
                    name: $('#space-name').val(),
                    order: 0,
                },
                onSuccess(r) {
                    $('#space-modal').modal('hide')
                    $('body').toast({
                        message: 'Space successfully created!',
                    })
                    renderPage()
                },
                onComplete(response, element, xhr) {
                    $('#space-name').val('')
                }
            })
            return false
        }
    }).modal('show')
}

function editSpace(id) {
    name = $(`.ui.segment[data-space-id=${id}] span.space-name`).text()
    $('#space-name').val(name)
    $('#space-modal').modal({
        onApprove() {
            $.api({
                on: 'now',
                method: 'PATCH',
                headers: {'X-CSRFToken': csrftoken},
                url: `/pm/api/projects/${PROJECT_ID}/spaces/${id}/`,
                data: {
                    name: $('#space-name').val(),
                    order: 0,
                },
                onSuccess(r) {
                    $('#space-modal').modal('hide')
                    $('body').toast({
                        message: 'Space successfully updated!',
                    })
                    renderPage()
                },
                onComplete(response, element, xhr) {
                    $('#space-name').val('')
                }
            })
            return false
        }
    }).modal('show')
}

function deleteSpace(id) {
    $('body').modal({
        title: gettext('Confirmation'),
        class: 'mini',
        closeIcon: true,
        content: gettext('Delete this space?'),
        actions: [
            {
                text: gettext('Cancel'),
                class: 'deny black'
            },
            {
                text: gettext('Yes, delete it'),
                class: 'approve red',
                icon: 'delete',
            },
        ],
        onApprove: () => {
            $.api({
                on: 'now',
                method: 'DELETE',
                url: `/pm/api/projects/${PROJECT_ID}/spaces/${id}/`,
                headers: { 'X-CSRFToken': csrftoken },
                stateContext: $(`.ui.segment[data-space-id=${id}]`),
                successTest: r => r != 0,
                onSuccess: r => {
                    $('body').toast({
                        message: 'Space successfully deleted!',
                    })
                    renderPage()
                },
            })
        }
    }).modal('show');
    
}

function renderBoard(board, boardsEl) {
    boardsEl.append(`
        <div class="ui ${board.allowed_users.map(u => u.username).includes(USER) ? "" : "disabled"} card" data-board-id="${board.id}" ${board.background_image ? `style="background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.3)), url('${board.background_image}'); background-size: cover;"`: ""}>
            <div class="center aligned handle content" style="flex: 0 0 auto; display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move;">
                <i class="grip lines icon"></i>
            </div>
            <div class="content" style="padding-bottom: 0;">
                <div class="header" style="display: flex; flex-flow: row nowrap; justify-content: space-between;">
                    <div class="" style="flex: 0 1 auto; overflow-wrap: anywhere; padding-right: .5em;">
                        <a href="/pm/project/${PROJECT_ID}/board/${board.id}/">
                            ${board.name}
                        </a>
                    </div>
                    <div class="ui basic icon top right pointing card-menu dropdown button" style="flex: 0 0 auto; align-self: flex-start;">
                        <i class="ellipsis horizontal icon"></i>
                        <div class="menu">
                            <a class="item" href="/pm/project/${PROJECT_ID}/board/${board.id}/"><i class="eye icon"></i>${gettext("Open")}</a>
                            <a class="item" href="/pm/project/${PROJECT_ID}/board/${board.id}/edit/"><i class="edit icon"></i>${gettext("Edit")}</a>
                            <div class="divider"></div>
                            <a class="delete-board item" data-board-id="${board.id}"><i class="delete icon"></i>${gettext("Delete")}</a>
                        </div>
                    </div>
                </div>
                <div class="meta">
                    <p>${interpolate(gettext("Created at %s"), [stringToLocalDatetime(board.created_at, languageCode)])}</p>
                </div>
                <div class="description">
                    <div style="padding-bottom: 1em;">
                        ${getUsersHtml(board.allowed_users)}
                    </div>
                    ${getProgressBarHtml(board)}
                </div>
            </div>
        </div>
    `)
}

function initializeDeleteBoardButtons() {
    $('.delete-board').click(e => {
        let boardId = $(e.target).attr('data-board-id');
        $('body').modal({
            title: gettext('Confirm deletion'), 
            class: 'mini', 
            closeIcon: true, 
            content: gettext('Delete this board?'), 
            actions: [
                { text: 'Cancel', class: 'secondary' },
                { text: 'Delete', class: 'red approve' },
            ],
            onApprove: () => {
                $.api({
                    on: 'now',
                    method: 'DELETE',
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${boardId}/`,
                    onSuccess: response => {
                        window.location.replace(response.url);
                    },
                    onFailure: (response, element, xhr) => { console.log("Something went wrong.") },
                    onError: (errorMessage, element, xhr) => { console.log(`Request error: ${errorMessage}`) },
                });
            }
        }).modal('show');
    })
}

function getUsersHtml(users) {
    html = ''
    users.forEach(u => {
        html += `<img class="ui avatar image" src="${u.profile.avatar}" alt="" data-content="${u.username}">`
    })
    return html
}

function getProgressBarHtml(board) {
    function getPopupMessage(count, percent) {
        if (count == 0) return gettext('No cards')
        return interpolate(ngettext('%s card (%s%)', '%s cards (%s%)', count), [count, percent])
    }
    html = ''
    if (board.card_count == 0) {
        html = `
            <div class="ui tiny multiple progress" data-percent="0" style="padding-bottom: 0;" data-content="${gettext('No cards yet')}">
                <div class="bar"></div>
            </div>
        `
    } else {
        html = `
            <div class="ui tiny multiple progress" data-percent="${Object.values(board.progress).map(v => v[1])}" style="padding-bottom: 0;">
                <div class="green bar" data-title="${gettext("Completed")}" data-content="${getPopupMessage(...board.progress.completed)}"></div>
                <div class="yellow bar" data-title="${gettext("In progress")}" data-content="${getPopupMessage(...board.progress.in_progress)}"></div>
                <div class="grey bar" data-title="${gettext("Not started")}" data-content="${getPopupMessage(...board.progress.not_started)}"></div>
            </div>
        `
    }
    return html
}

function initializeInviteForm() {
    INVITE_FORM.form({
        fields: {
            email: {
                identifier  : 'email',
                rules: [
                    {
                        type   : 'empty',
                        prompt : gettext('Please enter an email')
                    },
                    {
                        type   : 'email',
                        prompt : gettext('Please enter a valid email')
                    },
                ]
            },
        },
        onSuccess: () => {
            $('body').toast({
                message: interpolate(gettext('Your invitation was sent to %s.'), [$('input.invite[type=email]').val()]),
                class: 'success',
            });
            $.api({
                url: `/pm/api/projects/${PROJECT_ID}/invites/`,
                on: 'now',
                method: "POST",
                mode: 'same-origin',
                data: {
                    email: $('input.invite[type=email]').val(),
                    project: PROJECT_ID,
                },
                onSuccess: r => {
                    loadInvites();
                    $('input.invite[type=email]').val('');
                },
                onFailure: (response, element, xhr) => {
                    for (let error of response.non_field_errors) {
                        $('body').toast({
                            message: error,
                            class: 'error',
                        })
                    }
                },
                onError: (errorMessage, element, xhr) => {
                    console.log(`Request error: ${errorMessage}`);
                },
            });
        }
    });
    INVITE_FORM.submit(e => {
        e.preventDefault();
    });
}

function removeMember(userId) {
    $('body').modal({
        title: gettext('Confirmation'),
        class: 'mini',
        closeIcon: true,
        content: gettext('Are you sure you want to remove user from this project?'),
        actions: [
            {
                text: gettext('Cancel'),
                class: 'black'
            },
            {
                text: gettext('Yes, remove user.'),
                class: 'ok red'
            },
        ],
        onApprove: () => {
            $.api({
                url: `/pm/api/projects/${PROJECT_ID}/remove-user/`,
                on: 'now',
                method: "POST",
                mode: 'same-origin',
                data: {
                    user: userId,
                },
                onSuccess: r => {
                    $('body').toast({
                        message: gettext("User successfully removed from this project's team."),
                        class: 'success',
                    });
                    sleep(2000).then(() => {
                        window.location.reload();
                    });
                },
                onFailure: (response, element, xhr) => {
                    for (let error of response.non_field_errors) {
                        $('body').toast({
                            message: error,
                            class: 'error',
                        })
                    }
                },
                onError: (errorMessage, element, xhr) => {
                    console.log(`Request error: ${errorMessage}`);
                },
            });
        }
    }).modal('show');
}

function resendInvite(inviteId) {
    $('body').modal({
        title: gettext('Confirmation'),
        class: 'mini',
        closeIcon: true,
        content: gettext('Are you sure you want to resend the email invitation?'),
        actions: [
            {
                text: gettext('Cancel'),
                class: 'black'
            },
            {
                text: gettext('Yes, resend it.'),
                class: 'ok green'
            },
        ],
        onApprove: () => {
            $.api({
                on: 'now',
                method: "POST",
                url: `/pm/api/projects/${PROJECT_ID}/invites/${inviteId}/resend/`,
                onSuccess: r => {
                    $('body').toast({
                        message: r.message,
                        class: 'success',
                    });
                    loadInvites();
                    $('input.invite[type=email]').val('');
                },
                onFailure: (response, element, xhr) => {
                    for (let error of response.non_field_errors) {
                        $('body').toast({
                            message: error,
                            class: 'error',
                        })
                    }
                },
                onError: (errorMessage, element, xhr) => {
                    console.log(`Request error: ${errorMessage}`);
                },
            });
        }
    }).modal('show');
}

function deleteInvite(inviteId) {
    $('body').modal({
        title: gettext('Confirmation'),
        class: 'mini',
        closeIcon: true,
        content: gettext('Are you sure you want to delete this invite?'),
        actions: [
            {
                text: gettext('Cancel'),
                class: 'black'
            },
            {
                text: gettext('Yes, delete it.'),
                class: 'ok red'
            },
        ],
        onApprove: () => {
            $.api({
                on: 'now',
                method: "DELETE",
                url: `/pm/api/projects/${PROJECT_ID}/invites/${inviteId}/`,
                onSuccess: r => {
                    $('body').toast({
                        message: gettext('Invite deleted successfully.'),
                        class: 'success',
                    });
                    loadInvites();
                    $('input.invite[type=email]').val('');
                },
                onFailure: (response, element, xhr) => {
                    for (let error of response.non_field_errors) {
                        $('body').toast({
                            message: error,
                            class: 'error',
                        })
                    }
                },
                onError: (errorMessage, element, xhr) => {
                    console.log(`Request error: ${errorMessage}`);
                },
            });
        }
    }).modal('show');
}

function loadInvites() {
    $('#invites').empty();
    $.get(
        url=`/pm/api/projects/${PROJECT_ID}/invites/`
    )
    .done(r => {
        if (r.length === 0) {
            $('#invites').append(gettext('No invites yet'))
        } else {
            $('#invites').append(`
                <div style="overflow-x: auto;">
                    <table class="ui unstackable celled table">
                        <thead>
                            <tr>
                                <th>${gettext('Email')}</th>
                                <th>${gettext('Created')} at</th>
                                <th>${gettext('Accepted')}</th>
                                <th>${gettext('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                </div>
            `);
            r.forEach(invite => {
                if (invite.email !== null && invite.email !== '') {
                    created_at = new Date(invite.created_at)
                    $('#invites tbody').append(`
                        <tr class="${invite.accepted_by !== null ? 'positive' : 'negative'}">
                            <td>${invite.email}</td>
                            <td>${created_at}</td>
                            <td>${invite.accepted_by !== null ? '<i class="checkmark icon"></i>' : '<i class="delete icon"></i>'}</td>
                            <td>
                                <div class="ui tiny primary icon ${invite.accepted_by !== null ? 'disabled' : ''} button" data-content="${gettext('Resend email')}" onclick="resendInvite(${invite.id})"><i class="sync icon"></i></div>
                                <div class="ui tiny red icon ${invite.accepted_by !== null ? 'disabled' : ''} button" data-content="${gettext('Delete')}" onclick="deleteInvite(${invite.id})"><i class="delete icon"></i></div>
                            </td>
                        </tr>
                    `);
                };
            })
        }
    })
};

function sort() {
    field = $('#sort-field-dropdown').dropdown('get value');
    direction = $('#sort-direction-dropdown').dropdown('get value');
    url = `/pm/project/{{ object.id }}/?field=${ field == '' ? 'created_by' : field }&direction=${ direction == '' ? 'asc' : direction }`;
    window.location.replace(url);
}

function initializeFilterDropdowns() {
    $('#sort-field-dropdown').dropdown({
        action: 'select',
        onChange: sort,
    }).dropdown('set value', 'name', null, null, preventChangeTrigger=true);
    $('#sort-direction-dropdown').dropdown({
        action: 'select',
        onChange: sort,
    }).dropdown('set value', 'asc', null, null, preventChangeTrigger=true);
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

function retrieveSpaces() {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/pm/api/projects/${PROJECT_ID}/spaces/`,
        onSuccess(response, element, xhr) {
            console.log(response)
        }
    })
}