function toIsoString(date) {
    var tzo = -date.getTimezoneOffset(),
        dif = tzo >= 0 ? '+' : '-',
        pad = function (num) {
            return (num < 10 ? '0' : '') + num
        }
    return date.getFullYear() +
        '-' + pad(date.getMonth() + 1) +
        '-' + pad(date.getDate()) +
        'T' + pad(date.getHours()) +
        ':' + pad(date.getMinutes()) +
        ':' + pad(date.getSeconds())
}

function getObjectType() {
    if ($('#is-recurrent-or-installment').checkbox('is checked')) {
        if ($('.ui.radio.installment.checkbox').checkbox('is checked')) {
            type = "installment"
        }
        if ($('.ui.radio.recurrent.checkbox').checkbox('is checked')) {
            type = "recurrent"
        }
    } else {
        type = "transaction"
    }
    return type
}

function submitForm() {
    type = getObjectType()
    const amount = Number($('[name="amount"]').val().replace(',', '').replace('.', '')) / 100
    if (type == "transaction") {
        if (getTransactionType() == 'TRF') {
            url = '/fn/api/transferences/'
            payload = JSON.stringify({
                description: $('[name="description"]').val(),
                amount: amount,
                from_account: {
                    id: $('#from-accounts-dropdown').dropdown('get value'),
                },
                to_account: {
                    id: $('#to-accounts-dropdown').dropdown('get value'),
                },
                timestamp: toIsoString($('#timestamp').calendar('get date')),
            })
        } else {
            url = '/fn/api/transactions/'
            payload = JSON.stringify({
                amount: amount,
                description: $('[name="description"]').val(),
                account: {
                    id: $('#accounts-dropdown').dropdown('get value'),
                },
                category: {
                    id: $('#categories-dropdown').dropdown('get value'),
                },
                timestamp: toIsoString($('#timestamp').calendar('get date')),
            })
        }
    } else if (type == "recurrent") {
        url = '/fn/api/recurrent-transactions/'
        payload = JSON.stringify({
            amount: amount,
            description: $('[name="description"]').val(),
            account: {
                id: $('#accounts-dropdown').dropdown('get value'),
            },
            category: {
                id: $('#categories-dropdown').dropdown('get value'),
            },
            timestamp: toIsoString($('#timestamp').calendar('get date')),
            frequency: $('#frequency-dropdown').dropdown('get value'),
        })
    } else if (type == "installment") {
        url = '/fn/api/installments/'
        payload = JSON.stringify({
            total_amount: amount,
            description: $('[name="description"]').val(),
            account: {
                id: $('#accounts-dropdown').dropdown('get value'),
            },
            category: {
                id: $('#categories-dropdown').dropdown('get value'),
            },
            timestamp: toIsoString($('#timestamp').calendar('get date')),
            months: $('[name="months"]').val(),
            handle_remainder: $('#remainder-dropdown').dropdown('get value'),
        })
    }
    $('.ui.transaction.form .field').removeClass('error')
    $('.pointing.label').hide()
    $.api({
        on: 'now',
        url: url,
        method: 'POST',
        contentType: 'application/json',
        data: payload,
        successTest(r) { return true },
        onSuccess(r) {
            $('.ui.transaction.modal').modal('hide')
            location.reload()
        },
        onError(errorMessage, element, xhr) {
            if (xhr.status == 400) {
                for (p in xhr.responseJSON) {
                    if (p == 'non_field_errors') {
                        $('.ui.transaction.form').form(
                            'add errors',
                            errors
                        )
                    } else {
                        if (p == "total_amount") {
                            xhr.responseJSON["amount"] = xhr.responseJSON["total_amount"]
                            p = "amount"
                        }
                        if ('id' in xhr.responseJSON[p]) {
                            prompt = xhr.responseJSON[p]['id'].toString()
                        } else {
                            prompt = xhr.responseJSON[p].toString()
                        }
                        $('.ui.transaction.form').form('add prompt', p)
                        $(`.pointing.label[data-name=${p}]`).empty().text(prompt).fadeIn()
                    }
                }
            }
        },
    })
}

function clearForm() {
    $('#recurrent-or-installment').hide('swing')
    $('#is-recurrent-or-installment').checkbox('uncheck')
    $('.ui.transaction.form').form('clear')
    $('.pointing.label').hide()
    $('.ui.radio.recurrent.checkbox').checkbox('check')
    $('#transaction-type .item[data-value=EXP]').click()
}

function resetForm() {
    ts = $('#timestamp').calendar('get date')
    $('#recurrent-or-installment').hide('swing')
    $('#is-recurrent-or-installment').checkbox('uncheck')
    $('.ui.transaction.form').form('clear')
    $('.pointing.label').hide()
    $('.ui.radio.recurrent.checkbox').checkbox('check')
    $('#timestamp').calendar('set date', ts)
}

function showTransactionModal() {
    $('.ui.transaction.modal')
        .modal({
            onShow: () => {
                clearForm()
                $('#timestamp').calendar({
                    on: 'focus',
                    today: true,
                    touchReadonly: false,
                }).calendar('set date', new Date())
            },
            onApprove: () => {
                submitForm()
                return false
            }
        })
        .modal('show')
}

function inputMaskAmount() {
    let value = Number(document.activeElement.value.toString().replace(',', '').replace('.', ''))
    if (isNaN(value)) {
        document.activeElement.value = 0
        return false
    }
    value = value / 100
    document.activeElement.value = value.toLocaleString(LANGUAGE_CODE)
}

function getTransactionType() {
    return $('#transaction-type .item.active').attr('data-value')
}

function initializeAccountDropdown() {
    $('#accounts-dropdown').dropdown({
        placeholder: gettext("Account"),
        apiSettings: {
            url: '/fn/api/accounts/',
            cache: false,
            successTest: r => r.count > 0,
            onResponse: r => {
                results = r.results
                    .map(e => ({
                        name: e.name,
                        value: e.id,
                    }))
                return {
                    count: r.count,
                    results: results,
                }
            }
        },
        forceSelection: false,
        filterRemoteData: true,
        onChange: () => {
            $('#categories-dropdown').dropdown('show', true)
        },
    })
}

function initializeCategoryDropdown() {
    $('#categories-dropdown').dropdown({
        placeholder: gettext("Category"),
        apiSettings: {
            url: '/fn/api/categories/',
            cache: false,
            successTest: r => r.count > 0,
            onResponse: r => {
                results = r.results
                    .filter(
                        e => e.type == getTransactionType()
                    )
                    .map(e => ({
                        name: e.name,
                        value: e.id,
                        icon: e.icon,
                    }))
                return {
                    count: r.count,
                    results: results,
                }
            },
        },
        forceSelection: false,
        filterRemoteData: true,
        allowReselection: true,
    })
}

function initializeAmountInput() {
    const el = $("input[name=amount]")
    el.on('input', e => {
        let value = Number(el.val().toString().replace(',', '').replace('.', ''))
        value = value / 100
        el.val(value.toLocaleString(LANGUAGE_CODE))
    })
    el.on('keypress', e => {
        if (e.which < 48 || e.which > 57) {
            e.preventDefault()
        }
    })
}

function onEnterTab() {

    function onEnterFocusNext(currentEl, callback) {
        $(currentEl).on(
            "keypress",
            function (e) {
                if ([13, 9].includes(e.keyCode)) callback()
            }
        )
    }

    onEnterFocusNext(
        'input[name=amount]',
        () => { $('input[name=description]').select() }
    )
    onEnterFocusNext(
        'input[name=description]',
        () => { $('#accounts-dropdown').dropdown('show') }
    )
}

function highlightTransaction(id) {
    $(`.ui.segment[data-transaction=${id}]`).css('transition', '1s')
    $(`.ui.segment[data-transaction=${id}]`)
        .css('background-color', '#fff8db')
        .css('color', '#b58105')
        .css('box-shadow', '0 0 0 1px #b58105 inset,0 0 0 0 transparent')
}