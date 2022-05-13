function toast(title, message) {
    $('body').toast({
        title: title,
        message: message
    })
}

function renderList(checklistId, checklistName) {
    listsDiv.append(`
        <a class="teal checklist item" data-checklist-id="${checklistId}" onclick="selectChecklist(${checklistId})" style="display: flex; flex-flow: row nowrap; align-items: center;">
            <div style="flex: 1 0 0;">
                <span class="checklist-name">${checklistName}</span>
            </div>
            <div style="flex: 0 0 auto;">
                <div class="ui circular icon mini checklist button" onclick="editChecklist(${checklistId})">
                    <i class="edit icon"></i>
                </div>
                <div class="ui circular icon mini red checklist button" onclick="deleteChecklist(${checklistId})" style="margin-left: .5em;">
                    <i class="delete icon"></i>
                </div>
            </div>
        </a>
    `)
}

function renderTask(taskId, taskDescription, checked) {
    tasksDiv.append(`
        <a class="teal task item" data-task-id="${taskId}" data-checked="${checked}" style="display: flex; ">
            <div class="ui checkbox" data-task-id="${taskId}" style="flex: 0 0 auto;">
                <input type="checkbox" ${checked ? "checked" : ""}>
            </div>
            <span class="task-description">${taskDescription}</span>
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
    $(`.task.item[data-task-id=${taskId}]`).off().click(e => {
        if ($(e.target).hasClass('checkbox') || $(e.target).parent().hasClass('checkbox')) { return }
        selectedTask = sessionStorage.getItem('selectedTask')
        if ($(e.target).closest('.task.item').hasClass('active')) {
            toggleTaskPanel()
        } else {
            selectTask(taskId)
        }
    })
}

function createTask(taskDescription) {
    checklistId = sessionStorage.getItem('selectedChecklist')
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
            renderTask(r.id, r.description, r.checked_at != null)
        }
    })
}

async function createChecklist(checklistName) {
    $.api({
        on: 'now',
        method: 'POST',
        url: `/cl/api/checklists/`,
        data: {
            name: checklistName,
        },
        onSuccess: r => {
            renderList(r.id, r.name)
        }
    })
}

function retrieveLists() {
    $.api({
        on: 'now',
        url: '/cl/api/checklists/',
        successTest: r => true,
        onSuccess: r => {
            listsDiv.empty()
            r.results.forEach(
                item => renderList(item.id, item.name)
            )
        }
    })
}

function selectChecklist(checklistId) {
    sessionStorage.removeItem('selectedTask')
    retrieveTasks(checklistId)
    hideTaskPanel()
    $('*.checklist.item').removeClass('active')
    $(`.checklist.item[data-checklist-id=${checklistId}]`).addClass('active')
}

async function retrieveTasks(checklistId) {
    sessionStorage.setItem('selectedChecklist', checklistId)
    $.api({
        url: `/cl/api/checklists/${checklistId}/`,
        on: 'now',
        method: 'GET',
        stateContext: '#tasks-div',
        onSuccess: checklist => {
            $('#list-name').text(checklist.name);
        }
    })
    $.api({
        url: `/cl/api/tasks/?checklist__id=${checklistId}`,
        on: 'now',
        method: 'GET',
        stateContext: '#tasks-div',
        onSuccess: r => {
            tasksDiv.empty();
            r.results.forEach(
                item => {
                    renderTask(item.id, item.description, item.checked_at != null)
                    selectedTask = sessionStorage.getItem('selectedTask')
                    if (item.id == selectedTask) { $(`.task.item[data-task-id=${selectedTask}]`).addClass('active') }
                }
            )
            initializeTaskList()
        }
    })
}

function checkTask(taskId) {
    $.api({
        on: 'now',
        method: 'post',
        url: `/cl/api/tasks/${taskId}/check/`,
        onSuccess(r) {
            $(`.task.item[data-task-id=${taskId}] .ui.checkbox`).checkbox('check')
            $(`.task.item[data-task-id=${taskId}]`).attr('data-checked', true)
            selectedTask = sessionStorage.getItem('selectedTask')
            if (taskId === selectedTask) {
                $('#check-icon').addClass('check circle outline')
                $('#task-description').attr('data-checked', true)
            }
        }
    })
}

function uncheckTask(taskId) {
    $.api({
        on: 'now',
        method: 'post',
        url: `/cl/api/tasks/${taskId}/uncheck/`,
        onSuccess(r) {
            $(`.task.item[data-task-id=${taskId}] .ui.checkbox`).checkbox('uncheck')
            $(`.task.item[data-task-id=${taskId}]`).attr('data-checked', false)
            selectedTask = sessionStorage.getItem('selectedTask')
            if (taskId === selectedTask) {
                $('#check-icon').removeClass('check circle outline').addClass('circle outline')
                $('#task-description').attr('data-checked', false)
            }
        }
    })
}

function toggleSelectedTask() {
    taskId = sessionStorage.getItem('selectedTask')
    checklistId = sessionStorage.getItem('selectedChecklist')
    if ($(`.task.item[data-task-id="${taskId}"] .ui.checkbox`).checkbox('is checked')) {
        uncheckTask(taskId)
    } else {
        checkTask(taskId)
    }
}

function updateTask(data) {
    taskId = sessionStorage.getItem('selectedTask')
    checklistId = sessionStorage.getItem('selectedChecklist')
    $.api({
        on: 'now',
        method: 'PATCH',
        url: `/cl/api/tasks/${taskId}/`,
        stateContext: '#task-detail .segment',
        data: data,
        onSuccess(response, element, xhr) {
            retrieveTasks(checklistId)
        },
        onFailure(response, element, xhr) {
            toast(response)
        }
    })
}

function selectTask(taskId) {
    $('*.task.item').removeClass('active')
    $(`.task.item[data-task-id=${taskId}]`).addClass('active')
    $.api({
        on: 'now',
        url: `/cl/api/tasks/${taskId}/`,
        stateContext: '#task-detail .segment',
        onSuccess: r => {
            sessionStorage.setItem('selectedTask', taskId)
            renderTaskDetails(r)
            showTaskPanel()
            attachTaskUpdateEvents()
        }
    })
}

function renderTaskDetails(task) {
    $("#task-description").val(task.description)
    $("#task-note").val(task.note)
    if (task.checked_at) {
        $("#task-description").attr('data-checked', true)
        $('#check-icon').addClass('check circle outline')
        ts = new Date(task.checked_at)
        msg = interpolate(gettext('Checked at %s'), [ts.toString()])
    } else {
        $("#task-description").attr('data-checked', false)
        $('#check-icon').removeClass('check circle outline').addClass('circle outline')
        ts = new Date(task.created_at)
        msg = interpolate(gettext('Created at %s'), [ts.toString()])
    }
    $('#task-timestamp').text(msg)
    if (task.reminder === null) {
        $('#task-reminder').calendar('set date', null, true, false)
    } else {
        localReminder = new Date(task.reminder);
        utcReminder = new Date(localReminder.toUTCString().slice(0, -4));
        $('#task-reminder').calendar('set date', new Date(task.reminder), true, false)
    }
    if (task.due_date === null) {
        $('#task-due-date').calendar('set date', null, true, false)
    } else {
        localDueDate = new Date(task.due_date);
        utcDueDate = new Date(localDueDate.toUTCString().slice(0, -4));
        $('#task-due-date').calendar('set date', utcDueDate, true, false)
    }
}

function attachTaskUpdateEvents() {
    $("#task-description").off().on('input', e => {
        clearTimeout(updateTaskTimeout)
        updateTaskTimeout = setTimeout(function () {
            updateTask({
                note: $('#task-note').val(),
                description: $('#task-description').val()
            })
        }, 1000)
    })
    $("#task-note").off().on('input', e => {
        clearTimeout(updateTaskTimeout)
        updateTaskTimeout = setTimeout(function () {
            updateTask({
                note: $('#task-note').val(),
                description: $('#task-description').val(),
            })
        }, 1000)
    })
}

function deleteTask() {
    $('.ui.sidebar').sidebar('hide')
    $('body').modal({
        title: gettext('Confirmation'),
        class: 'mini',
        closeIcon: true,
        content: gettext('Are you sure you want to delete this task?'),
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
            taskId = sessionStorage.getItem('selectedTask')
            checklistId = sessionStorage.getItem('selectedChecklist')
            $.api({
                on: 'now',
                method: 'DELETE',
                url: `/cl/api/tasks/${taskId}`,
                onSuccess: r => {
                    sessionStorage.removeItem('selectedTask')
                    retrieveTasks(checklistId)
                    hideTaskPanel()
                }
            })
        }
    }).modal('show');
}
function deleteChecklist(id) {
    $('.ui.sidebar').sidebar('hide')
    $('body').modal({
        title: gettext('Confirmation'),
        class: 'mini',
        closeIcon: true,
        content: gettext('Are you sure you want to delete this checklist?'),
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
            $.api({
                on: 'now',
                method: 'DELETE',
                url: `/cl/api/checklists/${id}`,
                onSuccess: r => {
                    if (id == sessionStorage.getItem('selectedChecklist')) {
                        sessionStorage.removeItem('selectedChecklist')
                        hideTaskPanel()
                    }
                    retrieveLists()
                }
            })
        }
    }).modal('show');
}

function showNewChecklistModal() {
    $('.ui.sidebar').sidebar('hide')
    modal = $('#new-checklist')
    input = modal.find('input[name=name]')
    modal.modal({
        onShow: () => {
            input.val('')
            input.off().on('keyup', function (e) {
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

function editChecklist(checklistId) {
    $('.ui.sidebar').sidebar('hide')
    modal = $('#new-checklist')
    input = modal.find('input[name=name]')
    selectedChecklist = sessionStorage.getItem('selectedChecklist')
    modal.modal({
        onShow: () => {
            input.val($(`.checklist.item[data-checklist-id=${checklistId}] .checklist-name`).first().text())
            input.off().on('keyup', function (e) {
                if (e.key === 'Enter' || e.keyCode === 13) {
                    renameChecklist(checklistId, input.val())
                    modal.modal('hide')
                }
            })
        },
        onApprove: () => {
            renameChecklist(checklistId, input.val())
        }
    }).modal('show')
}

function renameChecklist(id, name) {
    $.api({
        on: 'now',
        method: 'PATCH',
        url: `/cl/api/checklists/${id}/`,
        data: { name: name },
        onSuccess() {
            toast('Checklist', gettext('Successfully renamed!'))
            retrieveLists()
        }
    })
}

function showNewTaskModal() {
    modal = $('#new-task')
    input = modal.find('input[name=name]')
    modal.modal({
        onShow: () => {
            input.val('')
            input.off().on('keyup', function (e) {
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

function hideTaskPanel() {
    $('#task-detail').parent().hide('swing')
    $('#task-list-panel').addClass('active')
}
function showTaskPanel() {
    $('#task-detail').parent().show('swing')
    $('#task-list-panel').removeClass('active')
}
function toggleTaskPanel() {
    $('#task-detail').parent().toggle('swing')
    $('#task-list-panel').toggleClass('active')
}

function initializeDragAndDrop() {
    dragula({
        isContainer: el => $(el).attr('id') === 'tasks-div',
        moves: (el, source, handle, sibling) => $(el).hasClass('task item'),
        direction: 'vertical',
    }).on('drop', (el, target, source, sibling) => {
        order = $(target).children().toArray().findIndex(e => e == el) + 1
        taskId = $(el).attr('data-task-id')
        $.api({
            on: 'now',
            method: 'POST',
            url: '/cl/api/task-move/',
            headers: { 'X-CSRFToken': csrftoken },
            stateContext: '#tasks-div',
            data: {
                task: taskId,
                order: order,
            },
            onSuccess: result => { },
        })
    })
    dragula({
        isContainer: el => $(el).attr('id') === 'lists-div',
        moves: (el, source, handle, sibling) => $(el).hasClass('checklist item'),
        direction: 'vertical',
    }).on('drop', (el, target, source, sibling) => {
        order = $(target).children().toArray().findIndex(e => e == el) + 1
        checlistId = $(el).attr('data-checklist-id')
        $.api({
            on: 'now',
            method: 'POST',
            url: '/cl/api/checklist-move/',
            headers: { 'X-CSRFToken': csrftoken },
            stateContext: '#lists-div',
            data: {
                checklist: checlistId,
                order: order,
            },
            onSuccess: result => { },
        })
    })
}

function initializeTaskList() {
    clearSearch()
    var options = {
        listClass: 'filter-list',
        valueNames: [
            'task-description',
        ]
    };
    taskList = new List('task-list-panel', options);
}

function clearSearch() {
    $('#search').val('')
}

function initializeDueDate() {
    $('#task-due-date').calendar({
        type: 'date',
    })
    $('#task-due-date').calendar({
        type: 'date',
        onChange() {
            dueDate = $('#task-due-date').calendar('get date')
            if (dueDate != null) {
                dueDate = $('#task-due-date').calendar('get date').toISOString().split('T')[0]
            }
            updateTask({
                due_date: dueDate
            })
        }
    })
}



function initializeReminder() {
    $('#task-reminder').calendar({
        type: 'datetime',
        disableMinute: true,
        ampm: false,
        onChange() {
            reminder = $('#task-reminder').calendar('get date')
            if (reminder != null) {
                reminder = $('#task-reminder').calendar('get date').toISOString()
            }
            updateTask({
                reminder: reminder
            })
        }
    })
}

function clearDueDate() {
    $('#task-due-date').calendar('set date', null, true, false)
    updateTask({
        due_date: null
    })
}

function clearReminder() {
    $('#task-reminder').calendar('set date', null, true, false)
    updateTask({
        reminder: null
    })
}
