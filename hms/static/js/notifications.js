/**
 * CampusCare Notification System
 * Handles browser push notifications
 */

const CampusCareNotifications = {
    // Check if notifications are supported
    isSupported() {
        return 'Notification' in window && 'serviceWorker' in navigator;
    },

    // Get current permission status
    getPermission() {
        if (!this.isSupported()) return 'unsupported';
        return Notification.permission;
    },

    // Request notification permission
    async requestPermission() {
        if (!this.isSupported()) {
            console.log('[Notifications] Not supported in this browser');
            return false;
        }

        try {
            const permission = await Notification.requestPermission();
            localStorage.setItem('notificationPermission', permission);
            return permission === 'granted';
        } catch (error) {
            console.error('[Notifications] Permission request failed:', error);
            return false;
        }
    },

    // Show a notification
    show(title, options = {}) {
        if (this.getPermission() !== 'granted') {
            console.log('[Notifications] Permission not granted');
            return false;
        }

        const defaultOptions = {
            icon: '/static/img/icon-192.png',
            badge: '/static/img/icon-192.png',
            vibrate: [100, 50, 100],
            requireInteraction: false,
            silent: false
        };

        const notification = new Notification(title, { ...defaultOptions, ...options });

        notification.onclick = function (event) {
            event.preventDefault();
            window.focus();
            notification.close();
            if (options.url) {
                window.location.href = options.url;
            }
        };

        return notification;
    },

    // Show success notification
    success(message, options = {}) {
        return this.show('✅ Success', { body: message, tag: 'success', ...options });
    },

    // Show info notification
    info(message, options = {}) {
        return this.show('ℹ️ CampusCare', { body: message, tag: 'info', ...options });
    },

    // Show warning notification
    warning(message, options = {}) {
        return this.show('⚠️ Attention', { body: message, tag: 'warning', ...options });
    },

    // Show error notification  
    error(message, options = {}) {
        return this.show('❌ Error', { body: message, tag: 'error', ...options });
    },

    // Update notification bell UI
    updateBellUI() {
        const bell = document.getElementById('notification-bell');
        const status = document.getElementById('notification-status');

        if (!bell) return;

        const permission = this.getPermission();

        if (permission === 'granted') {
            bell.classList.add('text-teal-400');
            bell.classList.remove('text-indigo-200');
            if (status) status.textContent = 'Notifications enabled';
        } else if (permission === 'denied') {
            bell.classList.add('text-red-400');
            bell.classList.remove('text-indigo-200');
            if (status) status.textContent = 'Notifications blocked';
        }
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    CampusCareNotifications.updateBellUI();
});

// Export for global use
window.CampusCareNotifications = CampusCareNotifications;
