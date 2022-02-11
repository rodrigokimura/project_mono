function desselectButtons(sidebar = true) {
    if (sidebar) {
        $('#search').val('');
        $('.main.menu .item').removeClass('teal').removeClass('active');
    }
    $('.snippets.menu .item').removeClass('teal').removeClass('active');
}
function showAll() {
    desselectButtons();
    button = $('#show-all');
    button.addClass('active');
    getSnippets();
    getLanguages();
    getTags();
}
function selectLanguage(language) {
    desselectButtons();
    button = $(`.menu .item[data-language='${language}']`);
    button.addClass('active');
    getSnippets(filter={'language': language});
}
function selectTag(tag) {
    desselectButtons();
    button = $(`.menu .item[data-tag='${tag}']`);
    button.addClass('active');
    if (tag == 'null') {
        getSnippets(filter={'tags__isnull': true});
    } else {
        getSnippets(filter={'tags__name': tag});
    }
}
function getSnippetFromStorage(snippetId) {
    snippets = JSON.parse(sessionStorage.getItem('snippets'));
    return snippets.find(snippet => snippet.id == snippetId);
}
function filterSnippets(query) {
    delay = 2000;
    lastFilterTimestamp = parseInt(sessionStorage.getItem('lastFilterTimestamp'));

    if (Date.now() < lastFilterTimestamp + delay) {
        console.log('Filtering too fast');
        return
    }

    snippets = JSON.parse(sessionStorage.getItem('snippets'));
    renderSnippets(snippets.filter(snippet => snippet.code.includes(query)));
    sessionStorage.setItem('lastFilterTimestamp', Date.now());
}
function getTagsHtml(tags) {
    if (tags.length == 0) {
        return '';
    }
    html = '';
    for (tag of tags) {
        html += `<div class="ui ${tag.color} label" data-tag-id="${tag.id}" style="margin-right: .5em;">${tag.name}</div>`;
    }
    return `<div>${html}</div>`;
}
function selectSnippet(snippetId) {
    desselectButtons(sidebar = false);
    button = $(`.menu .item[data-snippet-id=${snippetId}]`);
    button.addClass('teal').addClass('active');
    snippet = getSnippetFromStorage(snippetId);
    let el = $('#snippet');
    el.empty();
    el.append(`
        <div class="ui top attached teal segment" style="flex: 0 0 auto;">
            <h1 class="ui header">
                ${snippet.title}
                <div class="ui right floated red icon button" onclick="deleteSnippet(${snippetId})" data-content="Delete" data-variation="inverted">
                    <i class="delete icon"></i>
                </div>
                <div class="ui right floated yellow icon button" onclick="showModal(${snippetId})" data-content="Edit" data-variation="inverted">
                    <i class="edit icon"></i>
                </div>
                <div class="ui right floated icon button" onclick="copySnippet(${snippetId})" data-content="Copy" data-variation="inverted">
                    <i class="copy icon"></i>
                </div>
            </h1>
            <div class="ui header">${snippet.language}</div>
            ${getTagsHtml(snippet.tags)}
        </div>
        <div class="snippet highlight" style="width: 100%; overflow: auto; padding: 1em; flex: 1 1 auto;">${snippet.html}</div>
        <div class="ui bottom attached segment" style="display: flex; flex-flow: row nowrap; justify-content: space-between; align-items: baseline; width: 100%; padding: .5em; flex: 0 1 auto; margin-bottom: 0;">
            <div class="ui slider checkbox" id="public-checkbox" style="padding: 1em;">
                <input type="checkbox" name="newsletter">
                <label>Public</label>
            </div>
            <div class="ui action hidden input" style="flex: 1 0 auto; padding-left: .5em !important; padding-right: .75em !important;" id="public-id">
                <input type="url" readonly value="${`${window.location.origin}/cd/snippet/${snippet.public_id}/`}">
                <button class="ui teal right labeled icon button" onclick="copyPublicLink(${snippet.id})">
                    <i class="copy icon"></i>
                    Copy
                </button>
            </div>
        </div>
    `);
    $('.icon.button').popup(
        {
            position: 'top center',
            inverted: true,
        }
    );
    if (snippet.public) {
        $('#public-checkbox').checkbox('check');
        $('#public-id').removeClass('hidden');
    }
    $('.ui.checkbox').checkbox({
        onChecked: () => {
            $.api({
                on: 'now',
                url: `/cd/api/snippets/${snippetId}/`,
                method: 'PATCH',
                data: { public: true },
                headers: { 'X-CSRFToken': csrftoken },
                stateContext: '.ui.bottom.attached.segment',
                onSuccess: r => {
                    $('#public-id').removeClass('hidden');
                    $('body').toast({
                        title: 'Publish',
                        message: 'Snippet visibility was set to public.'
                    });
                }
            });
        },
        onUnchecked: () => {
            $.api({
                on: 'now',
                url: `/cd/api/snippets/${snippetId}/`,
                method: 'PATCH',
                data: { public: false },
                headers: { 'X-CSRFToken': csrftoken },
                stateContext: '.ui.bottom.attached.segment',
                onSuccess: r => {
                    $('#public-id').addClass('hidden');
                    $('body').toast({
                        title: 'Publish',
                        message: 'Snippet is now private.'
                    });
                }
            });
        },
    });
}
function getSnippets(filter = undefined) {
    $('#snippet').empty();
    let url = '/cd/api/snippets/';
    if (filter) {
        url += '?' + $.param(filter);
    }
    $.api({
        on: 'now',
        url: url,
        stateContext: '.snippets',
        onSuccess: function(response) {
            snippets = response.results;
            sessionStorage.setItem('snippets', JSON.stringify(snippets));
            renderSnippets(snippets);
            if (!filter) { $('#count-all').text(snippets.length); }
        }
    })
}
function deleteSnippet(id) {
    $('body').modal({
        title: 'Confirmation',
        class: 'mini',
        closeIcon: true,
        content: 'Are you sure you want to delete this snippet?',
        actions: [
            {
                text: 'Cancel',
                 class: 'black deny'
            },
            {
                text: 'Yes, delete it.',
                 class: 'red approve'
            },
        ],
        onApprove: () => {
            let url = `/cd/api/snippets/${id}`;
            $.api({
                on: 'now',
                url: url,
                method: 'DELETE',
                headers: { 'X-CSRFToken': csrftoken },
                stateContext: '.delete.button',
                onSuccess: function(response) {
                    $('body').toast({
                        title: 'Deletion',
                        message: 'Snippet deleted successfully.'
                    })
                    showAll();
                }
            });
        }
    }).modal('show');
}
function renderSnippets(snippets) {
    let el = $('.snippets');
    el.empty();
    if (snippets.length > 0) {
        snippets.forEach(snippet => {
            el.append(`
                <a class="item" data-snippet-id="${snippet.id}" onclick="selectSnippet('${snippet.id}')">
                    ${snippet.title}
                </a>
            `);
        });
    }
}
function getLanguages() {
    let el = $('.languages.menu');
    $.api({
        on: 'now',
        url: '/cd/api/snippets/languages/',
        stateContext: '.languages.segment',
        onSuccess: r => {
            renderLanguages(r);
        }
    })
}
function renderLanguages(languages) {
    let el = $('.languages.menu');
    el.empty();
    if (languages.length > 0) {
        languages.forEach(item => {
            el.append(
                `
                <a class="item" data-language="${item.language}" onclick="selectLanguage('${item.language}')" style="padding-right: 0; padding-left: 0;">
                    ${item.language}
                    <div class="ui label">${item.count}</div>
                </a>
                `
            );
        });
    } else {
        el.append(`
            <div class="ui disabled item" style="padding-right: 0; padding-left: 0;">
                No languages found
            </div>
        `);
    }
}
function getTags() {
    let el = $('.tags.menu');
    $.api({
        on: 'now',
        url: '/cd/api/snippets/tags/',
        stateContext: '.tags.segment',
        onSuccess: r => {
            renderTags(r);
        }
    })
}
function renderTags(tags) {
    let el = $('.tags.menu');
    el.empty();
    if (tags.length > 0) {
        tags.forEach(item => {
            el.append(
                `
                <a class="item" data-tag="${item.tag}" onclick="selectTag('${item.tag}')" style="padding-right: 0; padding-left: 0;">
                    ${item.tag ? item.tag : 'No tag'}
                    <div class="ui label">${item.count}</div>
                </a>
                `
            );
        });
    } else {
        el.append(`
            <div class="ui disabled item" style="padding-right: 0; padding-left: 0;">
                No tags found
            </div>
        `);
    }
}
function getFormInputData() {
    language = $('#languages-dropdown').dropdown('get value');
    title = $('input[name=title]').val();
    code = $('textarea[name=code]').val();
    return {
        title: title,
        language: language,
        code: code,
    }
}
function setFormInputData(snippetId) {
    snippet = getSnippetFromStorage(snippetId);
    $('#languages-dropdown').dropdown('set value', snippet.language);
    $('input[name=title]').val(snippet.title);
    $('textarea[name=code]').val(snippet.code);
}
function showModal(id = null) {
    let creation = id === null;
    if (creation) {
        title = 'Creting snippet';
        method = 'POST';
        url = '/cd/api/snippets/';
        resetForm();
    } else {
        title = 'Editing snippet';
        method = 'PUT';
        url = `/cd/api/snippets/${id}/`;
        setFormInputData(id);
    }
    $('#modal-title').text(title);
    $('.ui.modal')
        .modal({
            onApprove: () => {
                $.api({
                    on: 'now',
                    url: url,
                    method: method,
                    headers: { 'X-CSRFToken': csrftoken },
                    data: getFormInputData(),
                    onSuccess: r => {
                        $('body').toast({
                            title: 'Creation',
                            message: 'Snippet created successfully.',
                            class: 'success'
                        });
                        showAll();
                    }
                })
            },
        })
        .modal('show');
}
function resetLanguagesDropdown() {
    $('#languages-dropdown').dropdown('restore defaults');
}
function resetForm() {
    resetLanguagesDropdown();
    $('input[name=title]').val('');
    $('textarea[name=code]').val('');
}
function copySnippet(snippetId) {
    snippet = getSnippetFromStorage(snippetId);
    copyTextToClipboard(snippet.code);
    $('body').toast({
        title: 'Copying',
        message: 'Snippet copied successfully.',
        class: 'success'
    });
}
function copyPublicLink(snippetId) {
    snippet = getSnippetFromStorage(snippetId);
    copyTextToClipboard(`${window.location.origin}/cd/snippet/${snippet.public_id}/`);
    $('body').toast({
        title: 'Copying',
        message: 'Public link copied successfully.',
        class: 'success'
    });
}