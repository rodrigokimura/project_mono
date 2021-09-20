class Dashboard {
    constructor(id) {
        this.id = id;
    }
    get start() {
        return $('#rangestart').calendar('get date').toISOString().split('T')[0];
    }
    get end() {
        return $('#rangeend').calendar('get date').toISOString().split('T')[0];
    }
    updateGeneralInfo() {
        var params = $.param({
            start: this.start,
            end: this.end,
        });
        $.api({
            method: 'GET',
            url: `/pixel/dashboard/${this.id}/general-info/?${params}`,
            headers: { 'X-CSRFToken': csrftoken },
            on: 'now',
            stateContext: '.card-statistic',
            // loadingDuration: 1000,
            onSuccess: r => {
                var types = ['visitors', 'users', 'views', 'duration', 'bounce'];
                for (const t of types) {
                    $(`.card-statistic[data-type=${t}] .statistic .value`).text(r[t]);
                }
            }
        });
    }
    updateAggregatedByDate() {
        var params = $.param({
            start: this.start,
            end: this.end,
        });
        $.api({
            method: 'GET',
            url: `/pixel/dashboard/${this.id}/by-date/?${params}`,
            headers: { 'X-CSRFToken': csrftoken },
            on: 'now',
            stateContext: '.card-chart[data-type=by-date]',
            onSuccess: r => {
                var data = r.data;
                var dates = data.map(d => {
                    var date = new Date(d.date);
                    // return date;
                    return date.toLocaleDateString()
                });
                var views = data.map(d => d.views);
                var visitors = data.map(d => d.visitors);
                var duration = data.map(d => d.duration);
                var options = {
                    chart: {
                        type: 'line',
                        fontFamily: "Lato,'Helvetica Neue',Arial,Helvetica,sans-serif;"
                    },
                    plotOptions: {
                        bar: {
                            borderRadius: 4,
                        }
                    },
                    series: [
                        {
                            name: 'Views',
                            data: views,
                            type: 'line',
                        },
                        {
                            name: 'Visitors',
                            data: visitors,
                            type: 'line',
                        },
                        {
                            name: 'Page duration',
                            data: duration,
                            type: 'line',
                        },
                    ],
                    xaxis: {
                        categories: dates,
                        // type: 'datetime',
                    },
                    yaxis: [
                        {
                            show: false,
                            labels: { formatter: v => Math.ceil(v) }
                        },
                        {
                            show: false,
                            labels: { formatter: v => Math.ceil(v) }
                        },
                        { show: false },
                    ],
                }
                $('.card-chart[data-type=by-date]').empty();
                var chart = new ApexCharts($('.card-chart[data-type=by-date]')[0], options)
                chart.render()
            }
        });
    }
    updateAggregatedByDocLoc() {
        var params = $.param({
            start: this.start,
            end: this.end,
        });
        $.api({
            method: 'GET',
            url: `/pixel/dashboard/${this.id}/by-doc-loc/?${params}`,
            headers: { 'X-CSRFToken': csrftoken },
            on: 'now',
            stateContext: '.card-statistic',
            onSuccess: r => {
                $('#data-by-doc-loc').empty();
                r.data.forEach(d => {
                    $('#data-by-doc-loc').append(`
                        <tr>
                            <td>${d.document_location}</td>
                            <td>${d.views}</td>
                            <td>${d.visitors}</td>
                            <td>${d.duration}</td>
                        </tr>
                    `);
                });
                $('table').tablesort();
            }
        });
    }
    update() {
        this.updateGeneralInfo();
        this.updateAggregatedByDate();
        this.updateAggregatedByDocLoc();
    }
}
