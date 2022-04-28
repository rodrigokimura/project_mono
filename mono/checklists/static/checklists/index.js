function renderList(checklistId, checklistName) {
    listsDiv.append(`
        <a class="item" data-list-id="${checklistId}" onclick="retrieveTasks(${checklistId})">
            ${checklistName}
            <div class="ui icon label" onclick="window.location.href='/cl/list/${checklistId}/edit/'">
                <i class="edit icon"></i>
            </div>
        </a>
    `)
}

function renderTask(checklistId, taskId, taskDescription, checked) {
    tasksDiv.append(`
        <a class="task item" data-task-id="${taskId}" data-checked="${checked}" style="display: flex; ">
            <div class="ui checkbox" data-task-id="${taskId}" style="flex: 0 0 auto;">
                <input type="checkbox" ${checked ? "checked" : ""}>
            </div>
            <span>${taskDescription}</span>
        </a>
    `)
    $(`.ui.checkbox[data-task-id=${taskId}]`).checkbox({
        onChecked() {
            taskId = $(this).closest('.task.item').attr('data-task-id')
            checkTask(taskId)
        },
        onUnchecked() {
            taskId = $(this).closest('.task.item').attr('data-task-id')
            uncheckTask(taskId)
        },
    })
    $(`.task.item[data-task-id=${taskId}]`).click(e => {
        if ($(e.target).hasClass('task')) {
            showTaskDetail(checklistId, taskId)
        }
    })
}

function createTask(taskDescription) {
    checklistId = sessionStorage.getItem('selectedChecklist')
    console.log(checklistId)
    $.api({
        on: 'now',
        method: 'POST',
        url: `/cl/api/tasks/`,
        data: {
            checklist: checklistId,
            description: taskDescription,
            order: 5
        },
        onSuccess: r => {
            renderTask(checklistId, r.id, r.description, r.checked_at != null)
        }
    })
}

async function createChecklist(checklistName) {
    $.api({
        on: 'now',
        method: 'POST',
        url: `/cl/api/checklists/`,
        data: {
            "name": checklistName,
        },
        onSuccess: r => {
            renderList(r.id, r.name)
        }
    })
}

function retrieveLists() {
    // Retrieves lists from api and inserts to DOM
    $.api({
        on: 'now',
        url: '/cl/api/checklists/',
        successTest: r => true,
        onSuccess: r => {
            r.results.forEach(
                item => renderList(item.id, item.name)
            )
        }
    })
}

function retrieveTasks(checklistId) {
    sessionStorage.setItem('selectedChecklist', checklistId)
    $.api({
        url: `/cl/api/checklists/${checklistId}/`,
        on: 'now',
        method: 'GET',
        stateContext: '#list-name',
        onSuccess: task => {
            $('#list-name').text(task.name);
        }
    })
    $.api({
        url: `/cl/api/tasks/?checklist__id=${checklistId}`,
        on: 'now',
        method: 'GET',
        stateContext: '#list-name',
        onSuccess: r => {
            tasksDiv.empty();
            tasksDiv.attr("data-list-id", checklistId)
            r.results.forEach(
                item => {
                    renderTask(checklistId, item.id, item.description, item.checked_at != null)
                }
            )
        }
    })
}

function checkTask(taskId) {
    // Marks task as checked
    $.post(url=`/cl/api/tasks/${taskId}/check/`)
        .done(tasks => {
            $(`.task.item[data-task-id=${taskId}]`).attr('data-checked', true);
            $(`.task.item[data-task-id=${taskId}] input`).prop('checked', true);
        })
        .fail()
        .always()
}

function uncheckTask(taskId) {
    // Marks task as unchecked
    $.post(url=`/cl/api/tasks/${taskId}/uncheck/`)
        .done(tasks => {
            $(`.task.item[data-task-id="${taskId}"]`).attr('data-checked', false);
            $(`.task.item[data-task-id="${taskId}"] input`).prop('checked', false);
        })
        .fail()
        .always()
}

function toggleTask(checklistId, taskId) {
    checked = $(`.task.item[data-task-id="${taskId}"]`).attr('data-checked');
    if (checked == "true") {
        uncheckTask(checklistId, taskId);
    } else {
        checkTask(checklistId, taskId);
    }
}

function showTaskDetail(checklistId, taskId) {
    $.api({
        on: 'now',
        url: `/cl/api/tasks/${taskId}/`,
        onSuccess: r => {
            deleteButton = $("#delete-task-btn")
            deleteButton.attr("data-list-id", checklistId)
            deleteButton.attr("data-task-id", taskId)
            $("#modal-task-description").val(r.description)
            $('#task-detail').parent().show('swing')
            if (r.checked_at) {
                ts = new Date(r.checked_at)
                msg = 'Checked at ' + ts.toString()
            } else {
                ts = new Date(r.created_at)
                msg = 'Created at ' + ts.toString()
            }
            $('#task-timestamp').text(msg)
            // $("#edit-task-modal").modal({
            //     onApprove: () => {
            //         $.api({
            //             url: `/cl/api/tasks/${taskId}/`,
            //             method: 'PATCH',
            //             on: 'now',
            //             data: {
            //                 description: $('#modal-task-description').val(),
            //             },
            //             onSuccess: r => {
            //                 retrieveTasks(checklistId);
            //             }
            //         })
            //     }
            // }).modal("show");
        }
    })
}

function deleteTask() {
    deleteButton = $("#delete-task-btn")
    checklistId = deleteButton.attr("data-list-id")
    taskId = deleteButton.attr("data-task-id")
    $.api({
        method: 'DELETE',
        url: `/cl/api/tasks/${taskId}`,
        onSuccess: r => {
            retrieveTasks(checklistId)
            $(".ui.task.modal").modal("hide")
        }
    })
}

function showNewChecklistModal() {
    modal = $('#new-checklist')
    input = modal.find('input[name=name]')
    modal.modal({
        onShow: () => {
            input.val('')
            input.on('keyup', function (e) {
                if (e.key === 'Enter' || e.keyCode === 13) {
                    createChecklist(input.val())
                    modal.modal('hide')
                }
            })
        },
        onApprove: () => {
            createChecklist(input.val())
        }
    }).modal('show')
}

function showNewTaskModal() {
    modal = $('#new-task')
    input = modal.find('input[name=name]')
    modal.modal({
        onShow: () => {
            input.val('')
            input.on('keyup', function (e) {
                if (e.key === 'Enter' || e.keyCode === 13) {
                    createTask(input.val())
                    modal.modal('hide')
                }
            })
        },
        onApprove: () => {
            createTask(input.val())
        }
    }).modal('show')
}
