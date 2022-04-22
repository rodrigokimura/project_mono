function getCoverage(covered, statements) {
    if (statements == 0) {
        return '0%'
    }
    return Number.parseFloat(covered / statements * 100).toFixed(1) + '%'
}
function calculateCoverageSummary(results) {
    totalCovered = results.map(r => r.covered_lines).reduce((a, b) => a + b, 0)
    totalMissing = results.map(r => r.missing_lines).reduce((a, b) => a + b, 0)
    totalExcluded = results.map(r => r.excluded_lines).reduce((a, b) => a + b, 0)
    totalStatements = results.map(r => r.num_statements).reduce((a, b) => a + b, 0)
    $('.card-statistic .value[data-type=total_covered]').text(totalCovered)
    $('.card-statistic .value[data-type=total_missing]').text(totalMissing)
    $('.card-statistic .value[data-type=total_excluded]').text(totalExcluded)
    $('.card-statistic .value[data-type=total_statements]').text(totalStatements)
    $('.card-statistic .value[data-type=total_coverage]').text(getCoverage(totalCovered, totalStatements))
}
function summarizeResultsByFirstLevelFolder(results) {
    function sumarizePropByFolder(results, folder, prop) {
        return results.filter(r => r.file.startsWith(folder + '/')).map(r => r[prop]).reduce((a, b) => a + b, 0)
    }
    firstLevelFolders = [...new Set(results.map(r => r.file.split('/', 1)[0]))]
    return firstLevelFolders.map(
        folder => {
            covered = sumarizePropByFolder(results, folder, 'covered_lines')
            statements = sumarizePropByFolder(results, folder, 'num_statements')
            return {
                file: folder,
                covered_lines: covered,
                missing_lines: sumarizePropByFolder(results, folder, 'missing_lines'),
                excluded_lines: sumarizePropByFolder(results, folder, 'excluded_lines'),
                num_statements: statements,
                coverage: getCoverage(covered, statements),
            }
        }
    )
}
async function renderCoverageReport() {
    $.api({
        on: 'now',
        method: 'GET',
        url: '/hc/api/coverage/',
        stateContext: '#coverage',
        onSuccess: r => {    
            var el = $('#coverage-table tbody')
            el.empty()
            if (r.results.length == 0) {
                toast('No results found.')
                $('#coverage-table').hide()
                return
            } else {
                toast(`${r.results.length} results found.`)
                $('#coverage-table').show()
            }
            calculateCoverageSummary(r.results)
            resultsByFirstLevelFolder = summarizeResultsByFirstLevelFolder(r.results)
            resultsByFirstLevelFolder.forEach(resultByFolder => {
                el.append(`
                    <tr data-folder="${resultByFolder.file}">
                        <td><strong><i class="caret down icon"></i>${resultByFolder.file}</strong></td>
                        <td><strong>${resultByFolder.covered_lines}</strong></td>
                        <td><strong>${resultByFolder.missing_lines}</strong></td>
                        <td><strong>${resultByFolder.excluded_lines}</strong></td>
                        <td><strong>${resultByFolder.num_statements}</strong></td>
                        <td><strong>${resultByFolder.coverage}</strong></td>
                    </tr>
                `)
                r.results.filter(result => result.file.startsWith(resultByFolder.file + '/')).forEach(x => {
                    el.append(`
                        <tr data-parent="${resultByFolder.file}">
                            <td>${x.file}</td>
                            <td>${x.covered_lines}</td>
                            <td>${x.missing_lines}</td>
                            <td>${x.excluded_lines}</td>
                            <td>${x.num_statements}</td>
                            <td>${getCoverage(x.covered_lines, x.num_statements)}</td>
                        </tr>
                    `)
                })
                el.find(`tr[data-folder='${resultByFolder.file}']`).click(e => {
                    caret = el.find(`tr[data-folder='${resultByFolder.file}']`).find('.caret.icon')
                    if (caret.hasClass('caret right')) {
                        caret.removeClass('caret right').addClass('caret down')
                    } else if (caret.hasClass('caret down')){
                        caret.removeClass('caret down').addClass('caret right')
                    }
                    el.find(`tr[data-parent=${resultByFolder.file}]`).toggle()
                })
            })
        }
    })
}