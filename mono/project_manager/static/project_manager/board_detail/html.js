function getBucketHTML(bucket, dark, compact, width) {
    return `
        <div class="ui ${dark ? 'inverted ' : ' '}card bucket-el" data-bucket-id="${bucket.id}" data-bucket-updated-at="${bucket.updated_at}" style="width: ${width}px; flex: 0 0 auto; display: flex; flex-flow: column nowrap; overflow-y: visible; scroll-snap-align: start;${compact ? ' margin-right: .25em; margin-top: .5em; margin-bottom: .5em;' : ''}">
            <div class="center aligned handle content" style="flex: 0 0 auto; display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move; ${bucket.color !== null ? `background-color: ${dark ? bucket.color.dark : bucket.color.primary}; color: ${bucket.color.light}` : ''}; " data-bucket-id="${bucket.id}">
                <i class="grip lines icon"></i>
            </div>
            <div class="content" style="flex: 0 1 auto; ${bucket.color !== null ? `background-color: ${dark ? bucket.color.dark : bucket.color.light};` : ''};${compact ? ' padding: .5em;' : ''}">
                <div class="header" style="display: flex; flex-flow: row nowrap; justify-content: space-between;">
                    <div style="flex: 1 1 auto; overflow-wrap: anywhere; padding-right: .5em; ${bucket.color !== null ? `color: ${dark ? bucket.color.light : bucket.color.dark};` : ''}">
                        ${bucket.name}
                    </div>
                    <div style="flex: 0 0 auto;">
                        ${bucket.auto_status !== 'N' ? '<span class="ui small text" style="margin-right: .5em; opacity: .6;"><i class="robot icon"></i></span><br>' : ''}
                    </div>
                    <div class="ui basic icon top right pointing dropdown ${dark ? 'inverted ' : ' '}button" data-bucket-id="${bucket.id}" style="flex: 0 0 auto; align-self: flex-start;${compact ? ' height: 2em; padding: .5em; margin: 0;' : ''}">
                        <i class="ellipsis horizontal icon"></i>
                        <div class="menu">
                            <div class="add card item" data-bucket-id="${bucket.id}"><i class="add icon"></i>${gettext('Add new card')}</div>
                            <div class="divider"></div>
                            <div class="edit bucket item" data-bucket-id="${bucket.id}"><i class="edit icon"></i>${gettext('Edit this bucket')}</div>
                            <div class="delete bucket item" data-bucket-id="${bucket.id}"><i class="delete icon"></i>${gettext('Delete this bucket')}</div>
                        </div>
                    </div>
                </div>
                <div class="meta">
                    <span style="white-space: pre-line;">${bucket.description ? bucket.description : ''}</span>
                </div>
            </div>
            <div class="extra content cards-drake" id="bucket-${bucket.id}" style="flex: 1 1 auto; display: flex; flex-flow: column nowrap; align-items: stretch; overflow-y: auto;${compact ? ' padding: .5em;' : ''}">
            </div>
        </div>
    `
}

function getAddBucketButtonHTML(dark) {
    return `<div class="ui add bucket basic ${dark ? 'inverted ' : ' '}button" style="flex: 0 0 auto">${gettext('Add new bucket')}</div>`
}

function getCardHTML(card, dark, compact, overdue) {
    return `
        <div class="ui loading ${dark ? 'inverted ' : ' '}${card.is_running ? 'red ' : ''}${card.status === 'C' ? 'completed ' : ''}${overdue ? 'overdue ' : ''}card card-el" data-card-id="${card.id}" style="width: 100%; flex: 0 0 auto;${compact ? ' margin-bottom: -.25em;' : 'margin-bottom: .25em;'}">
            <div class="center aligned handle content" style="flex: 0 0 auto; display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move; ${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.primary}; color: ${card.color.light}` : ''};" data-card-id="${card.id}">
                <i class="grip lines small icon"></i>
            </div>
            <div class="content" style="${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.light};` : ''};${compact ? ' padding: .5em;' : ''}">
                <div class="header" style="display: flex; flex-flow: row nowrap; justify-content: space-between; ${card.color !== null ? `color: ${dark ? card.color.light : card.color.dark};` : ''}">
                    <div class="" style="flex: 0 1 auto; overflow-wrap: anywhere; padding-right: .5em;">
                        <i class="card-status ${dark ? 'dark ' : ' '}${status_icon} icon" data-status="${card.status}" data-card-id="${card.id}"></i>
                        <span class="${dark ? 'dark ' : ' '}card-name" data-card-id="${card.id}" style="${card.color !== null ? `color: ${dark ? card.color.light : card.color.dark};` : ''}">${card.name}</span>
                    </div>
                    <div class="ui basic icon top right pointing ${dark ? 'inverted ' : ' '}dropdown button" data-card-id="${card.id}" style="flex: 0 0 auto; align-self: flex-start;${compact ? ' height: 1.5em; padding: .25em; margin: 0;' : ''}">
                        <i class="ellipsis horizontal icon"></i>
                        <div class="menu">
                            <div class="edit card item" data-card-id="${card.id}"><i class="edit icon"></i>${gettext('Edit this card')}</div>
                            <div class="delete card item" data-card-id="${card.id}"><i class="delete icon"></i>${gettext('Delete this card')}</div>
                            ${FEATURES.time_entries ? `<div class="divider"></div>
                            <div class="start-stop-timer card item" data-card-id="${card.id}"><i class="stopwatch icon"></i>${gettext('Start/stop timer')}</div>
                            <div class="edit-time-entries card item" data-card-id="${card.id}"><i class="history icon"></i>${gettext('Edit time entries')}</div>` : ''}
                        </div>
                    </div>
                </div>
                <div class="meta" style="display: flex; flex-flow: column nowrap;">
                    <div class="tags" style="flex: 0 0 auto; padding-top: .5em;" data-card-id="${card.id}"></div>
                    <div class="description" style="white-space: pre-line;">${card.description ? card.description : ''}</div>
                    <div class="assignees" style="flex: 0 0 auto; padding-top: .5em;" data-card-id="${card.id}"></div>
                </div>
            </div>
            <div data-card-id="${card.id}" class="extra content" style="${card.color !== null ? `background-color: ${dark ? card.color.dark : card.color.light};` : ''};;${compact ? ' padding: .5em;' : ''}">
            </div>
            <div data-card-id="${card.id}" class="ui bottom attached progress" data-percent="${card.checked_items > 0 ? card.checked_items / card.total_items * 100 : 0}">
                <div class="bar"></div>
            </div>
        </div>
    `
}

function getTimeEntryCardletHTML(card) {
    return `
        <span class="ui right floated ${card.is_running ? 'red ' : ''} text" style="font-size: 85%;">
            <a class="start-stop-timer cardlet" data-card-id="${card.id}" data-content="${card.is_running ? gettext('Stop timer') : gettext('Start timer')}" data-variation="tiny basic">
                ${card.is_running ? '<i class="stop circle icon"></i>' : '<i class="play circle icon"></i>'}
            </a>
            <span class="total-time noselect cardlet" data-card-id="${card.id}" data-time="${card.total_time}" data-start="${new Date()}" data-content="${gettext('Total tracked time.')}" data-variation="tiny basic">
                ${str(card.total_time)}
            </span>
        </span>
    `
}

function getCommentCardletHTML(card) {
    return `
        <span class="ui left floated text noselect cardlet" style="font-size: 85%; margin-right: .5em;" data-title="${gettext('Comments')}" data-content="${card.comments}" data-variation="tiny basic">
            <i class="comment icon"></i>${card.comments}
        </span>
    `
}

function getFileCardletHTML(card) {
    return `
        <span class="ui left floated text noselect cardlet" style="font-size: 85%; margin-right: .5em;" data-title="${gettext('Attached files')}" data-content="${card.total_files}" data-variation="tiny basic">
            <i class="paperclip icon"></i>${card.total_files}
        </span>
    `
}

function getChecklistCardletHTML(card) {
    return `
        <span class="ui left floated text noselect cardlet" style="font-size: 85%; margin-right: .5em;" data-title="${gettext('Checklist items')}" data-content="${interpolate(ngettext('%s checked, %s in total.', '%s checked, %s in total.', card.checked_items), [card.checked_items, card.total_items])}" data-variation="tiny basic">
            <i class="tasks icon"></i>${card.checked_items}/${card.total_items}
        </span>
    `
}

function getDueDateCardletHTML(overdue, dueDate) {
    return `
        <span class="ui left floated${overdue ? ' red' : ''} text noselect cardlet" style="font-size: 85%; margin-right: .5em;" data-title="Due date" data-content="${dueDate.toLocaleDateString(LANGUAGE_CODE)}${overdue ? gettext(' - This card is overdue!') : ''}" data-variation="tiny red basic"><i class="calendar day icon"></i></span>
    `
}

function getTagHTML(tag) {
    if (tag.icon !== null) {
        return `
            <span class="ui mini ${tag.color ? tag.color.name.toLowerCase() : ''} label"><i class="${tag.icon.markup} icon"></i> ${tag.name}</span>
        `
    }
    return `
        <span class="ui mini ${tag.color ? tag.color.name.toLowerCase() : ''} label">${tag.name}</span>
    `
}

function getAssigneeHTML(borderColor, user, dark) {
    if (borderColor === null) {
        return `<img data-username="${user.username}" data-content="${user.username}" data-variation="basic" class="ui avatar mini image assignee${dark ? ' dark' : ''}" src="${user.profile.avatar === null ? PLACEHOLDER_AVATAR : user.profile.avatar}"">`
    }
    return `<img data-username="${user.username}" data-content="${user.username}" data-variation="basic" class="ui avatar mini image assignee${dark ? ' dark' : ''}" src="${user.profile.avatar === null ? PLACEHOLDER_AVATAR : user.profile.avatar}" style="border-color: ${borderColor}">`
}

function getFileHTML(file) {
    return `
        <div class="ui special card img-card-file" data-file-id=${file.id}>
            <div class="blurring dimmable image" data-file-id=${file.id}>
                <div class="ui dimmer">
                    <div class="content">
                        <div class="center">
                            <a href="${file.file}" target="_blank" class="ui inverted button">${gettext('Open')}</a>
                        </div>
                        <div class="center" style="margin-top: 1em;">
                            <a class="delete-file" data-file-id=${file.id}><i class="trash icon"></i>${gettext('Remove')}</a>
                        </div>
                    </div>
                </div>
                <img src="${file.image ? file.file : generateAvatar(file.extension)}" class="img-card-file">
            </div>
        </div>
    `
}

function getChecklistItemHTML(item, dark) {
    return `
        <div class="checklist-item" data-item-id="${item.id}" style="display: flex; flex-flow: row nowrap; align-items: center;">
            <div class="ui ${dark ? 'inverted ' : ' '}fitted checkbox" style="flex: 0 0 auto;" data-item-id="${item.id}">
                <input type="checkbox" ${item.checked ? 'checked' : ''}>
                <label></label>
            </div>
            <div class="ui ${dark ? 'inverted ' : ' '} input" style="flex: 1 0 auto;">
                <input class="${item.checked ? 'item-checked' : ''}" data-item-id="${item.id}" type="text" placeholder="${gettext('Enter text here')}" data-text="${item.name}" value="${item.name}">
            </div>
            <div data-item-id="${item.id}" class="ui mini icon basic delete-item ${dark ? 'inverted ' : ' '}button"><i data-item-id="${item.id}" class="trash alternate outline icon"></i></div>
        </div>
    `
}

function getNoTimeEntryPlaceholderHTML() {
    return `
        <div class="ui header">
            ${gettext('No time entries for this card.')}
        </div>
    `
}

function getTimeEntryHTML(timeEntry, dark) {
    return `
        <div data-time-entry-id="${timeEntry.id}" class="ui form ${dark ? 'inverted' : ''} segment">
            <div class="field">
                <label>${gettext('Name')}</label>
                <input type="text" name="name" placeholder="${gettext('Name')}" value="${timeEntry.name}" data-time-entry-id="${timeEntry.id}">
            </div>
            <div class="two fields">
                <div class="field">
                    <label>${gettext('Started at')}</label>
                    <div class="ui time-entry start-date calendar" data-time-entry-id="${timeEntry.id}">
                        <div class="ui input left icon">
                            <i class="calendar icon"></i>
                            <input type="text" placeholder="${gettext('Date/Time')}">
                        </div>
                    </div>
                </div>
                <div class="field">
                    <label>${gettext('Stopped at')}</label>
                    <div class="ui time-entry stop-date calendar" data-time-entry-id="${timeEntry.id}">
                        <div class="ui input left icon">
                            <i class="calendar icon"></i>
                            <input type="text" placeholder="${gettext('Date/Time')}">
                        </div>
                    </div>
                </div>
            </div>
            <div style="height: 2.5em;">
                <div class="ui left floated red icon labeled delete button" data-time-entry-id="${timeEntry.id}">
                    <i class="delete icon"></i>
                    ${gettext('Delete')}
                </div>
                <div class="ui right floated icon labeled primary save button" data-time-entry-id="${timeEntry.id}">
                    <i class="save icon"></i>
                    ${gettext('Save')}
                </div>
            </div>
        </div>
    `
}

function getCommentHTML(comment, text, dark, isAuthor) {
    if (isAuthor) {
        return `
            <div class="${dark ? 'inverted' : ''} comment">
                <div class="avatar">
                    <img class="ui small image" src="${comment.created_by.profile.avatar != null ? comment.created_by.profile.avatar : PLACEHOLDER_AVATAR}">
                </div>
                <div class="content">
                    <span class="author">${comment.created_by.username}</span>
                    <div class="metadata">
                        <span class="date">${comment.created_at}</span>
                    </div>
                    <div class="text" style="white-space: pre-line;">${text}</div>
                    <div class="actions">
                        <a class="edit-comment" data-comment-id=${comment.id}>${gettext('Edit')}</a>
                        <a class="delete-comment" data-comment-id=${comment.id}>${gettext('Delete')}</a>
                    </div>
                </div>
            </div>
        `
    }
    return `
        <div class="right aligned comment" style="display: flex; flex-flow: row nowrap; align-items: start;">
            <div class="content" style="flex: 1 1 auto; margin-right: 1em;">
                <div class="metadata">
                    <span class="date">${comment.created_at}</span>
                </div>
                <span class="author" style="margin-left: .5em;">${comment.created_by.username}</span>
                <div class="text" style="white-space: pre-line;">${text}</div>
            </div>
            <div class=" avatar" style="flex: 0 0 auto;">
                <img class="ui small image" src="${comment.created_by.profile.avatar != null ? comment.created_by.profile.avatar : PLACEHOLDER_AVATAR}">
            </div>
        </div>
    `
}

function getTagFormHTML(tagId, dark) {
    return `<form class="ui unstackable ${dark ? 'inverted' : ''} form" data-tag-id="${tagId}" style="width: 100%; margin-bottom: .5em;">
        <div class="" style="display: flex; flex-flow: row nowrap;">
            <input type="hidden" name="id" value="${tagId}">
            <div style="flex: 0 0 auto; width: 6em; display: flex; margin-right: .5em;">
                <select class="ui tag-icon clearable compact two column mini ${dark ? 'inverted' : ''} dropdown" data-tag-id="${tagId}">
                </select>
            </div>
            <div style="flex: 0 0 auto; width: 6em; display: flex; margin-right: .5em;">
                <select class="ui tag-color clearable compact two column ${dark ? 'inverted' : ''} dropdown" data-tag-id="${tagId}">
                </select>
            </div>
            <div style="flex: 1 1 auto; margin-right: .5em;" class="ui ${dark ? 'inverted' : ''} input">
                <input class="tag-name" type="text" placeholder="${gettext('Name')}" data-tag-id="${tagId}">
            </div>
            <div style="">
                <div class="ui icon red button" data-tag-id="${tagId}"><i class="delete icon"></i></div>
                <div class="ui popup top right">
                    <h4 class="ui header">${gettext('Delete tag?')}</h4>
                    <div class="ui delete button" data-tag-id="${tagId}">${gettext('Yes')}</div>
                </div>
            </div>
        </div>
    </form>`
}

function getActivityHTML(activity, dark, drawVerticalLine) {
    return `<div class="ui ${dark ? 'inverted': ''} segment activity">
        ${activity.verbose_text}
    </div>
    ${drawVerticalLine ? `<div class="${dark ? 'dark': ''} vertical-line"></div>` : ''}`
}
