function summarizePylintResults(results) {
    types = ['convention', 'refactor', 'warning']
    summarizedResults = {}
    types.forEach(t => {
        result = results.filter(r => r.type == t).length
        $(`.card-statistic .value[data-type='${t}']`).text(result)
    })
    result = results.filter(r => !types.includes(r.type)).length
    $(`.card-statistic .value[data-type='other']`).text(result)
}

async function renderPylintReport() {
    $.api({
        on: 'now',
        method: 'GET',
        url: '/hc/api/pylint/',
        stateContext: '#pylint',
        onSuccess: r => {
            var el = $('#pylint-table tbody')
            el.empty()
            if (r.results.length == 0) {
                toast('No results found.')
                $('#pylint-table').hide()
                return
            } else {
                toast(`${r.results.length} results found.`)
                $('#pylint-table').show()
            }
            results = r.results
            summarizePylintResults(results)
            results.forEach(result => {
                el.append(`
                    <tr>
                        <td>${result.type}</td>
                        <td>${result.module}</td>
                        <td>${result.obj}</td>
                        <td>${result.line}</td>
                        <td>${result.column}</td>
                        <td>${result.path}</td>
                        <td>${result.symbol}</td>
                        <td>${result.message}</td>
                        <td>${result.message_id}</td>
                    </tr>
                `)
            })
            for (var i = 0; i < r.results.length; i++) {
                var result = r.results[i]
            }
        }
    })
}