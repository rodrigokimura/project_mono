async function renderChangelog() {
    $.api({
        on: 'now',
        method: 'GET',
        url: '/hc/api/changelog/',
        stateContext: '#changelog',
        onSuccess: r => {
            $('#changelog').html(r.html)
        },
    })
}