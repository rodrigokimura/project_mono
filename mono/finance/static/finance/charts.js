
function getCharts() {
    chartsEl = $('#charts');
    $.api({
        on: "now",
        url: `/fn/api/charts/`,
        headers: { 'X-CSRFToken': csrftoken },
        onSuccess: r => {
            chartIds = r.data;
            chartsEl.empty();
            for (id of chartIds) {
                chartsEl.append(`
                    <div class="ui eight wide column">
                        <div class="ui fluid card" data-chart-id="${id}">
                            <div class="content" id="chart-${id}"></div>
                        </div>
                    </div>
                `)
                renderChart(id);
            }
        },
    });
}

function renderChart(chartId) {
    $.api({
        on: "now",
        url: `/fn/api/charts/${chartId}/`,
        headers: { 'X-CSRFToken': csrftoken },
        stateContext: `.ui.card[data-chart-id=${chartId}]`,
        onSuccess: r => {
            options = getOptions(r.data);
            chart = new ApexCharts($(`#chart-${chartId}`)[0], options);
            chart.render();
        },
    });
}

function getOptions(data) {
    axes = [...new Set(data['data_points'].map(d => d.axis))];
    categs = [...new Set(data['data_points'].map(d => d.categ))];

    options = {
        'series': [],
        'xaxis': {
            'categories': axes,
        },
        'title': {
            text: data['title'],
            align: 'left'
        },
        'yaxis': {
            'title': {
                'text': data['field']
            }
        },
        'chart': {
            'height': 350
        },
        'dataLabels': {
            'enabled': false
        },
    }
    options = setChartType(options, data['chart_type']);

    if (data['chart_type'] === 'donut') {
        options['labels'] = [];
        for (categ of categs) {
            filteredData = data['data_points'].filter(d => d.categ == categ);
            categData = filteredData.map(d => d.metric).reduce((partial_sum, a) => partial_sum + a, 0);
            options['series'].push(Math.round(categData * 100) / 100);
            options['labels'].push(categ);
        }
    } else {
        for (categ of categs) {
            categData = [];
            for (ax of axes) {
                filteredData = data['data_points'].filter(d => d.axis == ax && d.categ == categ);
                if (filteredData.length > 0) {
                    categData.push(
                        Math.round(filteredData.map(d => d.metric).reduce((partial_sum, a) => partial_sum + a, 0) * 100) / 100
                    );
                } else {
                    categData.push(0);
                }
            }
            options['series'].push(
                {
                    'name': categ,
                    'data': categData,
                }
            );
        }
    }

    return options;
}

function setChartType(options, type) {
    switch (type) {
        case 'bar':
            options['chart']['type'] = 'bar';
            options['chart']['stacked'] = true;
            options['plotOptions'] = {
                bar: {
                    horizontal: true
                }
            }
            break;
        case 'column':
            options['chart']['type'] = 'bar';
            options['chart']['stacked'] = true;
            options['plotOptions'] = {
                bar: {
                    horizontal: false
                }
            }
            break;
        case 'line':
            options['chart']['type'] = 'line';
            options['stroke'] = {
                curve: 'smooth'
            }
            break;
        case 'donut':
            options['chart']['type'] = 'donut';
            break;
    }
    return options;
}