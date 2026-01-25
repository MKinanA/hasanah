import { parseAllTimestamps } from '../utils/datetime.js';
import { parseAllUsernameToName } from '../utils/username.js';
import { getData } from '../utils/data.js';

document.addEventListener('DOMContentLoaded', () => {
    const data = getData();

    parseAllTimestamps();
    parseAllUsernameToName();

    document.querySelector('#delete-button').addEventListener('click', async e => {
        e.preventDefault();
        document.querySelector('#delete-button').classList.add('loading');
        if (!confirm('Hapus pembayaran ini?')) {
            document.querySelector('#delete-button').classList.remove('loading');
            return;
        };
        const resp = await fetch('/api/zis/payment/delete', {method: 'POST', body: JSON.stringify({
            uuid: data.payment.payment,
        })});
        const body = await resp.json();
        if ((Math.floor(resp.status / 100) === 2) && (body.type === 'success')) location.replace('.');
        else {
            alert(body.message ?? body.detail ?? 'Error');
            document.querySelector('#delete-button').classList.remove('loading');
        };
    });
});