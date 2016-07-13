'use strict';


class NotificationManager {

    constructor(serviceWorkerUrl) {
        this.serviceWorkerUrl = serviceWorkerUrl;
        this._installServiceWorker();
    }

    // Installs our service worker and puts a promise for
    // the service worker on the object, for use by other methods.
    _installServiceWorker() {
        this.serviceWorkerPromise = navigator.serviceWorker
            .register(this.serviceWorkerUrl)
            .catch(error => {
                console.log('serviceWorker.register() returned error: ', error)
            });
    }

    // Returns a Promise that resolves to the current subscription, or null.
    get subscription() {
        if (Notification.permission !== 'granted') {
            return Promise.resolve(null);
        }

        return this.serviceWorkerPromise.then(serviceWorker => {
            return serviceWorker.pushManager.getSubscription()
                .catch(error => {
                    // Errors are common when we're not subscribed, so
                    // don't bother logging.
                    return null;
                });
        });
    }

    // Returns a Promise that resolves to a PushSubscription.
    subscribe() {
        return this.serviceWorkerPromise.then(serviceWorker => {
            return serviceWorker.pushManager.subscribe({userVisibleOnly: true})
                .catch(error => {
                    console.log('pushManager.subscribe() gave error:', error);
                    throw error;
                });
        });
    }

    // Returning a Promise that resolves when our attempt to unsubscribe
    // completes. Does not communicate failure to caller.
    unsubscribe() {
        return this.subscription.then(subscription => {
                return subscription.unsubscribe()
                    .then(success => {
                        if (!success) {
                            console.log('PushSubscription.unsubscribe() returned failure');
                        }
                    }).catch(error => {
                        console.log('PushSubscription.unsubscribe() gave error: ', error);
                    });
            }).catch(error => {
                console.log('pushManager.getSubscrition() gave error: ', error);
            });
    }

}
