String.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    var hours = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours < 10) { hours = "0" + hours; }
    if (minutes < 10) { minutes = "0" + minutes; }
    if (seconds < 10) { seconds = "0" + seconds; }
    return hours + ':' + minutes + ':' + seconds;
}


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
                    return date.toLocaleDateString()
                });
                var views = data.map(d => d.views);
                var visitors = data.map(d => d.visitors);
                var duration = data.map(d => d.duration);
                var options = {
                    chart: {
                        type: 'line',
                        fontFamily: "Lato,'Helvetica Neue',Arial,Helvetica,sans-serif;",
                        height: '370px',
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
            stateContext: '#by-doc-loc .segments',
            onSuccess: r => {
                $('#by-doc-loc row').remove();
                r.data.forEach(d => {
                    $('#by-doc-loc .list').append(`
                        <div class="row">
                            <div class="seven wide column doc-loc">${d.document_location}</div>
                            <div class="three wide column right aligned views">${d.views}</div>
                            <div class="three wide column right aligned visitors">${d.visitors}</div>
                            <div class="three wide column right aligned duration" data-duration="${d.duration}">${d.duration.toHHMMSS()}</div>
                        </div>
                    `);
                });
                var options = {
                    valueNames: [
                        'doc-loc',
                        'views',
                        'visitors',
                        { name: 'duration', attr: 'data-duration' },
                    ]
                };
                var byDocLocList = new List('by-doc-loc', options);
            }
        });
    }
    update() {
        this.updateGeneralInfo();
        this.updateAggregatedByDate();
        this.updateAggregatedByDocLoc();
    }
}
