function sort() {
    field = $('#sort-field-dropdown').dropdown('get value');
    direction = $('#sort-direction-dropdown').dropdown('get value');
    url = `/pm/projects/?field=${ field == '' ? 'created_by' : field }&direction=${ direction == '' ? 'asc' : direction }`;
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

function initializeDeleteButtons() {
    $('.delete-project').click(e => {
        let projectId = $(e.target).attr('data-project-id');
        $('body').modal({
            title: 'Confirm deletion', 
            class: 'mini', 
            closeIcon: true, 
            content: 'Delete this project?', 
            actions: [
                { text: 'Cancel', class: 'secondary' },
                { text: 'Delete', class: 'red approve' },
            ],
            onApprove: () => {
                $.api({
                    url: `/pm/api/projects/${projectId}/`,
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

function initializeCardMenuDropdown() {
    $('.ui.card-menu.dropdown').dropdown({
        action: 'hide'
    })
}