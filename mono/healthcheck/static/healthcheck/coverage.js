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
    $('.card-statistic .value[data-type=total_covered]').text(totalCovered.toLocaleString())
    $('.card-statistic .value[data-type=total_missing]').text(totalMissing.toLocaleString())
    $('.card-statistic .value[data-type=total_excluded]').text(totalExcluded.toLocaleString())
    $('.card-statistic .value[data-type=total_statements]').text(totalStatements.toLocaleString())
    coverage = getCoverage(totalCovered, totalStatements)
    $('.card-statistic .value[data-type=total_coverage]').text(`${coverage.toLocaleString()}%`)
    $('.card-statistic .value[data-type=total_coverage]').parent().parent().append(`
        <div class="ui bottom attached progress" data-percent="${coverage}">
            <div class="bar"></div>
        </div>
    `)
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
                            <td>${resultByFolder.covered_lines.toLocaleString()}</td>
                            <td>${resultByFolder.missing_lines.toLocaleString()}</td>
                            <td>${resultByFolder.excluded_lines.toLocaleString()}</td>
                            <td>${resultByFolder.num_statements.toLocaleString()}</td>
                            <td>
                                ${getCoverageProgressBar(resultByFolder.coverage, "standard")}
                            </td>
                        </tr>
                    `)
                } else {
                    el.append(`
                        <tr data-folder="${resultByFolder.file}">
                            <td>
                                <strong><i class="caret down icon"></i>${resultByFolder.file}</strong>
                            </td>
                            <td><strong>${resultByFolder.covered_lines.toLocaleString()}</strong></td>
                            <td><strong>${resultByFolder.missing_lines.toLocaleString()}</strong></td>
                            <td><strong>${resultByFolder.excluded_lines.toLocaleString()}</strong></td>
                            <td><strong>${resultByFolder.num_statements.toLocaleString()}</strong></td>
                            <td>
                                ${getCoverageProgressBar(resultByFolder.coverage, "standard")}
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
                                    ${getCoverageProgressBar(getCoverage(x.covered_lines, x.num_statements))}
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
            collapseAll('coverage-table')
        }
    })
}

function getCoverageProgressBar(percent, size="small") {
    return `
        <div class="ui ${size} indicating progress" data-percent="${percent}" style="margin: 0;">
            <div class="bar">
                <div class="progress"></div>
            </div>
        </div>
    `
}