const names = {};

export const parseAllUsernameToName = (selector = '.username') => document.querySelectorAll(selector).forEach(async element => {
    const username = element.textContent;
    if (names[username] === undefined) names[username] = fetch('/api/user', {method: 'POST', body: JSON.stringify({
        username: username,
    })}).then(resp => resp.json().then(body => ({status: resp.status, ...body}))).then(body => (Math.floor(body.status / 100) === 2) && (body.type === 'success') ? body.name : username);
    element.textContent = await names[username];
});