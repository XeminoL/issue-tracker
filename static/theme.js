// Theme management
class ThemeManager {
    constructor() {
        this.darkModeKey = 'issue-tracker-dark-mode';
        this.init();
    }

    init() {
        const savedTheme = localStorage.getItem(this.darkModeKey);

        if (savedTheme === null) {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.setDarkMode(prefersDark);
        } else {
            this.setDarkMode(savedTheme === 'true');
        }

        this.setupToggle();
    }

    setDarkMode(isDark) {
        if (isDark) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem(this.darkModeKey, 'true');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem(this.darkModeKey, 'false');
        }
    }

    toggle() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        this.setDarkMode(!isDark);
        this.updateToggleButton();
    }

    setupToggle() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
            this.updateToggleButton();
        }
    }

    updateToggleButton() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            toggleBtn.textContent = isDark ? '☀️' : '🌙';
        }
    }

    isDarkMode() {
        return document.documentElement.getAttribute('data-theme') === 'dark';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
});
