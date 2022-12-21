function init() {
    retrieveLessons()
}

function retrieveLessons() {
    $.api({
        on: 'now',
        method: 'GET',
        url: `/tp/api/lessons/`,
        stateContext: '#grid',
        onSuccess(response) {
            $('#page-content').empty()
            $('#new-lesson-btn-row').remove()
            if (response.count > 0) {
                renderLessons(response.results)
                $('#page-content').parent().parent().append(`
                    <div class="row" id="new-lesson-btn-row">
                        <div class="column">
                            <div class="ui green button" onclick="showLessonModal()">${gettext('New lesson')}</div>
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
                ${gettext("No lessons yet.")}
            </div>
            <div class="ui icon labeled animated large green button" onclick="showLessonModal()">
                <div class="visible content">${gettext("Add your first lesson!")}</div>
                <div class="hidden content"><i class="plus icon"></i></div>
            </div>
        </div>
    `)
}

function renderLessons(lessons) {
    const pageContent = $('#page-content')
    pageContent.empty()
    pageContent.append(`
        <div class="ui message">
            ${interpolate(ngettext('You have only %s lesson.', 'You have %s lessons.', lessons.length), [lessons.length])}
        </div>
        <div class="ui three stackable cards" style="margin-top: .5em; padding-top: 0;" id="lessons"></div>
    `)
    pageContent.ready(e => {
        let lessonsEl = $('#lessons')
        lessonsEl.empty()
        lessons.forEach(renderLesson)
        lessonsEl.ready(e => {
            initializeCardMenuDropdown()
            initializeDeleteBoardButtons()
        })
    })
}

function renderLesson(lesson) {
    const lessonsEl = $('#lessons')
    const details = getDetails(lesson.text)
    let textSample = lesson.text.split('\n').slice(0, 3).join('\n')
    if (lesson.text.split('\n').length > 3) {
        textSample = textSample.trim() + ' …'
    }
    lessonsEl.append(`
        <div class="ui card" data-lesson-id="${lesson.id}">
            <div class="center aligned handle content" style="flex: 0 0 auto; display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move;">
                <i class="grip lines icon"></i>
            </div>
            <div class="content" style="padding-bottom: 0;">
                <div class="header" style="display: flex; flex-flow: row nowrap; justify-content: space-between;">
                    <div class="" style="flex: 0 1 auto; overflow-wrap: anywhere; padding-right: .5em;">
                        <a class="lesson-link" href="/tp/${lesson.id}/">${lesson.name}</a>
                    </div>
                    <div class="ui basic icon top right pointing card-menu dropdown button" style="flex: 0 0 auto; align-self: flex-start;">
                        <i class="ellipsis horizontal icon"></i>
                        <div class="menu">
                            <a class="item" href="/mm/${lesson.id}/"><i class="eye icon"></i>${gettext("Open")}</a>
                            <div class="item" onclick="showLessonModal('${lesson.id}')"><i class="edit icon"></i>${gettext("Edit")}</div>
                            <div class="divider"></div>
                            <a class="delete-board item" data-lesson-id="${lesson.id}"><i class="delete icon"></i>${gettext("Delete")}</a>
                        </div>
                    </div>
                </div>
                <div class="meta">
                    <p>${interpolate(gettext("Created at %s"), [stringToLocalDatetime(lesson.created_at, languageCode)])}</p>
                </div>
            </div>
            <div class="extra content">
                <div class="ui message text-sample" title="${lesson.text}">
                    <pre>${textSample}</pre>
                </div>
                <div class="ui bulleted list">
                    <div class="item">${details.lineCount} lines</div>
                    <div class="item">${details.wordCount} words</div>
                    <div class="item">${details.charCount} chars</div>
                    <div class="item">${details.distinctCharCount} unique chars</div>
                    <div class="item">${details.distinctFingers} unique fingers</div>
                </div>
            </div>
            <div class="extra content keyboard-heatmap" data-lesson-id="${lesson.id}"></div>
        </div>
    `)
    new StaggeredLayout(`.keyboard-heatmap[data-lesson-id="${lesson.id}"]`).render()
    renderHeatmap(lesson.text, lesson.id)
}

function getDetails(text) {
    text = text.replace(/\r/g, "")  // remove carriage returns

    const lineCount = text.split('\n').length
    const wordCount = text.split(' ').length
    const charCount = text.length
    const uniqueChars = [...new Set(text)]
    const handPosition = new HandPosition('qaz', 'wsx', 'edc', 'rfvtgb', ' ', ' ', 'yhnujm', 'ik,', 'ol.', 'çp;\n')

    fingers = text.split('').map(char => handPosition.getFinger(char))

    return {
        lineCount: lineCount,
        wordCount: wordCount,
        charCount: charCount,
        distinctCharCount: uniqueChars.length,
        distinctFingers: [...new Set(fingers)].length
    }
}

function renderHeatmap(text, lessonId, ignoreBlank = true) {
    text = text.replace(/\r/g, "")

    if (ignoreBlank) {
        text = text.replace(/\s/g, "")
    }

    const chars = text.split('')

    let charCount = {}
    chars.forEach(char => {
        if (charCount[char] === undefined) {
            charCount[char] = 1
        } else {
            charCount[char]++
        }
    })

    const maxCount = Math.max(...Object.values(charCount))
    for (const char in charCount) {
        const keyElement = $(`.keyboard-heatmap[data-lesson-id="${lessonId}"] .kb-key[data-key="${char}"]`)
        const percent = charCount[char] / maxCount
        keyElement.css('background-color', `rgba(65, 131, 196, ${percent})`)
        keyElement.attr('title', interpolate(ngettext('%s key press', '%s key presses', charCount[char]), [charCount[char]]))
        keyElement.popup()
        if (percent > 0.5) {
            keyElement.css('color', 'white')
        }
    }
}

function showLessonModal(lessonId = null) {
    const MODAL = $('#lesson-modal')
    let method, url
    if (!lessonId) {
        method = 'POST'
        url = '/mm/api/lessons/'
        MODAL.find('input[name="name"]').val('')
    } else {
        method = 'PATCH'
        url = `/mm/api/lessons/${lessonId}/`
        let lessonName = $(`.ui.card[data-lesson-id='${lessonId}'] .lesson-link`).text()
        MODAL.find('input[name="name"]').val(lessonName)
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
                    retrieveLessons()
                },
            })
        },
    }).modal('show')
}

function getFinger() {

    return fingers
}

function initializeDeleteBoardButtons() {
    $('.delete-board').click(e => {
        let lessonId = $(e.target).attr('data-lesson-id');
        $('body').modal({
            title: gettext('Confirm deletion'),
            class: 'mini',
            closeIcon: true,
            content: gettext('Delete this lesson?'),
            actions: [
                { text: 'Cancel', class: 'secondary' },
                { text: 'Delete', class: 'red approve' },
            ],
            onApprove: () => {
                $.api({
                    on: 'now',
                    method: 'DELETE',
                    url: `/tp/api/lessons/${lessonId}/`,
                    onSuccess(r) { retrieveLessons() },
                    onFailure: (response, element, xhr) => {
                        $('body').toast({
                            class: 'error',
                            message: response.detail,
                        }).toast('show')
                    },
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
