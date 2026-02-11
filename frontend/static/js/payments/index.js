import { leadingZeros } from '../utils/formatting.js';

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
    // document.querySelector('#scrolltop-button').addEventListener('click', () => {
    //     if (document.body.scrollTop !== 0) document.body.scrollTop = 0;
    //     else {
    //         setTimeout(() => {
    //             document.body.scrollTop = 0;
    //         }, 125);
    //         document.body.scrollTop = window.innerHeight / 16;
    //     };
    // });
    ['#export-button', '#filter-button'].forEach(buttonID => document.querySelector(buttonID).setAttribute('href', document.querySelector(buttonID).getAttribute('href') + location.search.substring(document.querySelector(buttonID).getAttribute('href').includes('?') ? 1 : 0)));
});