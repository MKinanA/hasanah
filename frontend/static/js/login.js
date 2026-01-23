import { checkUsername, checkPassword, storeToken, setVisibilityToggles, turnOffVisibilityToggles } from './utils/auth.js';

document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('body > form').addEventListener('submit', async e => {
        e.preventDefault();
        if (!document.querySelector('body > form > fieldset').hasAttribute('disabled')) {
            document.querySelector('body > form > fieldset').setAttribute('disabled', '');
            turnOffVisibilityToggles('body > form > fieldset > label > div > .visibility-toggle');
            const username = document.querySelector('body > form > fieldset > label > input[name="username"]').value;
            const password = document.querySelector('body > form > fieldset > label > input[name="password"]').value;
            const checks = [...checkUsername(username), ...checkPassword(password)];
            if (checks.length <= 0) {
                const resp = await fetch('/api/auth/login', {method: 'POST', body: JSON.stringify({
                    username: username,
                    password: password,
                })});
                const body = await resp.json();
                if ((Math.floor(resp.status / 100) === 2) && (body.type === 'success')) {
                    storeToken(body.token);
                    location.replace('/home');
                    return;
                } else alert(body.message ?? body.detail ?? 'Username atau password salah.');
            } else alert(checks.map(check => `\n• ${check}`).join('\n'));
            document.querySelector('body > form > fieldset').removeAttribute('disabled');
        };
    });

    setVisibilityToggles('body > form > fieldset > label > div > .visibility-toggle');
});