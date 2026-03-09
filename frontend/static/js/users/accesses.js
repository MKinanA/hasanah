import { getData } from '../utils/data.js';

document.addEventListener('DOMContentLoaded', () => {
    const data = getData();

    document.querySelectorAll('body > div > main > div > label > input[type="checkbox"]').forEach(toggle => toggle.addEventListener('click', (toggle => (async e => {
        document.querySelector(`body > div > main > div > label:has(> input[type="checkbox"][name="${toggle.getAttribute('name')}"])`).classList.add('loading');
        const resp = await fetch(`/api/user/${toggle.checked ? 'grant-access' : 'revoke-access'}`, {method: 'POST', body: JSON.stringify({
            username: data.target_user.username,
            access: toggle.getAttribute('name'),
        })});
        const body = await resp.json();
        if (!(Math.floor(resp.status / 100) === 2) || !(body.type === 'success')) {
            alert(`Error: ${body.message ?? body.detail ?? '?'}`);
            toggle.checked = !toggle.checked;
        };
        document.querySelector(`body > div > main > div > label:has(> input[type="checkbox"][name="${toggle.getAttribute('name')}"])`).classList.remove('loading');
    }))(toggle)));
});