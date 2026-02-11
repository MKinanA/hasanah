const values = {};

function updateTargetHref() {
    const rawValues = {};
    document.querySelectorAll('input, select').forEach(element => {
        const name = element.getAttribute('name'), value = element.value;
        if (!([null, undefined, ''].includes(name) || [null, undefined, ''].includes(value))) rawValues[name] = value;
    });

    Object.keys(values).forEach(key => delete values[key]);

    ['first_created_by', 'last_updated_by'].forEach(name => {
        if (rawValues.hasOwnProperty(name)) values[name] = rawValues[name];
    });
    ['first_created_between', 'last_updated_between'].forEach(name => {
        if (rawValues.hasOwnProperty(name + '_start') || rawValues.hasOwnProperty(name + '_end')) values[name] = `${rawValues.hasOwnProperty(name + '_start') ? Math.floor(new Date(rawValues[name + '_start']).getTime() / 1000) : ''}-${rawValues.hasOwnProperty(name + '_end') ? Math.floor(new Date(rawValues[name + '_end']).getTime() / 1000) : ''}`;
    });
    if (rawValues.hasOwnProperty('sort')) values['sort'] = rawValues['sort'];
    if (rawValues.hasOwnProperty('include_deleted')) {
        values['include_deleted'] = 1;
        if (rawValues['include_deleted'] === 'only_deleted') values['include_undeleted'] = 0;
    };

    const params = `${Object.keys(values).length > 0 ? '?' : ''}${Object.keys(values).map(key => `${key}=${values[key]}`).join('&')}`;
    history.replaceState(null, '', `filter` + params);
    document.querySelector('a#apply-button').setAttribute('href', `../payments${params}`);
};

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input, select').forEach(element => element.addEventListener('change', updateTargetHref));
});