class Dashboard {
    static refreshInterval = null;
    
    static async init() {
        this.render();
        await this.loadData();
        this.startAutoRefresh();
    }
    
    static render() {
        const container = document.getElementById('dashboard-page');
        container.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="mb-3"><i class="bi bi-speedometer2 me-2"></i>Market Dashboard</h2>
                    <p class="text-muted">Real-time market overview and AI-powered insights</p>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span><i class="bi bi-bar-chart me-2"></i>Major Indices</span>
                            <small id="lastUpdated" class="text-light opacity-75"></small>
                        </div>
                        <div class="card-body">
                            <div id="indicesContainer" class="row g-3">
                                <div class="col-12 text-center">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header">
                            <i class="bi bi-graph-up-arrow me-2"></i>Top Gainers
                        </div>
                        <div class="card-body p-0">
                            <div id="gainersContainer">
                                <div class="text-center p-4">
                                    <div class="spinner-border text-primary" role="status"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header bg-danger">
                            <i class="bi bi-graph-down-arrow me-2"></i>Top Losers
                        </div>
                        <div class="card-body p-0">
                            <div id="losersContainer">
                                <div class="text-center p-4">
                                    <div class="spinner-border text-primary" role="status"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span><i class="bi bi-robot me-2"></i>AI Market Summary</span>
                            <button class="btn btn-sm btn-light" id="refreshAISummary">
                                <i class="bi bi-arrow-clockwise"></i> Refresh
                            </button>
                        </div>
                        <div class="card-body">
                            <div id="aiSummaryContainer">
                                <div class="text-center p-4">
                                    <div class="spinner-border text-primary" role="status"></div>
                                    <p class="mt-2 text-muted">Generating AI market analysis...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('refreshAISummary').addEventListener('click', () => {
            this.loadAISummary();
        });
    }
    
    static async loadData() {
        await Promise.all([
            this.loadMarketSummary(),
            this.loadAISummary()
        ]);
    }
    
    static async loadMarketSummary() {
        try {
            const data = await API.market.getSummary();
            this.renderIndices(data.major_indices);
            this.renderMovers(data.top_gainers, 'gainersContainer');
            this.renderMovers(data.top_losers, 'losersContainer', true);
            
            document.getElementById('lastUpdated').textContent = 
                `Updated: ${new Date(data.last_updated).toLocaleTimeString()}`;
        } catch (error) {
            console.error('Failed to load market summary:', error);
            document.getElementById('indicesContainer').innerHTML = `
                <div class="col-12 text-center text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>Failed to load market data
                </div>
            `;
        }
    }
    
    static renderIndices(indices) {
        const container = document.getElementById('indicesContainer');
        
        if (!indices || indices.length === 0) {
            container.innerHTML = '<div class="col-12 text-center text-muted">No index data available</div>';
            return;
        }
        
        container.innerHTML = indices.map(index => `
            <div class="col-md-3 col-sm-6">
                <div class="card index-card">
                    <div class="name text-muted small">${index.name}</div>
                    <div class="price">${this.formatNumber(index.price)}</div>
                    <div class="change ${index.change >= 0 ? 'positive' : 'negative'}">
                        <i class="bi bi-${index.change >= 0 ? 'caret-up-fill' : 'caret-down-fill'}"></i>
                        ${index.change >= 0 ? '+' : ''}${index.change.toFixed(2)} (${index.change_percent >= 0 ? '+' : ''}${index.change_percent.toFixed(2)}%)
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    static renderMovers(movers, containerId, isLosers = false) {
        const container = document.getElementById(containerId);
        
        if (!movers || movers.length === 0) {
            container.innerHTML = '<div class="text-center text-muted p-4">No data available</div>';
            return;
        }
        
        container.innerHTML = `
            <table class="table table-hover stock-table mb-0">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>Change</th>
                    </tr>
                </thead>
                <tbody>
                    ${movers.map(stock => `
                        <tr class="stock-row" data-symbol="${stock.symbol}" style="cursor: pointer;">
                            <td>
                                <strong>${stock.symbol}</strong>
                                <div class="small text-muted">${stock.name || ''}</div>
                            </td>
                            <td>$${stock.price.toFixed(2)}</td>
                            <td class="${stock.change >= 0 ? 'positive' : 'negative'}">
                                ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}
                                <div class="small">(${stock.change_percent >= 0 ? '+' : ''}${stock.change_percent.toFixed(2)}%)</div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        container.querySelectorAll('.stock-row').forEach(row => {
            row.addEventListener('click', () => {
                const symbol = row.dataset.symbol;
                Explorer.showStockDetail(symbol);
                App.showPage('explorer');
            });
        });
    }
    
    static async loadAISummary() {
        const container = document.getElementById('aiSummaryContainer');
        container.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2 text-muted">Generating AI market analysis...</p>
            </div>
        `;
        
        try {
            const data = await API.market.getAISummary();
            container.innerHTML = `
                <div class="markdown-content">
                    ${this.formatMarkdown(data.summary)}
                </div>
            `;
        } catch (error) {
            console.error('Failed to load AI summary:', error);
            container.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Unable to generate AI summary. Please ensure the OpenAI API key is configured.
                </div>
            `;
        }
    }
    
    static formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(2) + 'M';
        } else if (num >= 1000) {
            return num.toLocaleString();
        }
        return num.toFixed(2);
    }
    
    static formatMarkdown(text) {
        if (!text) return '';
        
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^### (.*$)/gm, '<h5>$1</h5>')
            .replace(/^## (.*$)/gm, '<h4>$1</h4>')
            .replace(/^# (.*$)/gm, '<h3>$1</h3>')
            .replace(/^\- (.*$)/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
    }
    
    static startAutoRefresh() {
        this.stopAutoRefresh();
        this.refreshInterval = setInterval(() => {
            this.loadMarketSummary();
        }, CONFIG.REFRESH_INTERVALS.MARKET_SUMMARY);
    }
    
    static stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    static destroy() {
        this.stopAutoRefresh();
    }
}
