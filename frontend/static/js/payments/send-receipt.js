import { getData } from '../utils/data.js';

document.addEventListener('DOMContentLoaded', () => {
    const data = getData();
    const viaTarget = {
        wa: data.payment.payer_number,
        email: data.payment.payer_email,
    }

    document.querySelectorAll('button.send-button').forEach(button => button.addEventListener('click', (button => (async e => {
        e.preventDefault();
        button.classList.add('loading');
        if (!confirm(`Kirim via ${button.textContent} ke ${viaTarget[button.dataset.via]}?`)) {
            button.classList.remove('loading');
            return;
        };
        const resp = await fetch('/api/zis/payment/send-receipt', {method: 'POST', body: JSON.stringify({
            uuid: data.payment.payment,
            via: button.dataset.via,
        })});
        const body = await resp.json();
        if ((Math.floor(resp.status / 100) === 2) && (body.type === 'success')) alert('Tanda terima sudah dikirim, silahkan pastikan pesan sudah masuk ke penerima.');
        else alert(`Error: ${body.message ?? body.detail ?? '?'}`);
        button.classList.remove('loading');
    }))(button)));
});