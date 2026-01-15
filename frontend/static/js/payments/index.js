import {} from '../utils/auth.js';
import { leadingZeros } from '../utils/formatting.js';

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('body > div > main > div#table > table > tbody > tr > td:is(:nth-child(2), :nth-child(4)) > p').forEach(cell => {
        const date = new Date(parseInt(cell.textContent) * 1000);
        cell.textContent = `${leadingZeros(date.getDate(), 2)}/${leadingZeros(date.getMonth() + 1, 2)}/${leadingZeros(date.getFullYear(), 2)} ${leadingZeros(date.getHours(), 2)}:${leadingZeros(date.getMinutes(), 2)}:${leadingZeros(date.getSeconds(), 2)}`
    });
});