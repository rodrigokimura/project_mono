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
    getSnippetTags();
}
function selectLanguage(language) {
    desselectButtons();
    button = $(`.menu .item[data-language='${language}']`);
    button.addClass('active');
    getSnippets(filter = { 'language': language });
}
function selectTag(tagId) {
    desselectButtons();
    button = $(`.menu .item[data-tag='${tagId}']`);
    button.addClass('active');
    if (tagId == 'null') {
        getSnippets(filter = { 'tags__isnull': true });
    } else {
        getSnippets(filter = { 'tags__id': tagId });
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
function getSnippetTagsHtml(snippetTags, snippetId) {
    
    html = '';
    dropdownHtml = `
        <div class="ui floating dropdown tiny icon button" id="tags-dropdown">
            <i class="tags icon"></i>
            <div class="menu">
                <div class="ui search icon input">
                    <i class="search icon"></i>
                    <input name="search" placeholder="Search issues..." type="text">
                </div>
                <div class="divider"></div>
                ${getTagsHtmlForDropdown(snippetTags.map(tag => tag.id))}
            </div>
        </div>
    `;
    for (tag of snippetTags) {
        html += `
            <div class="ui ${tag.color} label" data-tag-id="${tag.id}" style="margin-right: .5em;">
                ${tag.name}
                <i class="delete icon" onclick="untagSnippet(${tag.id}, ${snippetId})"></i>
            </div>
        `;
    }
    return `<div>
        ${html}
        ${dropdownHtml}
    </div>`;
}
function selectSnippet(snippetId) {
    sessionStorage.setItem('selectedSnippet', snippetId);
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
            ${getSnippetTagsHtml(snippet.tags, snippetId)}
        </div>
        <div class="ui attached segment" style="padding: 0; flex: 1 1 auto; overflow: auto; display: flex; flex-flow: column nowrap;">
            <div id="snippet-code" class="${sessionStorage.getItem('style')} snippet highlight">${snippet.html}</div>
        </div>
        <div class="ui bottom attached segment" style="display: flex; flex-flow: row nowrap; justify-content: space-between; align-items: baseline; padding: .5em; flex: 0 1 auto; margin-bottom: 0;">
            <div class="ui slider checkbox" id="public-checkbox" style="padding: 1em;">
                <input type="checkbox">
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
    $('#public-checkbox').checkbox({
        onChecked: () => {
            $.api({
                on: 'now',
                url: `/cd/api/snippets/${snippetId}/`,
                method: 'PATCH',
                data: { public: true },
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
    initializeTagsDropdown(snippetId);
}
function getTagsHtmlForDropdown(excludedTags = []) {
    let html = '';
    let allTags = JSON.parse(sessionStorage.getItem('tags'));
    tags = allTags.filter(tag => !excludedTags.includes(tag.id));
    for (tag of tags) {
        html += `
            <div class="tag item" data-value="${tag.id}">
                <i class="${tag.color} empty circle icon"></i>
                ${tag.name == '' ? 'No name' : tag.name}
            </div>
        `
    }
    return html
}
function initializeTagsDropdown(snippetId) {
    if ($('.tag.item').length == 0) {
        $('#tags-dropdown').remove();
        return;
    }
    $('#tags-dropdown').dropdown({
        action: 'hide',
        direction: 'downward',
        fullTextSearch: true,
        onChange: (value, text, $choice) => {
            tagSnippet(value, snippetId);
        }
    });
}
async function getSnippets(filter = undefined, callback = undefined, args = []) {
    $('#snippet').empty();
    let url = '/cd/api/snippets/';
    if (filter) {
        url += '?' + $.param(filter);
    }
    $.api({
        on: 'now',
        url: url,
        stateContext: '.snippets',
        onSuccess: function (response) {
            snippets = response.results;
            sessionStorage.setItem('snippets', JSON.stringify(snippets));
            renderSnippets(snippets);
            if (!filter) { $('#count-all').text(snippets.length); }
            if (callback) { callback(...args); }
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
                headers: { '': csrftoken },
                stateContext: '.delete.button',
                onSuccess: r => {
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
function getSnippetTags() {
    let el = $('.tags.menu');
    $.api({
        on: 'now',
        url: '/cd/api/snippets/tags/',
        stateContext: '.tags.segment',
        onSuccess: r => {
            renderSnippetTags(r);
        }
    })
}
function renderSnippetTags(tags) {
    let el = $('.tags.menu');
    el.empty();
    if (tags.length > 0) {
        tags.forEach(tag => {
            el.append(
                `
                <a class="item" data-tag="${tag.id}" onclick="selectTag('${tag.id}')" style="padding-right: 0; padding-left: 0;">
                    <span>    
                        <i class="empty ${tag.color} circle icon"></i>
                        ${tag.id === null ? 'No tag' : tag.name === '' ? 'No name' : tag.name}
                    </span>    
                    <div class="ui label">${tag.count}</div>
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
    $('#snippet-modal')
        .modal({
            onApprove: () => {
                $.api({
                    on: 'now',
                    url: url,
                    method: method,
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
        title: 'Snippet copied!',
        position: 'bottom right',
        class: 'black',
        showIcon: 'copy',
        showProgress: 'bottom'
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
function tagSnippet(tagId, snippetId) {
    $.api({
        on: 'now',
        method: 'POST',
        url: `/cd/api/snippets/${snippetId}/tag/`,
        data: { tag: tagId },
        successTest: r => true,
        onSuccess: r => {
            getSnippets(undefined, selectSnippet, [snippetId]);
            getSnippetTags();
            $('body').toast({
                title: 'Tagging',
                message: 'Snippet tagged successfully.',
            })
        }
    })
}
function untagSnippet(tagId, snippetId) {
    $.api({
        on: 'now',
        method: 'POST',
        url: `/cd/api/snippets/${snippetId}/untag/`,
        data: { tag: tagId },
        successTest: r => true,
        onSuccess: r => {
            getSnippets(undefined, selectSnippet, [snippetId]);
            getSnippetTags();
            $('body').toast({
                title: 'Untagging',
                message: 'Snippet untagged successfully.',
            })
        }
    })
}
function refreshSnippet(snippetId = undefined) {
    if (!snippetId) { 
        sessionStorage.getItem('selectedSnippet') ? snippetId = sessionStorage.getItem('selectedSnippet') : snippetId = undefined;
    }
    if (snippetId) { 
        getSnippets(undefined, selectSnippet, [snippetId]);
    }
}
function manageTags() {
    getTags(render = true);
    $('#tags-modal')
        .modal('show');
}
async function getTags(render = false) {
    $.api({
        on: 'now',
        url: '/cd/api/tags/',
        stateContext: '#tags-modal .form.content',
        autofocus: false,
        onSuccess: r => {
            if (render) { renderTags(r.results) };
            sessionStorage.setItem('tags', JSON.stringify(r.results));
        }
    })
}
var tagUpdateTimeout;
async function renderTags(tags) {
    let el = $('#tags-modal .form.content');
    el.empty();
    for (tag of tags) {
        el.append(`
            <div class="two fields">
                <div class="field">
                    <label>Color</label>
                    <div class="ui selection tag-color dropdown" data-tag-id=${tag.id}>
                        <i class="dropdown icon"></i>
                        <div class="default text">Color</div>
                    </div>
                </div>
                <div class="field">
                    <label>Name</label>
                    <input class="tag-name" type="text" value="${tag.name}" data-tag-id=${tag.id}>
                </div>
                <div class="ui red icon button" style="margin: 1.5em .5em 0 .5em;" onclick="deleteTag(${tag.id})"><i class="delete icon"></i></div>
            </div>
        `)
        $(`.tag-color.dropdown[data-tag-id=${tag.id}]`).dropdown({
            values: COLORS,
            showOnFocus: false,
            onChange: (value, text, choice) => {
                tagId = choice.closest('.ui.dropdown').attr('data-tag-id');
                updateTag(tagId, { color: value })
            },
        }).dropdown('set selected', tag.color, null, true);
    }
    $(`.tag-name`).on('input', e => {
        clearTimeout(tagUpdateTimeout);
        tagUpdateTimeout = setTimeout(function () {
            tagId = $(e.target).attr('data-tag-id');
            updateTag(tagId, { name: $(e.target).val() });
        }, 1000);
    });
    el.append(`
        <div class="ui green icon labeled button" onclick="addTag()">Add tag<i class="add icon"></i></div>
    `)
}
function updateTag(tagId, data) {
    $.api({
        on: 'now',
        method: 'PATCH',
        url: `/cd/api/tags/${tagId}/`,
        data: data,
        onSuccess: r => {
            getTags(render = false);
            getSnippetTags();
            refreshSnippet();
            $('body').toast({
                title: 'Tag updated',
                message: 'Tag updated successfully.'
            })
        }
    })
}
function addTag() {
    $.api({
        on: 'now',
        method: 'POST',
        url: `/cd/api/tags/`,
        onSuccess: r => {
            getTags(render = true);
            getSnippetTags();
            refreshSnippet();
            $('body').toast({
                title: 'Tag updated',
                message: 'Tag updated successfully.'
            })
        }
    })
}
function deleteTag(tagId) {
    $.api({
        on: 'now',
        method: 'DELETE',
        url: `/cd/api/tags/${tagId}/`,
        onSuccess: r => {
            getTags(render = true);
            getSnippetTags();
            refreshSnippet();
            $('body').toast({
                title: 'Tag deleted',
                message: 'Tag deleted successfully.'
            })
        }
    })
}
function initializeStylesDropdown() {
    $('#code-style-dropdown').dropdown({
        values: STYLES,
        showOnFocus: false,
        onChange: (value, text, choice) => {
            $('#demo').removeClass().addClass(value);
        },
    })
}
function initializeLineNumbersCheckbox() {
    $('#lineno-checkbox').checkbox();
}
function readConfig() {
    $.api({
        on: 'now',
        method: 'GET',
        url: '/cd/api/config/',
        onSuccess: r => {
            $('#lineno-checkbox').checkbox(r.linenos ? 'check' : 'uncheck');
            $('#code-style-dropdown').dropdown('set selected', r.style);
        }
    })
}
function showConfigModal() {
    readConfig();
    $('#config-modal')
        .modal({
            onApprove: () => {
                lineno = $('#lineno-checkbox').checkbox('is checked');
                style = $('#code-style-dropdown').dropdown('get value');
                $.api({
                    on: 'now',
                    method: 'PATCH',
                    url: '/cd/api/config/',
                    data: { lineno: lineno, style: style },
                    onSuccess: r => {
                        setSnippetStyle();
                        refreshSnippet();
                        $('body').toast({
                            title: 'Config updated',
                            message: 'Config updated successfully.'
                        })
                    }
                })
            }
        })
        .modal('show');
}
async function setSnippetStyle() {
    $.api({
        on: 'now',
        method: 'GET',
        url: '/cd/api/config/',
        onSuccess: r => {
            $('#snippet-code').addClass(r.style);
            sessionStorage.setItem('style', r.style);
        }
    })
}