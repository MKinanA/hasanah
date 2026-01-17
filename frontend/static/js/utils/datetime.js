import { leadingZeros } from './formatting.js';

export const parseAllTimestamps = (selector = '.timestamp') => document.querySelectorAll(selector).forEach(element => {
    const date = new Date(parseInt(element.textContent) * 1000);
    element.textContent = `${leadingZeros(date.getDate(), 2)}/${leadingZeros(date.getMonth() + 1, 2)}/${leadingZeros(date.getFullYear(), 2)} ${leadingZeros(date.getHours(), 2)}:${leadingZeros(date.getMinutes(), 2)}:${leadingZeros(date.getSeconds(), 2)}`
});