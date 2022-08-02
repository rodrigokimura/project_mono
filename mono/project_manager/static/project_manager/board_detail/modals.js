function showCardModal(card = null, bucketId) {
    let create = card === null
    let dark = getDarkMode()
    hideManageTagsModal()
    const modal = $('.ui.card-form.modal')
    modal.off().form('reset')
    modal.find('.card-files').val('')
    modal.find('.files-container').empty()

    if (card) { populateModal(modal, card) }

    modal.modal({
        restoreFocus: false,
        autofocus: true,
        transition: 'scale',
        duration: 400,
        allowMultiple: true,
        blurring: true,
        onShow() {
            cardEdited = false
            modal.find('.scrolling.content').animate({ scrollTop: 0 })
            modal.find('.ui.card-due-date.calendar').calendar({
                type: 'date',
                today: true,
                formatInput: true,
                formatter: {
                    date: (date, settings) => {
                        if (!date) return ''
                        return date.toLocaleDateString(LANGUAGE_CODE)
                    }
                }
            })
            if (card !== null) {
                if (card.id != getActiveCard()?.card) {
                    $('#card-tab-menu .item').tab('change tab', 'details')
                }
                setActiveCard(card.id, bucketId)
            } else { $('#card-tab-menu .item').tab('change tab', 'details') }
        },
        onHidden() {
            if (cardEdited) { getCards(bucketId) }
            $('.checklist-drake').empty()
            clearModal(modal)
        },
        onApprove() {
            modal.form('validate form')
            if (!modal.form('is valid')) {
                return false
            }
            var data = {
                name: modal.find('input[name=name]').val(),
                description: modal.find('textarea[name=description]').val(),
                bucket: bucketId,
            }
            if (FEATURES.status) {
                data['status'] = modal.find('.ui.status.dropdown')?.dropdown('get value')
            }
            if (FEATURES.color) {
                data['color'] = modal.find('.ui.card-color.dropdown')?.dropdown('get value')
            }
            if (FEATURES.tags) {
                tagsString = modal.find('.ui.tags.dropdown')?.dropdown('get value')
                tags = tagsString.split(",").map(tag => ({ name: tag }))
                data['tag'] = JSON.stringify(tags)
            }
            if (FEATURES.assignees) {
                assigneesString = modal.find('.ui.assigned_to.dropdown')?.dropdown('get value')
                assignees = assigneesString?.split(",").map(username => ({ username: username }))
                data['assigned_to'] = JSON.stringify(assignees)
            }
            if (FEATURES.dueDate) {
                dueDate = modal.find('.ui.card-due-date.calendar')?.calendar('get date') // If not null, dueDate is a Date object
                if (dueDate !== null) { data['due_date'] = dueDate.toISOString().split("T")[0] } // Convert to string in correct format
            }
            if (create) {
                method = 'POST'
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/`
                data['order'] = 0
            } else {
                method = 'PUT'
                id = modal.find('input[name=id]').val()
                data['order'] = $(`.card-el[data-card-id=${card.id}]`).index() + 1
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${id}/`
            }

            $.api({
                on: 'now',
                url: url,
                method: method,
                data: data,
                onSuccess(r) {
                    if (FEATURES.files) {
                        var files = modal.find('.card-files')[0]?.files
                        if (files.length > 0) {
                            var cardId = create ? r.id : card.id
                            for (f of files) {
                                var fd = new FormData()
                                fd.append('file', f)
                                attachFile(fd, bucketId, cardId)
                            }
                        }
                    }
                    getCards(bucketId)
                }
            })
        }
    }).modal('show')

    initializeTagsDropdown(modal.find('.ui.tags.dropdown'), card)
    initializeUsersDropdown(modal.find('.ui.assigned_to.dropdown'), card)

    modal.submit(e => {
        e.preventDefault()
        modal.find('.positive.button').click()
    })

    modal.find('.manage-tags').off().on('click', e => {
        selectedTags = modal.find('.ui.tags.dropdown').dropdown('get value').split(',')
        showManageTagsModal(
            false,
            true,
            () => {
                initializeTagsDropdown(modal.find('.ui.tags.dropdown'))
                modal.find('.ui.tags.dropdown').dropdown('set exactly', selectedTags)
            },
        )
    })

    if (!create) {
        if (FEATURES.files) {
            getFiles(modal, bucketId, card.id)
        }
        if (FEATURES.comments) {
            modal.find('#suggest-comment').val('')
            initializeSuggest()
            loadComments(card, bucketId)
        }
        if (FEATURES.checklist) {
            loadChecklistItems(card, bucketId)
        }
    }
}

async function showManageTagsModal(allowMultiple = false, fromCardModal = false, callback = undefined) {
    $('.ui.sidebar').sidebar('hide')
    let dark = getDarkMode()
    let tagsModal = $('.ui.tags.modal')
    if (dark) {
        tagsModal.find('.ui.basic.segment').addClass('inverted')
    } else {
        tagsModal.find('.ui.basic.segment').removeClass('inverted')
    }
    tagsModal.modal({
        autofocus: false,
        allowMultiple: allowMultiple,
        inverted: false,
        closable: true,
        blurring: true,
        context: fromCardModal ? '.card-form' : 'body',
        onHidden() {
            if (callback) { callback() }
        },
        onShow() {
            let el = tagsModal.find('.content')
            tagsModal.find('.close.button').off().click(hideManageTagsModal)
            tagsModal.find('.save.button').off().click(
                () => {
                    saveTagsOnManageTagsModal(tagsModal, callback)
                }
            )
            el.empty()
            el.append(`
                <div class="ui new-tag icon labeled green button" style="margin-bottom: 1em;">
                    <i class="add icon"></i>
                    ${gettext('Add new tag')}
                </div>
            `)
            el.find('.new-tag').off().click(() => {
                addNewTagInput(el)
            })
            var tags = getTags()
            for (tag of tags) {
                renderTagForms(el, tag)
            }
        },
    })
    tagsModal.modal('show')
}

async function showBucketModal(bucket = null) {
    var create
    const modal = $('.ui.bucket-form.modal')
    modal.form('reset')
    modal.off()
    if (bucket != null) {
        create = false
        modal.find('input[name=id]').val(bucket.id)
        modal.find('input[name=name]').val(bucket.name)
        modal.find('textarea[name=description]').val(bucket.description)
        modal.find('.ui.auto-status.dropdown').dropdown('set selected', bucket.auto_status)
        modal.find('.ui.color.dropdown').dropdown('set selected', bucket.color !== null ? bucket.color.id : '')
    } else {
        create = true
        modal.find('input[name=id]').val('')
        modal.find('input[name=name]').val('')
        modal.find('textarea[name=description]').val('')
        modal.find('.ui.auto-status.dropdown').dropdown('set selected', 'N')
        modal.find('.ui.color.dropdown').dropdown('clear')
    }
    modal.modal({
        restoreFocus: false,
        autofocus: false,
        transition: 'scale',
        duration: 400,
        onApprove(el) {
            modal.form('validate form')
            if (!modal.form('is valid')) {
                return false
            }
            name = modal.find('input[name=name]').val()
            description = modal.find('textarea[name=description]').val()
            autoStatus = modal.find('.ui.auto-status.dropdown').dropdown('get value')
            color = modal.find('.ui.color.dropdown').dropdown('get value')
            if (create === true) {
                method = 'POST'
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/`
                order = 0
            } else {
                id = modal.find('input[name=id]').val()
                order = $(`.bucket-el[data-bucket-id=${bucket.id}]`).index() + 1
                method = 'PUT'
                url = `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${id}/`
            }
            $.api({
                on: 'now',
                method: method,
                url: url,
                data: {
                    name: name,
                    board: BOARD_ID,
                    description: description,
                    auto_status: autoStatus,
                    color: color,
                    order: order,
                },
                onSuccess(r) {
                    loadBoard()
                }
            })
        }
    })
    modal.submit(e => {
        e.preventDefault()
        modal.find('.positive.button').click()
    })
    modal.modal('show')
}

async function showTimeEntriesModal(cardId, bucketId) {
    const modal = $('#time-entries.modal')
    modal.modal({
        autofocus: false,
        onShow() {
            modal.addClass('loading')
            getTimeEntries(bucketId, cardId)
        },
        onVisible() {
            modal.removeClass('loading')
        },
        onHidden() {
            getCards(bucketId)
            modal.find('.content').empty()
        },
    }).modal('show')
}

async function showDeleteFileModal(bucketId, cardId, fileId) {
    dark = getDarkMode()
    $('body').modal({
        title: gettext('Confirmation'),
        class: `mini ${dark ? 'inverted' : ''}`,
        closeIcon: true,
        content: gettext('Delete this file?'),
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
                url: `/pm/api/projects/${PROJECT_ID}/boards/${BOARD_ID}/buckets/${bucketId}/cards/${cardId}/files/${fileId}/`,
                stateContext: $(`.ui.special.card.img-card-file[data-file-id=${id}]`),
                successTest: r => r != 0,
                onSuccess(r) {
                    $(`.ui.special.card.img-card-file[data-file-id=${fileId}]`).remove()
                    cardEdited = true
                },
            })
        }
    }).modal('show')
}
