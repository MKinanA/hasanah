import { storeToken } from './utils/auth.js';

storeToken(localStorage.getItem('token'));

document.addEventListener('DOMContentLoaded', () => document.querySelectorAll('a:is([href="/logout"], [href="/logout/"])').forEach(element => element.addEventListener('click', e => confirm('Logout dari user anda saat ini? Anda akan harus login kembali.') ? true : e.preventDefault())));