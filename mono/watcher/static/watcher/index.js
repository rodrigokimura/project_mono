function getIssues() {
    $.api({
        url: '/watcher/api/issues/',
        on: 'now',
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
                            <td data-label="Name">${i.name}</td>
                            <td data-label="Description">${i.description}</td>
                            <td data-label="Events">${i.events}</td>
                            <td data-label="Users">${i.users}</td>
                            <td data-label="First event">${i.first_event}</td>
                            <td data-label="Last event">${i.last_event}</td>
                        </tr>
                    `)
                })
            }
        }
    })
}
function getAvgRequestsByAppName() {
    $.api({
        url: '/watcher/api/requests/app_name/',
        on: 'now',
        successTest: function (response) { return true },
        onSuccess: function (response) {
            $(`#requests-by-app tbody`).empty()
            response.forEach(i => {
                $(`#requests-by-app tbody`).append(`
                    <tr>
                        <td data-label="App">${i.app_name}</td>
                        <td data-label="Duration">${(parseFloat(i.avg_duration) * 1000).toFixed(3)}</td>
                        <td data-label="Count">${i.total_count}</td>
                    </tr>
                `)
            })
            let total = response.reduce((acc, i) => acc + parseFloat(i.total_count), 0)
            $('#total-request-count').text(total)
        }
    })
}