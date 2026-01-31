class App {
    static currentPage = 'dashboard';
    
    static init() {
        Auth.init();
        
        this.setupNavigation();
        
        this.showPage('dashboard');
    }
    
    static setupNavigation() {
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.closest('[data-page]').dataset.page;
                this.showPage(page);
            });
        });
    }
    
    static showPage(page) {
        document.querySelectorAll('.page-content').forEach(p => {
            p.classList.add('d-none');
        });
        
        document.querySelectorAll('[data-page]').forEach(link => {
            link.classList.remove('active');
        });
        
        const pageElement = document.getElementById(`${page}-page`);
        if (pageElement) {
            pageElement.classList.remove('d-none');
        }
        
        const navLink = document.querySelector(`[data-page="${page}"]`);
        if (navLink) {
            navLink.classList.add('active');
        }
        
        this.currentPage = page;
        
        switch (page) {
            case 'dashboard':
                Dashboard.init();
                break;
            case 'chat':
                Chat.init();
                break;
            case 'explorer':
                Explorer.init();
                break;
            case 'scheduler':
                Scheduler.init();
                break;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
