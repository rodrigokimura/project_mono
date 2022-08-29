async function renderSummary() {
    $.api({
        on: 'now',
        method: 'GET',
        url: '/hc/api/summary/',
        stateContext: '#summary',
        onSuccess: r => {
            console.table(r.results)
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
        }
    })
}