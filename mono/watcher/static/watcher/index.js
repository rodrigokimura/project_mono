function getIssues() {
    $.api({
        on: 'now',
        url: '/watcher/api/issues/',
        stateContext: $('#unresolved-issues').closest('.ui.segment'),
        onSuccess: function (response) {
            let mapping = {
                '#unresolved-issues': response.results.filter(issue => !issue.resolved_at),
                '#resolved-issues': response.results.filter(issue => issue.resolved_at)
            }
            for (const [selector, issues] of Object.entries(mapping)) {
                $(`${selector} tbody`).empty()
                issues.forEach(i => {
                    $(`${selector} tbody`).append(`
                        <tr>
                            <td data-label="ID">${i.id}</td>
                            <td data-label="Name"><a href="/watcher/issue/${i.id}/">${i.name}</a></td>
                            <td data-label="Description">${i.description}</td>
                            <td data-label="Events">${i.events}</td>
                            <td data-label="Users">${i.users}</td>
                            <td data-label="First event">${stringToLocalDatetime(i.first_event, languageCode)}</td>
                            <td data-label="Last event">${stringToLocalDatetime(i.last_event, languageCode)}</td>
                        </tr>
                    `)
                })
            }
        }
    })
}
function getAvgRequestsByAppName() {
    $.api({
        on: 'now',
        url: '/watcher/api/requests/app_name/',
        stateContext: $('#requests-by-app').closest('.ui.segment'),
        successTest: function (response) { return true },
        onSuccess: function (response) {
            $(`#requests-by-app tbody`).empty()
            response.forEach(i => {
                $(`#requests-by-app tbody`).append(`
                    <tr>
                        <td data-label="App">${i.app_name ? i.app_name : '(No app)'}</td>
                        <td data-label="Duration">${(parseFloat(i.avg_duration) * 1000).toLocaleString(languageCode)}</td>
                        <td data-label="Count">${i.total_count}</td>
                    </tr>
                `)
            })
            let total = response.reduce((acc, i) => acc + parseFloat(i.total_count), 0)
            $('#total-request-count').text(total.toLocaleString(languageCode))
        }
    })
}