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
    document.querySelector('a#apply-button').addEventListener('click', updateTargetHref);

    const params = new URL(location.href).searchParams;
    ['first_created_by', 'last_updated_by'].forEach(param => {
        if (params.get(param)) document.querySelector(`input[name="${param}"]`).value = params.get(param);
        console.log(params.get(param));
    });
    ['first_created_between', 'last_updated_between'].forEach(param => {
        if (params.get(param)) [
            parseInt(params.get(param).split('-')[0]) ? ['start', new Date(parseInt(params.get(param).split('-')[0]) * 1000)] : null,
            parseInt(params.get(param).split('-')[1]) ? ['end', new Date(parseInt(params.get(param).split('-')[1]) * 1000)] : null,
        ].filter(x => x !== null).forEach(
            dt => document.querySelector(`input[name="${param}_${dt[0]}"]`).value = `${dt[1].getFullYear()}-${(dt[1].getMonth() + 1).toString().padStart(2, '0')}-${dt[1].getDate().toString().padStart(2, '0')}T${dt[1].getHours().toString().padStart(2, '0')}:${dt[1].getMinutes().toString().padStart(2, '0')}:${dt[1].getSeconds().toString().padStart(2, '0')}`
        );
        console.log(params.get(param));
    });
    if (params.get('sort')) document.querySelector(`select[name="sort"]`).value = params.get('sort');
    if (params.get('include_deleted') == 1) {
        if (params.get('include_undeleted') == 0) document.querySelector(`select[name="include_deleted"]`).value = 'only_deleted';
        else document.querySelector(`select[name="include_deleted"]`).value = 'true';
    };
});