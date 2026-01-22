import { leadingZeros } from '../utils/formatting.js';
import { parseAllTimestamps } from '../utils/datetime.js';
import { parseAllUsernameToName } from '../utils/username.js';

const names = {};

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('body > div > main > div#table > table > tbody > tr > td:is(:nth-child(2), :nth-child(4)) > p').forEach(cell => {
        const date = new Date(parseInt(cell.textContent) * 1000);
        cell.textContent = `${leadingZeros(date.getDate(), 2)}/${leadingZeros(date.getMonth() + 1, 2)}/${leadingZeros(date.getFullYear(), 2)} ${leadingZeros(date.getHours(), 2)}:${leadingZeros(date.getMinutes(), 2)}:${leadingZeros(date.getSeconds(), 2)}`
    });
    document.querySelectorAll('body > div > main > div#table > table > tbody > tr > td:is(:nth-child(3), :nth-child(5)) > p').forEach(async cell => {
        const username = cell.textContent;
        if (names[username] === undefined) names[username] = fetch('/api/user', {method: 'POST', body: JSON.stringify({
            username: username,
        })}).then(resp => resp.json().then(body => ({status: resp.status, ...body}))).then(body => (Math.floor(body.status / 100) === 2) && (body.type === 'success') ? body.name : username);
        cell.textContent = await names[username];
    });
    parseAllTimestamps();
    parseAllUsernameToName();
    document.querySelector('#delete-button').addEventListener('click', async e => {
        e.preventDefault();
        document.querySelector('#delete-button').classList.add('loading');
        if (!confirm('Hapus pembayaran ini?')) {
            document.querySelector('#delete-button').classList.remove('loading');
            return;
        };
        const resp = await fetch(document.querySelector('#delete-button').getAttribute('href'), {method: 'POST', body: JSON.stringify({})});
        const body = await resp.json();
        if ((Math.floor(resp.status / 100) === 2) && (body.type === 'success')) location.replace('.');
        else {
            alert(body.message ?? body.detail ?? 'Error');
            document.querySelector('#delete-button').classList.remove('loading');
        };
    });
});