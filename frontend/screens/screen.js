/* This is NOT security-critical and is not relied on for security purposes, the script the try-catch block below only checks if the page is opened as a proper iframe for UX purposes */
/* Do be aware that this page could still be opened as an iframe in unintended pages and will then most-likely throw errors all the time due to missing requirements on the parent window */
if (false) /* TODO: Delete this temporary `if (false)` blocker */ try { // This is a try block to catch any error thrown by any expression inside
    if ( // Insert expressions below (separated by `||`) where any `expression == true` throws an error and redirects client to the root path
        window.top === window.self // This checks if this window is the same as the top window, which means it's opened as a standalone page instead of an iframe
        || window.origin !== window.parent.origin // This checks if the origin of this window is not the same as the origin of the parent window
        || window.frameElement === null // This checks if this window if not opened as an iframe
    ) throw null; // This throws an error intentionally to trigger the following `catch` block if any of the above expressions is true
    else console.log(`Iframe: ${window.location.href} is loaded in an iframe inside ${window.parent.location.href}`); // This logs the URL of this window and the parent window and also assures that both pages are same-origin, otherwise throws an error
} catch { // This catches any error thrown above
    try {window.top.location.replace('/');} // This tries to redirect the client away as the top window
    catch {window.location.replace('/');}; // This redirects the client away as this window if the previous one throws an error
};

document.addEventListener('DOMContentLoaded', () => {
    const backButton = document.querySelector('body > main > button#back-button');
    if (window.parent.history.state != null && (window.parent.history.state.index ?? 0) > 0) {
        backButton.addEventListener('click', () => window.parent.history.back());
        backButton.removeAttribute('hidden');
    }
    else backButton.setAttribute('hidden', '');
});

window.addEventListener('load', () => {
    document.documentElement.scrollLeft = 0;
    document.body.scrollLeft = 0;
});