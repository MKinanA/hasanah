import { getData } from '../utils/data.js';

document.addEventListener('DOMContentLoaded', () => {
    const data = getData(),
        nameEditButton = document.querySelector('body > div > main > h2:first-of-type:has(+ p) > #name-edit-button');

    nameEditButton.addEventListener('click', async e => {
        nameEditButton.classList.add('loading');
        const newName = prompt('Masukkan nama baru:');
        if (newName !== null) {
            const resp = await fetch(`/api/user/update-name`, {method: 'POST', body: JSON.stringify({
                username: data.target_user.username,
                new_name: newName,
            })});
            const body = await resp.json();
            if ((Math.floor(resp.status / 100) === 2) && (body.type === 'success')) location.reload();
            else alert(`Error: ${body.message ?? body.detail ?? '?'}`);
        }
        nameEditButton.classList.remove('loading');
    });
});