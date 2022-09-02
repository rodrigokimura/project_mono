async function toast(title, message) {
    $('body').toast({
        title: title,
        message: message,
        class: 'success',
        className: { toast: 'ui message' },
        showProgress: 'bottom',
        closeIcon: true,
    })
}

function getConfigAttr(config, attr, fallback) {
    try {
        return config[attr] || fallback
    }
    catch(err) {
        return fallback
    }
}