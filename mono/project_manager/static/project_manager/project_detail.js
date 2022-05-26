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
        url: `/pm/api/projects/${PROJECT_ID}/boards/`,
        stateContext: '#grid',
        onSuccess(response) {
            if (response.length == 0) {
                renderPlaceholder()
                return
            }
            renderBoards(response)
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

function renderBoard(board) {
    boardsEl = $('#boards')
    boardsEl.append(`
        <div class="ui card" data-board-id="${board.id}">
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
            <div class="ui tiny multiple progress" data-percent="0" style="padding-bottom: 0;" data-content="{% translate "No cards yet" %}">
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
    console.log(`Resending invite ${inviteId}`);
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
        [$('#boards')[0]],
        {
            direction: 'horizontal',
        }
    )
    .on('drop', (el, target, source, sibling) => {
        board = $(el).attr('data-board-id')
        order = $(target).children().toArray().findIndex(e => e == el) + 1
        console.log(board)
        $.api({
            on: 'now',
            url: `/pm/api/board-move/`,
            method: 'POST',
            stateContext: '#boards',
            data: {
                project: PROJECT_ID,
                board: board,
                order: order,
            },
            onSuccess: r => {
                $('body').toast({
                    title: 'Success',
                    message: 'Board order updated successfully',
                    class: 'success',
                })
            },
            onFailure(response) {
                console.log(response)
                $('body').toast({
                    title: 'Failure',
                    message: 'A problem occurred while updating chart order',
                    class: 'error',
                })
                renderBoards()
            },
        });
    })
}