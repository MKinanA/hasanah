const screensBank = '#screens-bank',
    inactiveScreens = '#inactive-screens',
    activeScreens = '#active-screens',
    screenClass = '.screen',
    movingInClass = '.moving-in',
    movingOutClass = '.moving-out',
    transitionDurationMilliseconds = 250,
    statePurposes = [
        'change screen',
        'in-screen mechanism',
        'back blocker'
    ],
    appStartedOnScreenIndex = history.state != null ? history.state.screenIndex ?? 0 : 0,
    uncreatedScreenIndexes = [...Array(appStartedOnScreenIndex)].map((_, index) => index),
    screenHandlers = {},
    log = message => console.log(`Hasanah Internal: ${message}`),
    initScreen = 'home';

let started = false,
    currState = {},
    ignorePopState = false;

function main(event) {
    started = true;
    log('Started');
    if (history.state != null ? typeof history.state.screen == 'string' : false) navigate(history.state.screen, undefined, undefined, undefined, false, true);
    else navigate(initScreen, undefined, undefined, undefined, false, true);
};

function generateScreenId() {
    let id;
    do {
        do {
            id = Math.random().toString(36).substring(2);
        } while ('0123456789'.includes(id.charAt(0)));
    } while (document.querySelector(`${screenClass}#${id}`) != null);
    return id;
};

function navigate(screen, data = null, forceNewStack = false, withBackBlocker = false, animate = true, replace = false, manipulateHistory = true, customState = null) {
    log('Function navigate invoked');
    const index = customState != null && customState.index != undefined ? customState.index : (history.state != null ? (history.state.index ?? 0) : 0) + (!replace ? 1 : 0),
        screenIndex = customState != null && customState.screenIndex != undefined ? customState.screenIndex : (history.state != null ? (history.state.screenIndex ?? 0) : 0) + (!replace ? 1 : 0),
        prevStates = customState != null && customState.prevStates != undefined ? customState.prevStates : history.state != null ? history.state.prevStates ?? [] : [];

    uncreatedScreenIndexes.includes(index) && uncreatedScreenIndexes.splice(uncreatedScreenIndexes.findIndex(value => value == index));

    const inactiveScreen = !forceNewStack ? document.querySelector(`${inactiveScreens} > ${screenClass}[data-screen="${screen}"]:last-child`) : null;
    const screenElement = inactiveScreen ?? document.querySelector(`${screensBank} > ${screenClass}[data-screen="${screen}"]`).cloneNode(true);
    if (inactiveScreen == null) document.querySelector(inactiveScreens).innerHTML = null;
    if (screenElement == null) return;

    const id = customState != null && [null, undefined, ''].includes(customState.id) ? customState.id : replace && history.state != null && ![null, undefined, ''].includes(history.state.id) ? history.state.id : (![null, undefined, ''].includes(screenElement.id) ? screenElement.id : generateScreenId());

    history.state != null && !replace && prevStates.push(history.state);
    const state = customState ?? {
        purpose: statePurposes[0],
        screen: customState != null && customState.screen != undefined ? customState.screen : screen,
        id: id,
        index: index,
        screenIndex: screenIndex,
        data: data,
        withBackBlocker: withBackBlocker,
        prevStates: prevStates
    };
    if (inactiveScreen != null && !replace && manipulateHistory) {
        ignorePopState = true;
        history.forward();
    };
    manipulateHistory && (!replace ? history.pushState(state, '') : history.replaceState(state, ''));
    if (manipulateHistory) currState = history.state;

    screenElement.id = id;
    screenElement.classList.add(movingInClass.substring(1));
    log(`replace = ${replace}, ${activeScreens} > ${screenClass}:not(${movingOutClass}) exists = ${document.querySelector(`${activeScreens} > ${screenClass}:not(${movingOutClass})`) != null}, ${activeScreens} children = ${document.querySelector(activeScreens).childElementCount}`);
    if (replace && document.querySelector(`${activeScreens} > ${screenClass}:not(${movingOutClass})`) != null) [...document.querySelectorAll(`${activeScreens} > ${screenClass}:not(${movingOutClass})`)].at(-1).insertAdjacentElement('afterend', screenElement);
    else if (replace && document.querySelector(activeScreens).childElementCount > 0) document.querySelector(`${activeScreens} > *`).insertAdjacentElement('beforebegin', screenElement);
    else document.querySelector(activeScreens).append(screenElement);

    if (!animate) screenElement.classList.remove(movingInClass.substring(1));
    else requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            screenElement.classList.remove(movingInClass.substring(1));
        });
    });

    if (withBackBlocker) blockBack();

    ((screenName, freshScreen) => (freshScreen && typeof screenHandlers[screenName] == 'function') && setTimeout(() => screenHandlers[screenName](state), 0))(screen, inactiveScreen == null);

    log(`Function navigate finished, navigated to ${screen}${withBackBlocker ? ' with back blocker' : ''}`);
};

function blockBack() {
    log('Function blockBack invoked');
    const state = typeof history.state == 'object' ? history.state : false;
    if (!state) {
        log('Current state is unsupported for back blocker');
        return
    };
    state.purpose = statePurposes[2];
    state.index = typeof state.index == 'number' ? state.index + 1 : 1;
    state.withBackBlocker = false;
    history.pushState(state, '');
    currState = state;
    log(`Function blockBack finished, created a back blocker for screen ${history.state.screen}`);
};

function goBackDespiteBackBlocker() {
    if (typeof history.state == 'object' && history.state != null || history.state.purpose == statePurposes[2]) {
        do {
            ignorePopState = true;
            history.back();
        } while (history.state.purpose == statePurposes[2]);
    };
    history.back();
};

function onPopState(event) {
    log('Function onPopState invoked');
    const prevState = currState;
    currState = event.state;

    if (ignorePopState) {
        ignorePopState = false;
        log('popState ignored');
        currState = event.state;
        return;
    };

    if (Math.abs(prevState.index - event.state.index) > 1) {
        ignorePopState = true;
        history.go(prevState.index - event.state.index);
        window.alert('Maaf,\nMohon melakukan navigasi satu-per-satu, jangan lebih dari satu langkah sekaligus.\n\nIni untuk memastikan aplikasi berjalan dengan benar dan bisa menangani navigasi anda dengan baik.\n\nNavigasi yang baru saja anda lakukan telah dibatalkan dan anda belum berpindah halaman atau keadaan.');
        return;
    };

    if (event.state == null) return;

    if ((event.state.index ?? 0) < (prevState.index ?? 0)) {
        if (prevState.purpose == statePurposes[0]) {
            let index = prevState.index, targetElement;
            while (true) {
                targetElement = [...document.querySelectorAll(`${activeScreens} > ${screenClass}:not(${movingOutClass})`)].at(-1) ?? null;
                if (targetElement == null || targetElement.id == event.state.id) break;
                targetElement.classList.add(movingOutClass.substring(1));
                (toMove => setTimeout(() => {
                    document.querySelector(inactiveScreens).append(toMove);
                    toMove.classList.remove(movingOutClass.substring(1));
                }, transitionDurationMilliseconds))(targetElement);
                if (--index < 0) break;
            };
            if (uncreatedScreenIndexes.includes(event.state.index)) {
                if (event.state.purpose == statePurposes[2])
                log(`${event.state.screen} of ${event.state.index}${[null, 'st', 'nd', 'rd'][event.state.index] ?? 'th'} index is not created due to mid-stack reload, creating`);
                navigate(event.state.screen, event.state.data, undefined, undefined, false, true);
            };
        } else if (prevState.purpose == statePurposes[2]) {
            window.confirm('Apakah anda yakin ingin kembali? Perubahan yang anda buat di halaman ini bisa hilang.') ? history.back() : history.forward();
        };
    } else if ((event.state.index ?? 0) > (prevState.index ?? 0)) {
        if (event.state.purpose == statePurposes[0]) {
            navigate(event.state.screen, undefined, undefined, undefined, undefined, true);
            const stateWithBackBlocker = history.state;
            stateWithBackBlocker.withBackBlocker = event.state.withBackBlocker;
            history.replaceState(stateWithBackBlocker, '');
            currState = history.state;
            log(`event.state.withBackBlocker = ${event.state.withBackBlocker}`);
            if (event.state.withBackBlocker) history.forward();
        } else if (event.state.purpose == statePurposes[2]); // Tidak perlu melakukan apa-apa jika state merupakan back blocker, karena state back blocker tidak merubah tampilan
    } else return;

    log('Function onPopState finished');
};

document.addEventListener('DOMContentLoaded', main);
window.addEventListener('popstate', onPopState);

/* class Screen extends HTMLDivElement {
    static observedAttributes = ['id', 'class'];
    constructor() {super()};
    connectedCallback() {
        if ([...document.querySelector(activeScreens).children].includes(this) && ![null, undefined, ''].includes(this.id));
    };
    disconnectedCallback() {
        if (![
            ...document.querySelector(activeScreens).children,
            ...document.querySelector(inactiveScreens).children,
        ].includes(this) || [null, undefined, ''].includes(this.id));
    };
    attributeChangedCallback(name, oldValue, newValue) {};
};
customElements.define('screen', Screen, {'extends': 'div'}); */