function initializeDragula() {
    var chartsDrake = dragula([$('#charts')[0]],
        {
            moves: (el, source, handle, sibling) => (
                $(handle).hasClass('handle')
                || $(handle).parent().hasClass('handle')
            ),
            accepts: (el, target, source, sibling) => true,
            direction: 'horizontal'
        }
    )
        .on('drop', (el, target, source, sibling) => {
            chart = $(el).find('.chart-card').attr('data-chart-id');
            order = $(target).children().toArray().findIndex(e => e == el) + 1;
            console.log(order)
            $.api({
                on: 'now',
                url: `/fn/api/chart-move/`,
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                stateContext: `.chart-card[data-chart-id=${chart}]`,
                data: {
                    chart: chart,
                    order: order,
                },
                onSuccess: r => {
                    $('body').toast({
                        title: 'Success',
                        message: 'Chart order updated successfully',
                        class: 'success',
                    });
                },
                onFailure: () => {
                    $('body').toast({
                        title: 'Failure',
                        message: 'A problem occurred while updating chart order',
                        class: 'error',
                    });
                    getCharts();
                },
            });
        })
}


function getCharts() {
    chartsEl = $('#charts');
    $.api({
        on: "now",
        url: `/fn/api/charts/`,
        headers: { 'X-CSRFToken': csrftoken },
        onSuccess: r => {
            chartIds = r.data;
            chartsEl.empty();
            charts = [];
            for (id of chartIds) {
                chartsEl.append(
                    `
                    <div class="ui eight wide column">
                        <div class="ui fluid chart-card card" data-chart-id="${id}">
                            <div class="handle" style="display: flex; flex-flow: column nowrap; align-items: center; padding: 0; margin: 0; cursor: move;">
                                <i class="grip lines small icon"></i>
                            </div>                        
                            <div class="content">
                                <div class="ui tiny icon card-menu floating dropdown basic button" style="display: block; position: absolute; right: 1em; z-index: 99;">
                                    <i class="ellipsis horizontal icon"></i>
                                    <div class="menu">
                                        <div class="item" onclick="showChartModal(${id})"><i class="edit icon"></i>Edit chart</div>
                                        <div class="item" onclick="deleteChart(${id})"><i class="delete icon"></i>Delete chart</div>
                                    </div>
                                </div>
                                <div id="chart-${id}">
                                </div>
                            </div>
                        </div>
                    </div>
                    `
                )
                renderChart(id);
            }
            $('.card-menu.dropdown').dropdown();
            chartsEl.append(
                `
                <div class="ui eight wide column">
                    <div class="ui fluid button" onclick="showChartModal()">Add new chart</div>
                </div>
                `
            )
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
            charts.push(
                {
                    id: chartId,
                    title: r.data['title'],
                    type: r.data['type'],
                    metric: r.data['metric'],
                    field: r.data['field'],
                    axis: r.data['axis'],
                    category: r.data['category'],
                    filters: r.data['filters'],
                }
            )
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
                'text': data['field_display']
            }
        },
        'chart': {
            'height': 350,
            'toolbar': {
                'show': false
            }
        },
        'dataLabels': {
            'enabled': false
        },
    }
    options = setChartType(options, data['type']);

    if (data['type'] === 'donut') {
        options['labels'] = [];
        for (categ of categs) {
            filteredData = data['data_points'].filter(d => d.categ == categ);
            categData = filteredData.map(d => d.metric).reduce((partial_sum, a) => partial_sum + a, 0);
            options['series'].push(Math.round(categData * 100) / 100);
            options['labels'].push(categ);
        }
        options['dataLabels'] = {
            'enabled': true
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

function deleteChart(chartId) {
    $('body').modal({
        title: 'Important Notice',
        class: 'mini',
        closeIcon: true,
        content: 'Are you sure you want to delete this chart?',
        actions: [
            {
                text: 'Cancel',
                class: 'black deny',
            },
            {
                text: 'Yes, delete it',
                class: 'red approve',
            },
        ],
        onApprove: () => {
            $.api({
                on: "now",
                url: `/fn/api/charts/${chartId}/`,
                method: "DELETE",
                headers: { 'X-CSRFToken': csrftoken },
                onSuccess: r => {
                    $('body').toast({
                        title: 'Success',
                        message: 'Chart deleted successfully',
                    });
                    $(`.ui.card[data-chart-id=${chartId}]`).parent().remove();
                },
            });
        }
    }).modal('show');
}

function showChartModal(chartId = null) {
    var create = chartId === null;
    const modal = $('.ui.chart.modal');
    if (create) {
        modal.find('.header').text('Add new chart');
        url = '/fn/api/charts/';
    } else {
        modal.find('.header').text('Edit chart');
        url = `/fn/api/charts/${chartId}/`;
        chartData = charts.filter(e => e.id == chartId)[0];
        modal.find('input[name=title]').val(chartData['title'])
        modal.find('.dropdown[data-field=type]').dropdown('set selected', chartData['type'])
        modal.find('.dropdown[data-field=metric]').dropdown('set selected', chartData['metric'])
        modal.find('.dropdown[data-field=field]').dropdown('set selected', chartData['field'])
        modal.find('.dropdown[data-field=axis]').dropdown('set selected', chartData['axis'])
        modal.find('.dropdown[data-field=category]').dropdown('set selected', chartData['category'])
        modal.find('.dropdown[data-field=filter]').dropdown('set selected', chartData['filters'])
    }
    modal
        .modal({
            onApprove: () => {
                $.api({
                    on: "now",
                    url: url,
                    method: create ? 'POST' : 'PATCH',
                    headers: { 'X-CSRFToken': csrftoken },
                    data: {
                        title: modal.find('input[name=title]').val(),
                        type: modal.find('.dropdown[data-field=type]').dropdown('get value'),
                        metric: modal.find('.dropdown[data-field=metric]').dropdown('get value'),
                        field: modal.find('.dropdown[data-field=field]').dropdown('get value'),
                        axis: modal.find('.dropdown[data-field=axis]').dropdown('get value'),
                        category: modal.find('.dropdown[data-field=category]').dropdown('get value'),
                        filter: modal.find('.dropdown[data-field=filter]').dropdown('get value').split(','),
                    },
                    onSuccess: r => {
                        $('body').toast({
                            title: 'Success',
                            message: 'Chart saved successfully',
                        });
                        modal.find('input[name=title]').val('');
                        modal.find('.dropdown').dropdown('clear');
                        getCharts();
                    },
                    onFailure: () => { console.log('failure') },
                })
            },
        })
        .modal('show');
}