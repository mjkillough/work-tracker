'use strict';

// A very simple service worker that displays a notification whenever
// it receives a push event from the server.
this.addEventListener('push', event => {
    const title = 'What time is it?';
    const body = 'It is probably time to go home.';
    event.waitUntil(this.registration.showNotification(title, {body: body}));
});
