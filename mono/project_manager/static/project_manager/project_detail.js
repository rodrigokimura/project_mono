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

function initializeDeleteBoardButtons() {
    $('.delete-board').click(e => {
        let boardId = $(e.target).attr('data-board-id');
        $('body').modal({
            title: 'Confirm deletion', 
            class: 'mini', 
            closeIcon: true, 
            content: 'Delete this board?', 
            actions: [
                { text: 'Cancel', class: 'secondary' },
                { text: 'Delete', class: 'red approve' },
            ],
            onApprove: () => {
                $.api({
                    url: `/pm/api/projects/${PROJECT_ID}/boards/${boardId}/`,
                    method: 'DELETE',
                    mode: 'same-origin',
                    headers: {'X-CSRFToken': csrftoken},
                    cache: false,
                    on: 'now',
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
                headers: {'X-CSRFToken': csrftoken},
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
    console.log(`Removing member ${userId}`);
    $('body').modal({
        title: 'Confirmation',
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
                headers: {'X-CSRFToken': csrftoken},
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
        title: 'Confirmation',
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
                url: `/pm/api/projects/${PROJECT_ID}/invites/${inviteId}/resend/`,
                on: 'now',
                method: "POST",
                mode: 'same-origin',
                headers: {'X-CSRFToken': csrftoken},
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
        title: 'Confirmation',
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
                url: `/pm/api/projects/${PROJECT_ID}/invites/${inviteId}/`,
                on: 'now',
                method: "DELETE",
                mode: 'same-origin',
                headers: {'X-CSRFToken': csrftoken},
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