class Auth {
    static currentUser = null;
    
    static init() {
        const savedUser = localStorage.getItem(CONFIG.STORAGE_KEYS.USER);
        if (savedUser) {
            this.currentUser = JSON.parse(savedUser);
            this.updateUI();
        }
        
        this.setupEventListeners();
    }
    
    static setupEventListeners() {
        document.querySelectorAll('[data-auth-tab]').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(e.target.dataset.authTab);
            });
        });
        
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });
        
        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.register();
        });
        
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
    }
    
    static switchTab(tab) {
        document.querySelectorAll('[data-auth-tab]').forEach(t => {
            t.classList.toggle('active', t.dataset.authTab === tab);
        });
        
        document.getElementById('loginForm').classList.toggle('d-none', tab !== 'login');
        document.getElementById('registerForm').classList.toggle('d-none', tab !== 'register');
        document.getElementById('authModalTitle').textContent = tab === 'login' ? 'Login' : 'Register';
        
        this.clearMessages();
    }
    
    static async login() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        this.clearMessages();
        
        try {
            const response = await API.auth.login(email, password);
            this.currentUser = response.user;
            localStorage.setItem(CONFIG.STORAGE_KEYS.USER, JSON.stringify(this.currentUser));
            
            this.showSuccess('Login successful!');
            this.updateUI();
            
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('authModal')).hide();
                document.getElementById('loginForm').reset();
            }, 1000);
            
        } catch (error) {
            this.showError(error.message);
        }
    }
    
    static async register() {
        const name = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        
        this.clearMessages();
        
        try {
            const response = await API.auth.register(name, email, password);
            
            this.showSuccess('Registration successful! Please login.');
            
            setTimeout(() => {
                this.switchTab('login');
                document.getElementById('registerForm').reset();
                document.getElementById('loginEmail').value = email;
            }, 1500);
            
        } catch (error) {
            this.showError(error.message);
        }
    }
    
    static logout() {
        this.currentUser = null;
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
        this.updateUI();
        
        if (App.currentPage === 'scheduler') {
            App.showPage('dashboard');
        }
    }
    
    static updateUI() {
        const loginBtn = document.getElementById('loginBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const userGreeting = document.getElementById('userGreeting');
        
        if (this.currentUser) {
            loginBtn.classList.add('d-none');
            logoutBtn.classList.remove('d-none');
            userGreeting.classList.remove('d-none');
            userGreeting.textContent = `Hello, ${this.currentUser.name}`;
        } else {
            loginBtn.classList.remove('d-none');
            logoutBtn.classList.add('d-none');
            userGreeting.classList.add('d-none');
        }
    }
    
    static showError(message) {
        const errorEl = document.getElementById('authError');
        errorEl.textContent = message;
        errorEl.classList.remove('d-none');
    }
    
    static showSuccess(message) {
        const successEl = document.getElementById('authSuccess');
        successEl.textContent = message;
        successEl.classList.remove('d-none');
    }
    
    static clearMessages() {
        document.getElementById('authError').classList.add('d-none');
        document.getElementById('authSuccess').classList.add('d-none');
    }
    
    static isLoggedIn() {
        return this.currentUser !== null;
    }
    
    static getUserId() {
        return this.currentUser?.id;
    }
    
    static requireAuth() {
        if (!this.isLoggedIn()) {
            const modal = new bootstrap.Modal(document.getElementById('authModal'));
            modal.show();
            return false;
        }
        return true;
    }
}
