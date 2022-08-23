function getCoverage(covered, statements) {
    if (statements == 0) {
        return 0
    }
    return Number(covered / statements * 100).toFixed(1)
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
        return results.filter(r => r.file.startsWith(folder)).map(r => r[prop]).reduce((a, b) => a + b, 0)
    }
    firstLevelFolders = [...new Set(results.map(r => r.file.split('/', 1)[0]))]
    return firstLevelFolders.map(
        folder => {
            let isTopLevelFile = results.map(r => r.file).includes(folder)
            if (!isTopLevelFile) {
                folder = folder + '/'
            }
            covered = sumarizePropByFolder(results, folder, 'covered_lines')
            statements = sumarizePropByFolder(results, folder, 'num_statements')
            return {
                file: folder,
                isTopLevelFile: isTopLevelFile,
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
            resultsByFirstLevelFolder.sort(
                (x, y) => {
                    // isTopLevelFile values last
                    return (x.isTopLevelFile === y.isTopLevelFile) ? 0 : x.isTopLevelFile ? 1 : -1;
                }
            )
            resultsByFirstLevelFolder.forEach(resultByFolder => {
                let isTopLevelFile = resultByFolder.isTopLevelFile
                if (isTopLevelFile === true) {
                    el.append(`
                        <tr data-folder="${resultByFolder.file}">
                            <td>
                                ${resultByFolder.file}
                            </td>
                            <td>${resultByFolder.covered_lines}</td>
                            <td>${resultByFolder.missing_lines}</td>
                            <td>${resultByFolder.excluded_lines}</td>
                            <td>${resultByFolder.num_statements}</td>
                            <td>
                                ${getProgressBar(resultByFolder.coverage, "standard")}
                            </td>
                        </tr>
                    `)
                } else {
                    el.append(`
                        <tr data-folder="${resultByFolder.file}">
                            <td>
                                <strong><i class="caret down icon"></i>${resultByFolder.file}</strong>
                            </td>
                            <td><strong>${resultByFolder.covered_lines}</strong></td>
                            <td><strong>${resultByFolder.missing_lines}</strong></td>
                            <td><strong>${resultByFolder.excluded_lines}</strong></td>
                            <td><strong>${resultByFolder.num_statements}</strong></td>
                            <td>
                                ${getProgressBar(resultByFolder.coverage, "standard")}
                            </td>
                        </tr>
                    `)
                    r.results.filter(result => result.file.startsWith(resultByFolder.file)).forEach(x => {
                        el.append(`
                            <tr data-parent="${resultByFolder.file}">
                                <td>${x.file}</td>
                                <td>${x.covered_lines}</td>
                                <td>${x.missing_lines}</td>
                                <td>${x.excluded_lines}</td>
                                <td>${x.num_statements}</td>
                                <td>
                                    ${getProgressBar(getCoverage(x.covered_lines, x.num_statements))}
                                </td>
                            </tr>
                        `)
                    })
                    // Collapse sub rows on click
                    el.find(`tr[data-folder='${resultByFolder.file}']`).click(e => {
                        let caret = el.find(`tr[data-folder='${resultByFolder.file}']`).find('.caret.icon')
                        if (caret.hasClass('right')) {
                            caret.removeClass('right').addClass('down')
                        } else if (caret.hasClass('down')){
                            caret.removeClass('down').addClass('right')
                        }
                        el.find(`tr[data-parent='${resultByFolder.file}']`).toggle()
                    })
                }
            })
            $('.ui.progress').progress({
                precision: 1
            })
            collapseAll()
        }
    })
}

function collapseAll() {
    $('#coverage-table tbody tr[data-folder]').each((i, el) => {
        let file = $(el).data('folder')
        let caret = $(el).find('.caret.icon')

        caret.removeClass('down').addClass('right')
        $('#coverage-table tbody').find(`tr[data-parent='${file}']`).hide()
    })
}

function getProgressBar(percent, size="small") {
    return `
        <div class="ui ${size} indicating progress" data-percent="${percent}" style="margin: 0;">
            <div class="bar">
                <div class="progress"></div>
            </div>
        </div>
    `
}