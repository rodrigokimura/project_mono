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

}
