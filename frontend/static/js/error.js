import {} from './utils/auth.js';
import { delay } from './utils/async.js';

document.addEventListener('DOMContentLoaded', async () => {
    const timer = document.querySelector('body > div > main > p > span');
    for (let i = parseInt(timer.textContent) || 10; i >= 0; i--) {
        timer.textContent = i;
        await delay(1000);
    };
    setTimeout(() => location.replace('/'), 1000);
    history.back();
});