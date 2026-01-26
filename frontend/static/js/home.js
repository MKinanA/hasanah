const currHour = new Date().getHours();

document.addEventListener('DOMContentLoaded', () => document.querySelector('body > div > main > h1').textContent = document.querySelector('body > div > main > h1').textContent.replace('pagi', currHour >= 19 ? 'malam' : currHour >= 15 ? 'sore' : currHour >= 11 ? 'siang' : 'pagi'));