function getChartOptions(commitSeries, dateLabels) {
    return {
        series: commitSeries,
        chart: {
            height: 180,
            type: 'heatmap',
            fontFamily: "Lato,'Helvetica Neue',Arial,Helvetica,sans-serif;",
            events: {
                dataPointSelection: function(event, chartContext, config) {
                    date = dateLabels[6-config.seriesIndex][config.dataPointIndex]
                    getCommitsByDate(date)
                }
            },
            toolbar: { show: false }
        },
        dataLabels: { enabled: false },
        tooltip: {
            x: {
                formatter: (v, o) => dateLabels[6-o.seriesIndex][o.dataPointIndex],
            },
        },
        grid: {
            show: false,
            xaxis: { lines: { show: false } },                    
            yaxis: { lines: { show: false } },                    
        },
        plotOptions: {
            heatmap: {
                radius: 4,
                shadeIntensity: 1,
                useFillColorAsStroke: false,
                colorScale: {
                    min: 0,
                },
            },
        },
        colors: [ "#008FFB" ],
        title: { show: false },
        xaxis: {
            labels: { show: false },
            axisBorder: { show: false },
        },
    }
}

async function getCommitsByDate(date) {
    $.api({
        on: 'now',
        url: `/hc/api/commits/by-date/?date=${date}`,
        method: 'GET',
        stateContext: '.segment',
        onSuccess: r => {
            renderCommits(r)
        }
    })
}

async function renderHeatmap() {
    if ($('#chart').html()) { return }
    $.api({
        on: 'now',
        method: 'GET',
        url: '/hc/api/commits/for-heatmap/',
        stateContext: '#chart',
        onSuccess: r => {
            dateLabels = [
                r.data_0.map(d => d.d),
                r.data_1.map(d => d.d),
                r.data_2.map(d => d.d),
                r.data_3.map(d => d.d),
                r.data_4.map(d => d.d),
                r.data_5.map(d => d.d),
                r.data_6.map(d => d.d),
            ]
            commitSeries = [
                { name: 'S', data: r.data_0.map(d => d.c) },
                { name: 'M', data: r.data_1.map(d => d.c) },
                { name: 'T', data: r.data_2.map(d => d.c) },
                { name: 'W', data: r.data_3.map(d => d.c) },
                { name: 'T', data: r.data_4.map(d => d.c) },
                { name: 'F', data: r.data_5.map(d => d.c) },
                { name: 'S', data: r.data_6.map(d => d.c) },
            ].reverse()
            var chart = new ApexCharts($('#chart')[0], getChartOptions(commitSeries, dateLabels))
            chart.render()
        },
    })
}

async function renderCommits(commits) {
    var el = $('#commits-table tbody')
    el.empty()
    if (commits.length == 0) {
        toast('No commits found.')
        $('#commits-table').hide()
        return
    } else {
        toast(`${commits.length} commits found.`)
        $('#commits-table').show()
    }
    for (var i = 0; i < commits.length; i++) {
        var commit = commits[i]
        var commitEl = $(`
            <tr>
                <td data-label="SHA">${commit.hexsha}</td>
                <td data-label="Message">${commit.message}</td>
                <td data-label="Author">${commit.author}</td>
            </tr>
        `)
        el.append(commitEl)
    }
}