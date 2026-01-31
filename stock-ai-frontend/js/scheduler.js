class Scheduler {
    static schedulers = [];
    static nextRuns = {};
    
    static init() {
        this.render();
        if (Auth.isLoggedIn()) {
            this.loadSchedulers();
        }
    }
    
    static render() {
        const container = document.getElementById('scheduler-page');
        const isLoggedIn = Auth.isLoggedIn();
        
        container.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="mb-3"><i class="bi bi-clock me-2"></i>Alert Scheduler</h2>
                    <p class="text-muted">Set up automated stock alerts for morning pre-market and evening post-market updates</p>
                </div>
            </div>
            
            ${!isLoggedIn ? `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Please <a href="#" data-bs-toggle="modal" data-bs-target="#authModal">login or register</a> to create and manage scheduled alerts.
                </div>
            ` : ''}
            
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-info-circle me-2"></i>Schedule Info
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <strong><i class="bi bi-sunrise me-2 text-warning"></i>Morning Alert</strong>
                                <p class="text-muted small mb-0">Sent at 8:30 AM (1 hour before market open)</p>
                            </div>
                            <div>
                                <strong><i class="bi bi-sunset me-2 text-info"></i>Evening Alert</strong>
                                <p class="text-muted small mb-0">Sent at 5:00 PM (after market close)</p>
                            </div>
                            <hr>
                            <div id="nextRunsInfo">
                                <small class="text-muted">Loading next run times...</small>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-plus-circle me-2"></i>Create New Alert
                        </div>
                        <div class="card-body">
                            <form id="createSchedulerForm">
                                <div class="mb-3">
                                    <label class="form-label">Trigger Time</label>
                                    <div class="btn-group w-100" role="group">
                                        <input type="radio" class="btn-check" name="triggerTime" id="triggerMorning" value="morning" checked ${!isLoggedIn ? 'disabled' : ''}>
                                        <label class="btn btn-outline-warning" for="triggerMorning">
                                            <i class="bi bi-sunrise me-1"></i>Morning
                                        </label>
                                        <input type="radio" class="btn-check" name="triggerTime" id="triggerEvening" value="evening" ${!isLoggedIn ? 'disabled' : ''}>
                                        <label class="btn btn-outline-info" for="triggerEvening">
                                            <i class="bi bi-sunset me-1"></i>Evening
                                        </label>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Symbols (optional)</label>
                                    <input type="text" class="form-control" id="schedulerSymbols" 
                                        placeholder="e.g., AAPL, MSFT, GOOGL (comma separated)" ${!isLoggedIn ? 'disabled' : ''}>
                                    <small class="text-muted">Leave empty for general market summary</small>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Custom Prompt</label>
                                    <textarea class="form-control" id="schedulerPrompt" rows="3" 
                                        placeholder="e.g., Focus on tech stocks and provide buy/sell recommendations" ${!isLoggedIn ? 'disabled' : ''}></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary w-100" ${!isLoggedIn ? 'disabled' : ''}>
                                    <i class="bi bi-plus-circle me-2"></i>Create Alert
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span><i class="bi bi-list-check me-2"></i>Your Scheduled Alerts</span>
                            <button class="btn btn-sm btn-light" id="refreshSchedulersBtn" ${!isLoggedIn ? 'disabled' : ''}>
                                <i class="bi bi-arrow-clockwise"></i>
                            </button>
                        </div>
                        <div class="card-body" id="schedulersContainer">
                            ${!isLoggedIn ? `
                                <div class="empty-state">
                                    <i class="bi bi-lock"></i>
                                    <p>Login to view your scheduled alerts</p>
                                </div>
                            ` : `
                                <div class="text-center p-4">
                                    <div class="spinner-border text-primary" role="status"></div>
                                </div>
                            `}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
        this.loadNextRuns();
    }
    
    static setupEventListeners() {
        document.getElementById('createSchedulerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            if (Auth.requireAuth()) {
                this.createScheduler();
            }
        });
        
        document.getElementById('refreshSchedulersBtn').addEventListener('click', () => {
            if (Auth.isLoggedIn()) {
                this.loadSchedulers();
            }
        });
    }
    
    static async loadNextRuns() {
        try {
            this.nextRuns = await API.scheduler.getNextRuns();
            const container = document.getElementById('nextRunsInfo');
            container.innerHTML = `
                <div class="mb-2">
                    <small class="text-warning"><i class="bi bi-sunrise me-1"></i>Next Morning:</small>
                    <small class="d-block">${new Date(this.nextRuns.morning).toLocaleString()}</small>
                </div>
                <div>
                    <small class="text-info"><i class="bi bi-sunset me-1"></i>Next Evening:</small>
                    <small class="d-block">${new Date(this.nextRuns.evening).toLocaleString()}</small>
                </div>
            `;
        } catch (error) {
            console.error('Failed to load next runs:', error);
        }
    }
    
    static async loadSchedulers() {
        if (!Auth.isLoggedIn()) return;
        
        const container = document.getElementById('schedulersContainer');
        container.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary" role="status"></div>
            </div>
        `;
        
        try {
            const response = await API.scheduler.getUserSchedulers(Auth.getUserId());
            this.schedulers = response.schedulers || [];
            this.renderSchedulers();
        } catch (error) {
            console.error('Failed to load schedulers:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Failed to load schedulers: ${error.message}
                </div>
            `;
        }
    }
    
    static renderSchedulers() {
        const container = document.getElementById('schedulersContainer');
        
        if (this.schedulers.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-calendar-x"></i>
                    <p>No scheduled alerts yet</p>
                    <small class="text-muted">Create your first alert using the form above</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div class="row g-3">
                ${this.schedulers.map(scheduler => `
                    <div class="col-md-6">
                        <div class="card scheduler-card ${scheduler.trigger_time}">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <span class="trigger-badge badge ${scheduler.trigger_time === 'morning' ? 'bg-warning' : 'bg-info'}">
                                        <i class="bi bi-${scheduler.trigger_time === 'morning' ? 'sunrise' : 'sunset'} me-1"></i>
                                        ${scheduler.trigger_time.charAt(0).toUpperCase() + scheduler.trigger_time.slice(1)}
                                    </span>
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" 
                                            id="toggle-${scheduler.id}" 
                                            ${scheduler.is_active ? 'checked' : ''}
                                            onchange="Scheduler.toggleScheduler('${scheduler.id}', this.checked)">
                                        <label class="form-check-label small" for="toggle-${scheduler.id}">
                                            ${scheduler.is_active ? 'Active' : 'Paused'}
                                        </label>
                                    </div>
                                </div>
                                
                                ${scheduler.symbols && scheduler.symbols.length > 0 ? `
                                    <div class="mb-2">
                                        ${scheduler.symbols.map(s => `<span class="badge bg-secondary me-1">${s}</span>`).join('')}
                                    </div>
                                ` : '<div class="mb-2"><span class="badge bg-light text-dark">General Market</span></div>'}
                                
                                <p class="small text-muted mb-2">${scheduler.prompt || 'No custom prompt'}</p>
                                
                                <div class="small text-muted mb-2">
                                    <i class="bi bi-clock me-1"></i>
                                    Next run: ${scheduler.next_run ? new Date(scheduler.next_run).toLocaleString() : 'N/A'}
                                </div>
                                
                                <div class="btn-group btn-group-sm w-100">
                                    <button class="btn btn-outline-primary" onclick="Scheduler.testScheduler('${scheduler.id}')">
                                        <i class="bi bi-play me-1"></i>Test
                                    </button>
                                    <button class="btn btn-outline-danger" onclick="Scheduler.deleteScheduler('${scheduler.id}')">
                                        <i class="bi bi-trash me-1"></i>Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    static async createScheduler() {
        const triggerTime = document.querySelector('input[name="triggerTime"]:checked').value;
        const symbolsInput = document.getElementById('schedulerSymbols').value;
        const prompt = document.getElementById('schedulerPrompt').value;
        
        const symbols = symbolsInput
            .split(',')
            .map(s => s.trim().toUpperCase())
            .filter(s => s.length > 0);
        
        try {
            await API.scheduler.create({
                user_id: Auth.getUserId(),
                trigger_time: triggerTime,
                symbols: symbols,
                prompt: prompt || 'Provide a comprehensive market analysis',
                is_active: true
            });
            
            document.getElementById('schedulerSymbols').value = '';
            document.getElementById('schedulerPrompt').value = '';
            
            this.showToast('Alert created successfully!', 'success');
            this.loadSchedulers();
        } catch (error) {
            this.showToast(`Failed to create alert: ${error.message}`, 'danger');
        }
    }
    
    static async toggleScheduler(id, isActive) {
        try {
            await API.scheduler.update(id, { is_active: isActive });
            this.showToast(`Alert ${isActive ? 'activated' : 'paused'}`, 'success');
            this.loadSchedulers();
        } catch (error) {
            this.showToast(`Failed to update alert: ${error.message}`, 'danger');
            this.loadSchedulers();
        }
    }
    
    static async deleteScheduler(id) {
        if (!confirm('Are you sure you want to delete this alert?')) return;
        
        try {
            await API.scheduler.delete(id);
            this.showToast('Alert deleted', 'success');
            this.loadSchedulers();
        } catch (error) {
            this.showToast(`Failed to delete alert: ${error.message}`, 'danger');
        }
    }
    
    static async testScheduler(id) {
        this.showToast('Running test alert...', 'info');
        
        try {
            const result = await API.scheduler.test(id);
            if (result.email_sent) {
                this.showToast('Test alert sent to your email!', 'success');
            } else {
                this.showToast('Test completed but email not configured', 'warning');
            }
        } catch (error) {
            this.showToast(`Test failed: ${error.message}`, 'danger');
        }
    }
    
    static showToast(message, type = 'info') {
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
        toast.show();
        
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
}
