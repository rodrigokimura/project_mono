function summarizePytestResults(results) {
    testCount = results.length
    
}
function calculatePytestSummary(results) {
    totalDuration = results.map(r => r.duration).reduce((a, b) => a + b, 0)
    $('.card-statistic .value[data-type=total_count]').text(results.length)
    $('.card-statistic .value[data-type=total_duration]').text(Number.parseFloat(totalDuration).toFixed(3))
}
function summarizePytestByFirstLevelFolder(results) {
    function sumarizePropByFolder(results, folder, prop) {
        return results.filter(r => r.node_id.startsWith(folder + '/')).map(r => r[prop]).reduce((a, b) => a + b, 0)
    }
    firstLevelFolders = [...new Set(results.map(r => r.node_id.split('/', 1)[0]))]
    return firstLevelFolders.map(
        folder => {
            return {
                node_id: folder,
                count: results.filter(r => r.node_id.startsWith(folder + '/')).length,
                duration: Number.parseFloat(sumarizePropByFolder(results, folder, 'duration')).toFixed(3),
            }
        }
    )
}

async function renderPytestReport() {
    $.api({
        on: 'now',
        method: 'GET',
        url: '/hc/api/pytest/',
        stateContext: '#pytest',
        onSuccess: r => {
            var el = $('#pytest-table tbody')
            el.empty()
            if (r.pytest_results.length == 0) {
                toast('No results found.')
                $('#pytest-table').hide()
                return
            } else {
                toast(`${r.pytest_results.length} results found.`)
                $('#pytest-table').show()
            }
            results = r.pytest_results
            calculatePytestSummary(results)
            resultsByFirstLevelFolder = summarizePytestByFirstLevelFolder(results)
            resultsByFirstLevelFolder.forEach(resultByFolder => {
                el.append(`
                    <tr data-folder="${resultByFolder.node_id}">
                        <td><strong><i class="caret down icon"></i>${resultByFolder.node_id}</strong></td>
                        <td><strong>${resultByFolder.count}</strong></td>
                        <td><strong>${resultByFolder.duration}</strong></td>
                        <td><strong> - </strong></td>
                    </tr>
                `)
                results.filter(result => result.node_id.startsWith(resultByFolder.node_id + '/')).forEach(x => {
                    el.append(`
                        <tr data-parent="${resultByFolder.node_id}">
                            <td colspan="2">${x.node_id}</td>
                            <td>${Number.parseFloat(x.duration).toFixed(3)}</td>
                            <td>${x.outcome}</td>
                        </tr>
                    `)
                })
                el.find(`tr[data-folder=${resultByFolder.node_id}]`).click(e => {
                    caret = el.find(`tr[data-folder='${resultByFolder.node_id}']`).find('.caret.icon')
                    if (caret.hasClass('caret right')) {
                        caret.removeClass('caret right').addClass('caret down')
                    } else if (caret.hasClass('caret down')){
                        caret.removeClass('caret down').addClass('caret right')
                    }
                    el.find(`tr[data-parent=${resultByFolder.node_id}]`).toggle()
                })
            })
        }
    })
}