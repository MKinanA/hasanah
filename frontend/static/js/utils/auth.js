export const allowedUsernameCharacters = new Set('abcdefghijklmnopqrstuvwxyz0123456789_.-');

export function checkUsername(value) {
    let checks = [];
    if (!(typeof value === 'string')) checks.push('Username harus berupa string.');
    if (!(1 <= value.length)) checks.push('Panjang username minimal 1 karakter.');
    if (!(value.length <= 64)) checks.push('Panjang username maksimal 64 karakter.');
    if (![...value].every(char => allowedUsernameCharacters.has(char))) checks.push('Username hanya boleh berisi huruf, angka, dan beberapa karakter khusus (_.-\').');
    return checks;
};

export function checkPassword(value) {
    let checks = [];
    if (!(typeof value === 'string')) checks.push('Password harus berupa string.');
    if (!(8 <= value.length)) checks.push('Panjang password minimal 8 karakter.');
    if (!(value.length <= 64)) checks.push('Panjang password maksimal 64 karakter.');
    return checks;
};

export function storeToken(token) {
    localStorage.setItem('token', token);
    let hostname = '';
    location.hostname.split('.').reverse().forEach(part => {
        hostname = [part, ...hostname.split('.').filter(x => x !== '')].join('.');
        document.cookie = `token=${token}; max-age=3155760000; path=/; domain=${hostname}`;
    });
};

export const setVisibilityToggles = (selector) => document.querySelectorAll(selector).forEach(toggle => {
    toggle.addEventListener('click', (toggle => e => {
        e.preventDefault();
        if (toggle.querySelector('svg.eye-crossed').hasAttribute('hidden')) {
            toggle.querySelector('svg.eye').setAttribute('hidden', '');
            toggle.querySelector('svg.eye-crossed').removeAttribute('hidden');
            toggle.parentElement.parentElement.querySelector('input').setAttribute('type', 'text');
        } else {
            toggle.querySelector('svg.eye-crossed').setAttribute('hidden', '');
            toggle.querySelector('svg.eye').removeAttribute('hidden');
            toggle.parentElement.parentElement.querySelector('input').setAttribute('type', 'password');
        };
    })(toggle));
    requestAnimationFrame(() => toggle.click());
});