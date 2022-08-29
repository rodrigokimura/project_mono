async function renderSummary() {
    $.api({
        on: 'now',
        method: 'GET',
        url: '/hc/api/summary/',
        stateContext: '#summary',
        onSuccess: r => {
            $('#summary').empty()
            toast(`${r.results.length} results found.`)
            let now = new Date()
            let deploysLastWeek = r.results
                .map(
                    r => new Date(r.deployed_at)
                )
                .filter(
                    d => d >= now.setDate(now.getDate() - 7)
                )
            $('.card-statistic .value[data-type=pull_requests]').text(r.results.length)
            $('.card-statistic .value[data-type=deploys_lw]').text(deploysLastWeek.length)
            let keysToFilter = ['pytest_tests', 'pytest_duration', 'cov_statements', 'cov_coverage', 'pylint_issues', 'pylint_score']
            let results = r.results.filter(
                r => {
                    return keysToFilter.some(
                        k => r[k] != null
                    )
                }
            )
            renderCharts(results)
        }
    })
}

function renderCharts(data) {
    ['pytest', 'coverage', 'pylint'].forEach(
        v => {
            $('#summary').append(`
                <div class="ui segment">
                    <div id="summary-chart-${v}"></div>
                </div>
            `)
        }
    )
    let categories = data.map(r => r.number)
    renderChart(
        $('#summary-chart-pytest'),
        'Pytest', categories,
        "Tests", data.map(r => r['pytest_tests']),
        "Duration", data.map(r => r['pytest_duration'])
    )
    renderChart(
        $('#summary-chart-coverage'),
        'Coverage', categories,
        "Statements", data.map(r => r['cov_statements']),
        "Coverage", data.map(r => r['cov_coverage'])
    )
    renderChart(
        $('#summary-chart-pylint'),
        'Pylint', categories,
        "Issues", data.map(r => r['pylint_issues']),
        "Score", data.map(r => r['pylint_score'])
    )
}

async function renderChart(element, title, categories, columnName, columnData, lineName, lineData) {
    let options = {
        series: [
            {
                name: columnName,
                type: "column",
                data: columnData,
            },
            {
                name: lineName,
                type: "line",
                data: lineData,
            },
        ],
        chart: {
            height: 350,
            zoom: {
                enabled: false
            }
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'straight'
        },
        title: {
            text: title,
            align: 'left'
        },
        grid: {
            row: {
                colors: ['#f3f3f3', 'transparent'],
                opacity: 0.5
            },
        },
        xaxis: {
            categories: categories,
        },
        yaxis: [
            {
                labels: {
                    formatter: v => v?.toFixed(0),
                }
            },
            {
                opposite: true,
                labels: {
                    formatter: v => v?.toFixed(2),
                }
            },
        ],
    }
    let chart = new ApexCharts(element[0], options)
    chart.render()
}