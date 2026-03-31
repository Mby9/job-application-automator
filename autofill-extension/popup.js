document.addEventListener('DOMContentLoaded', () => {
    const loginView = document.getElementById('loginView');
    const mainView = document.getElementById('mainView');
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const dashboardBtn = document.getElementById('dashboardBtn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginError = document.getElementById('loginError');
    const userGreeting = document.getElementById('userGreeting');
    const signupLink = document.getElementById('signupLink');

    if (signupLink) {
        signupLink.href = CONFIG.FRONTEND_URL + '/signup';
    }

    const checkAuth = () => {
        chrome.storage.local.get(['token'], (result) => {
            if (result.token) {
                loginView.style.display = 'none';
                mainView.style.display = 'block';
                // Optionally fetch user info to update greeting
                userGreeting.textContent = 'Active & Connected';
            } else {
                loginView.style.display = 'block';
                mainView.style.display = 'none';
            }
        });
    };

    checkAuth();

    // Login logic
    loginBtn.addEventListener('click', () => {
        const username = usernameInput.value;
        const password = passwordInput.value;
        if (!username || !password) return;

        loginBtn.disabled = true;
        loginBtn.textContent = 'Logging in...';
        loginError.style.display = 'none';

        chrome.runtime.sendMessage({ 
            type: "LOGIN", 
            data: { username, password } 
        }, (response) => {
            loginBtn.disabled = false;
            loginBtn.textContent = 'Log In';
            
            // Check for chrome.runtime.lastError first to catch 'port closed' or background crashes
            if (chrome.runtime.lastError) {
                loginError.textContent = "Extension Error: " + chrome.runtime.lastError.message;
                loginError.style.display = 'block';
                return;
            }

            if (response && response.success) {
                checkAuth();
            } else {
                loginError.textContent = (response && response.error) ? response.error : 'Login failed explicitly.';
                loginError.style.display = 'block';
            }
        });
    });

    // Logout logic
    logoutBtn.addEventListener('click', () => {
        chrome.storage.local.remove('token', () => {
            checkAuth();
        });
    });

    // Refresh Mappings
    refreshBtn.addEventListener('click', () => {
        refreshBtn.disabled = true;
        chrome.runtime.sendMessage({ type: "GET_FILL_VALUES" }, (response) => {
            refreshBtn.disabled = false;
            if (response && response.success) {
                alert('Mappings synced successfully!');
            } else {
                alert('Error syncing: ' + (response.error || 'Unknown error'));
            }
        });
    });

    // Open Dashboard
    dashboardBtn.addEventListener('click', () => {
        chrome.tabs.create({ url: CONFIG.FRONTEND_URL });
    });
});

