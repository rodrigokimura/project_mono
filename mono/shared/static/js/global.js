$.fn.calendar.settings.text = {
    days: [
        pgettext('weekday sunday', 'S'),
        pgettext('weekday monday', 'M'), 
        pgettext('weekday tuesday', 'T'), 
        pgettext('weekday wednesday', 'W'), 
        pgettext('weekday thursday', 'T'), 
        pgettext('weekday friday', 'F'), 
        pgettext('weekday saturday', 'S'),
    ],
    months: [
        pgettext('month', 'January'), 
        pgettext('month', 'February'), 
        pgettext('month', 'March'), 
        pgettext('month', 'April'), 
        pgettext('month', 'May'), 
        pgettext('month', 'June'), 
        pgettext('month', 'July'), 
        pgettext('month', 'August'), 
        pgettext('month', 'September'), 
        pgettext('month', 'October'), 
        pgettext('month', 'November'), 
        pgettext('month', 'December'),
    ],
    monthsShort: [
        pgettext('short month', 'Jan'), 
        pgettext('short month', 'Feb'), 
        pgettext('short month', 'Mar'), 
        pgettext('short month', 'Apr'), 
        pgettext('short month', 'May'), 
        pgettext('short month', 'Jun'), 
        pgettext('short month', 'Jul'), 
        pgettext('short month', 'Aug'), 
        pgettext('short month', 'Sep'), 
        pgettext('short month', 'Oct'), 
        pgettext('short month', 'Nov'), 
        pgettext('short month', 'Dec'),
    ],
    today: gettext('Today'),
    now: gettext('Now'),
    am: pgettext('hour', 'AM'),
    pm: pgettext('hour', 'PM')
}

$.fn.calendar.settings.formatter.date = function (date, settings) {
    if (!date) return '';
    return date.toLocaleDateString(languageCode)
}

$.fn.calendar.settings.formatter.time = function (time, settings) {
    if (!time) return '';
    return time.toLocaleTimeString(languageCode, {hour: '2-digit', minute:'2-digit'})
}

function stringToLocalDatetime(dateString, location) {
    d = new Date(dateString)
    return d.toLocaleString(location)
}

function stringToLocalDate(dateString, location) {
    year = dateString.split('-')[0]
    month = dateString.split('-')[1] - 1
    day = dateString.split('-')[2]
    d = new Date(year, month, day)
    return d.toLocaleDateString(location)
}