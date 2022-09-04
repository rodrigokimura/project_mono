async function toast(message) {
    $('body').toast({
        message: message,
        showProgress: 'bottom',
        closeIcon: true,
    })
}

function getConfigAttr(config, attr, fallback) {
    try {
        return config[attr] || fallback
    }
    catch (err) {
        return fallback
    }
}

function setSelectionRange(input, selectionStart, selectionEnd) {
    if (input.setSelectionRange) {
        input.focus()
        input.setSelectionRange(selectionStart, selectionEnd)
    }
    else if (input.createTextRange) {
        var range = input.createTextRange()
        range.collapse(true)
        range.moveEnd('character', selectionEnd)
        range.moveStart('character', selectionStart)
        range.select()
    }
  }
  
function setCaretToPos(input, pos) {
    setSelectionRange(input, pos, pos)
}