const currHour = new Date().getHours();

document.addEventListener('DOMContentLoaded', () => document.querySelector('body > div > main > h1').textContent = document.querySelector('body > div > main > h1').textContent.replace('pagi', currHour >= 11 ? 'siang' : currHour >= 15 ? 'sore' : currHour >= 19 ? 'malam' : 'pagi'));