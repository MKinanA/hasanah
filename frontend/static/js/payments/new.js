import { parseAllTimestamps } from '../utils/datetime.js';
import { parseAllUsernameToName } from '../utils/username.js';
import { validate } from '../utils/zis-payment.js';
import { getData } from '../utils/data.js';

document.addEventListener('DOMContentLoaded', () => {
    parseAllTimestamps();
    parseAllUsernameToName();

    document.querySelector('#cancel-button').addEventListener('click', () => location.href = '.');

    document.querySelector('body > div > main > form').addEventListener('submit', async e => {
        e.preventDefault();

        const details = {
            payer_name: document.querySelector('form :is(input, textarea, select)[name="payer_name"]:not(.line *)').value.trim(),
            payer_number: document.querySelector('form :is(input, textarea, select)[name="payer_number"]:not(.line *)').value.trim(),
            payer_email: document.querySelector('form :is(input, textarea, select)[name="payer_email"]:not(.line *)').value.trim(),
            payer_address: document.querySelector('form :is(input, textarea, select)[name="payer_address"]:not(.line *)').value.trim(),
            note: document.querySelector('form :is(input, textarea, select)[name="note"]:not(.line *)').value.trim(),
            lines: [...document.querySelectorAll('form .line:has(:is(input, select, textarea):not([disabled])):not(#line-template)')].map(line => {
                const data = {
                    payer_name: line.querySelector(':is(input, textarea, select)[name="line_payer_name"]').value.trim(),
                    category: line.querySelector(':is(input, textarea, select)[name="line_category"]').value.trim(),
                    amount: Number(line.querySelector(':is(input, textarea, select)[name="line_amount"]').value),
                    unit: line.querySelector(':is(input, textarea, select)[name="line_unit"]').value.trim(),
                    note: line.querySelector(':is(input, textarea, select)[name="line_note"]').value.trim(),
                }
                if (data.note === '') delete data.note;
                return data;
            }),
        };
        if (details.payer_number === '') delete details.payer_number;
        if (details.payer_email === '') delete details.payer_email;
        if (details.note === '') delete details.note;

        const checks = validate(details);

        document.querySelectorAll('form :is(input, textarea, select, button):not(#line-template *)').forEach(field => field.setAttribute('disabled', ''));
        if (checks.length <= 0) {
            if (confirm('Anda akan membuat pembayaran baru, simpan?')) {
                const resp = await fetch('/api/zis/payment/create', {method: 'POST', body: JSON.stringify({
                    payment: details,
                })});
                const body = await resp.json();
                if ((Math.floor(resp.status / 100) === 2) && (body.type === 'success')) {
                    location.href = `./${body.uuid}`;
                    return;
                } else alert(body.message ?? body.detail ?? 'Terjadi error.');
            };
        } else alert(checks.map(check => `\n• ${check}`).join('\n'));
        document.querySelectorAll('form :is(input, textarea, select, button):not(#line-template *)').forEach(field => field.removeAttribute('disabled'));
    });
});

window.addLine = (button, event) => {
    const newLine = document.querySelector('#line-template:last-child').cloneNode(true);
    newLine.id = '';
    newLine.querySelectorAll(':is(input, select, textarea)').forEach(field => field.removeAttribute('disabled'));
    button.closest('.line').insertAdjacentElement(event.shiftKey ? 'beforebegin' : 'afterend', newLine);
};

window.removeLine = (button, event) => ((document.querySelectorAll('.line:not(#line-template)').length > 1) && (event.shiftKey || confirm('Hapus baris ini?'))) ? button.closest('.line').remove() : undefined;

window.moveLineUp = button => {
    const line = button.closest('.line');
    const previous = line.previousElementSibling;
    if (previous !== null) previous.insertAdjacentElement('beforebegin', line);
};

window.moveLineDown = button => {
    const line = button.closest('.line');
    const next = line.nextElementSibling;
    if (next !== null && next.id !== 'line-template') next.insertAdjacentElement('afterend', line);
};