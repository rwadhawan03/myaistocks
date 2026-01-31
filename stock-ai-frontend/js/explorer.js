class Explorer {
    static currentSymbol = null;
    static priceChart = null;
    
    static init() {
        this.render();
        this.setupEventListeners();
    }
    
    static render() {
        const container = document.getElementById('explorer-page');
        container.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="mb-3"><i class="bi bi-search me-2"></i>Market Explorer</h2>
                    <p class="text-muted">Search and analyze stocks, ETFs, and funds</p>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="search-container">
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-search"></i></span>
                            <input type="text" class="form-control form-control-lg" id="stockSearchInput" 
                                placeholder="Search by symbol (e.g., AAPL, MSFT, SPY)">
                            <button class="btn btn-primary" type="button" id="searchBtn">Search</button>
                        </div>
                        <div id="searchResults" class="search-results d-none"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="d-flex gap-2 flex-wrap">
                        <span class="text-muted align-self-center">Quick access:</span>
                        <button class="btn btn-outline-secondary btn-sm quick-symbol" data-symbol="AAPL">AAPL</button>
                        <button class="btn btn-outline-secondary btn-sm quick-symbol" data-symbol="MSFT">MSFT</button>
                        <button class="btn btn-outline-secondary btn-sm quick-symbol" data-symbol="GOOGL">GOOGL</button>
                        <button class="btn btn-outline-secondary btn-sm quick-symbol" data-symbol="NVDA">NVDA</button>
                        <button class="btn btn-outline-secondary btn-sm quick-symbol" data-symbol="SPY">SPY</button>
                        <button class="btn btn-outline-secondary btn-sm quick-symbol" data-symbol="QQQ">QQQ</button>
                    </div>
                </div>
            </div>
            
            <div id="stockDetailContainer" class="d-none">
            </div>
            
            <div id="defaultView">
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <i class="bi bi-graph-up me-2"></i>Top Stocks
                            </div>
                            <div class="card-body p-0">
                                <div id="topStocksContainer">
                                    <div class="text-center p-4">
                                        <div class="spinner-border text-primary" role="status"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <i class="bi bi-pie-chart me-2"></i>Top ETFs
                            </div>
                            <div class="card-body p-0">
                                <div id="topETFsContainer">
                                    <div class="text-center p-4">
                                        <div class="spinner-border text-primary" role="status"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.loadDefaultView();
    }
    
    static setupEventListeners() {
        const searchInput = document.getElementById('stockSearchInput');
        const searchBtn = document.getElementById('searchBtn');
        
        searchBtn.addEventListener('click', () => {
            const symbol = searchInput.value.trim().toUpperCase();
            if (symbol) this.showStockDetail(symbol);
        });
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const symbol = searchInput.value.trim().toUpperCase();
                if (symbol) this.showStockDetail(symbol);
            }
        });
        
        document.querySelectorAll('.quick-symbol').forEach(btn => {
            btn.addEventListener('click', () => {
                this.showStockDetail(btn.dataset.symbol);
            });
        });
    }
    
    static async loadDefaultView() {
        try {
            const [stockMovers, etfMovers] = await Promise.all([
                API.market.getMovers('stocks', 10),
                API.market.getMovers('etf', 10)
            ]);
            
            this.renderMoversList(stockMovers.gainers || [], 'topStocksContainer');
            this.renderMoversList(etfMovers.gainers || [], 'topETFsContainer');
        } catch (error) {
            console.error('Failed to load default view:', error);
        }
    }
    
    static renderMoversList(movers, containerId) {
        const container = document.getElementById(containerId);
        
        if (!movers || movers.length === 0) {
            container.innerHTML = '<div class="text-center text-muted p-4">No data available</div>';
            return;
        }
        
        container.innerHTML = `
            <div class="list-group list-group-flush">
                ${movers.map(stock => `
                    <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center stock-item" 
                         data-symbol="${stock.symbol}" style="cursor: pointer;">
                        <div>
                            <strong>${stock.symbol}</strong>
                            <div class="small text-muted">${stock.name || ''}</div>
                        </div>
                        <div class="text-end">
                            <div>$${stock.price.toFixed(2)}</div>
                            <div class="small ${stock.change_percent >= 0 ? 'positive' : 'negative'}">
                                ${stock.change_percent >= 0 ? '+' : ''}${stock.change_percent.toFixed(2)}%
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.querySelectorAll('.stock-item').forEach(item => {
            item.addEventListener('click', () => {
                this.showStockDetail(item.dataset.symbol);
            });
        });
    }
    
    static async showStockDetail(symbol) {
        this.currentSymbol = symbol;
        document.getElementById('stockSearchInput').value = symbol;
        document.getElementById('defaultView').classList.add('d-none');
        document.getElementById('stockDetailContainer').classList.remove('d-none');
        
        const container = document.getElementById('stockDetailContainer');
        container.innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2">Loading ${symbol} data...</p>
            </div>
        `;
        
        try {
            const [info, history, technicals, news] = await Promise.all([
                API.stocks.getInfo(symbol),
                API.stocks.getHistory(symbol, '3mo', '1d'),
                API.stocks.getTechnicals(symbol),
                API.stocks.getNews(symbol)
            ]);
            
            this.renderStockDetail(info, history, technicals, news);
        } catch (error) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Failed to load data for ${symbol}: ${error.message}
                </div>
                <button class="btn btn-primary" onclick="Explorer.backToDefault()">
                    <i class="bi bi-arrow-left me-2"></i>Back to Explorer
                </button>
            `;
        }
    }
    
    static renderStockDetail(info, history, technicals, news) {
        const container = document.getElementById('stockDetailContainer');
        const change = info.current_price - info.previous_close;
        const changePercent = (change / info.previous_close) * 100;
        
        container.innerHTML = `
            <button class="btn btn-outline-secondary mb-3" onclick="Explorer.backToDefault()">
                <i class="bi bi-arrow-left me-2"></i>Back to Explorer
            </button>
            
            <div class="stock-detail-header">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <h2>${info.symbol} - ${info.name}</h2>
                        <p class="mb-0 opacity-75">${info.sector} | ${info.industry}</p>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <div class="price">$${info.current_price?.toFixed(2) || 'N/A'}</div>
                        <div class="${change >= 0 ? 'positive' : 'negative'}">
                            <i class="bi bi-${change >= 0 ? 'caret-up-fill' : 'caret-down-fill'}"></i>
                            ${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span><i class="bi bi-graph-up me-2"></i>Price Chart</span>
                            <div class="btn-group btn-group-sm" id="periodSelector">
                                <button class="btn btn-outline-primary" data-period="1mo">1M</button>
                                <button class="btn btn-outline-primary active" data-period="3mo">3M</button>
                                <button class="btn btn-outline-primary" data-period="6mo">6M</button>
                                <button class="btn btn-outline-primary" data-period="1y">1Y</button>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="priceChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <i class="bi bi-info-circle me-2"></i>Key Metrics
                        </div>
                        <div class="card-body">
                            <div class="row g-3">
                                <div class="col-6">
                                    <div class="metric-card">
                                        <div class="label">Open</div>
                                        <div class="value">$${info.open?.toFixed(2) || 'N/A'}</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="metric-card">
                                        <div class="label">Volume</div>
                                        <div class="value">${this.formatVolume(info.volume)}</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="metric-card">
                                        <div class="label">Day High</div>
                                        <div class="value">$${info.day_high?.toFixed(2) || 'N/A'}</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="metric-card">
                                        <div class="label">Day Low</div>
                                        <div class="value">$${info.day_low?.toFixed(2) || 'N/A'}</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="metric-card">
                                        <div class="label">52W High</div>
                                        <div class="value">$${info['52_week_high']?.toFixed(2) || 'N/A'}</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="metric-card">
                                        <div class="label">52W Low</div>
                                        <div class="value">$${info['52_week_low']?.toFixed(2) || 'N/A'}</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="metric-card">
                                        <div class="label">P/E Ratio</div>
                                        <div class="value">${info.pe_ratio?.toFixed(2) || 'N/A'}</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="metric-card">
                                        <div class="label">Market Cap</div>
                                        <div class="value">${this.formatMarketCap(info.market_cap)}</div>
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
                            <i class="bi bi-activity me-2"></i>Technical Analysis
                        </div>
                        <div class="card-body">
                            ${technicals.error ? `<div class="text-muted">Technical data unavailable</div>` : `
                                <div class="row g-3 mb-3">
                                    <div class="col-4">
                                        <div class="metric-card">
                                            <div class="label">RSI (14)</div>
                                            <div class="value ${technicals.rsi > 70 ? 'text-danger' : technicals.rsi < 30 ? 'text-success' : ''}">${technicals.rsi?.toFixed(2) || 'N/A'}</div>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <div class="metric-card">
                                            <div class="label">SMA 20</div>
                                            <div class="value">$${technicals.sma_20?.toFixed(2) || 'N/A'}</div>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <div class="metric-card">
                                            <div class="label">SMA 50</div>
                                            <div class="value">$${technicals.sma_50?.toFixed(2) || 'N/A'}</div>
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-2"><strong>Signals:</strong></div>
                                <div>
                                    ${(technicals.signals || []).map(signal => `
                                        <span class="signal-badge ${signal.toLowerCase().includes('bullish') ? 'bullish' : signal.toLowerCase().includes('bearish') ? 'bearish' : 'neutral'}">
                                            ${signal}
                                        </span>
                                    `).join('')}
                                </div>
                            `}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span><i class="bi bi-robot me-2"></i>AI Analysis</span>
                            <button class="btn btn-sm btn-light" id="getAIAnalysisBtn">
                                <i class="bi bi-lightning me-1"></i>Get Analysis
                            </button>
                        </div>
                        <div class="card-body" id="aiAnalysisContainer">
                            <div class="text-center text-muted">
                                <i class="bi bi-robot" style="font-size: 2rem;"></i>
                                <p class="mt-2">Click "Get Analysis" for AI-powered stock recommendation</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <i class="bi bi-newspaper me-2"></i>Recent News
                        </div>
                        <div class="card-body p-0">
                            ${news.news && news.news.length > 0 ? news.news.map(item => `
                                <div class="news-item">
                                    <a href="${item.link}" target="_blank" class="title">${item.title}</a>
                                    <div class="meta">
                                        <span>${item.publisher}</span>
                                        ${item.published ? `<span class="ms-2">${item.published}</span>` : ''}
                                    </div>
                                </div>
                            `).join('') : '<div class="text-center text-muted p-4">No recent news available</div>'}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.renderPriceChart(history);
        this.setupDetailEventListeners();
    }
    
    static setupDetailEventListeners() {
        document.querySelectorAll('#periodSelector button').forEach(btn => {
            btn.addEventListener('click', async () => {
                document.querySelectorAll('#periodSelector button').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const history = await API.stocks.getHistory(this.currentSymbol, btn.dataset.period, '1d');
                this.renderPriceChart(history);
            });
        });
        
        document.getElementById('getAIAnalysisBtn').addEventListener('click', () => {
            this.loadAIAnalysis();
        });
    }
    
    static renderPriceChart(history) {
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        if (this.priceChart) {
            this.priceChart.destroy();
        }
        
        const data = history.data || [];
        const labels = data.map(d => d.date);
        const prices = data.map(d => d.close);
        
        const isPositive = prices.length > 1 && prices[prices.length - 1] >= prices[0];
        const color = isPositive ? 'rgb(25, 135, 84)' : 'rgb(220, 53, 69)';
        
        this.priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Price',
                    data: prices,
                    borderColor: color,
                    backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: (context) => `$${context.parsed.y.toFixed(2)}`
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxTicksLimit: 6
                        }
                    },
                    y: {
                        display: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: (value) => '$' + value.toFixed(0)
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
    
    static async loadAIAnalysis() {
        const container = document.getElementById('aiAnalysisContainer');
        container.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2 text-muted">Generating AI analysis...</p>
            </div>
        `;
        
        try {
            const analysis = await API.stocks.getAIAnalysis(this.currentSymbol);
            container.innerHTML = `
                <div class="markdown-content" style="max-height: 300px; overflow-y: auto;">
                    ${this.formatMarkdown(analysis.analysis)}
                </div>
            `;
        } catch (error) {
            container.innerHTML = `
                <div class="text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Failed to generate analysis. Please ensure the OpenAI API key is configured.
                </div>
            `;
        }
    }
    
    static backToDefault() {
        this.currentSymbol = null;
        document.getElementById('stockSearchInput').value = '';
        document.getElementById('stockDetailContainer').classList.add('d-none');
        document.getElementById('defaultView').classList.remove('d-none');
    }
    
    static formatVolume(volume) {
        if (!volume) return 'N/A';
        if (volume >= 1000000000) return (volume / 1000000000).toFixed(2) + 'B';
        if (volume >= 1000000) return (volume / 1000000).toFixed(2) + 'M';
        if (volume >= 1000) return (volume / 1000).toFixed(2) + 'K';
        return volume.toString();
    }
    
    static formatMarketCap(cap) {
        if (!cap) return 'N/A';
        if (cap >= 1000000000000) return '$' + (cap / 1000000000000).toFixed(2) + 'T';
        if (cap >= 1000000000) return '$' + (cap / 1000000000).toFixed(2) + 'B';
        if (cap >= 1000000) return '$' + (cap / 1000000).toFixed(2) + 'M';
        return '$' + cap.toLocaleString();
    }
    
    static formatMarkdown(text) {
        if (!text) return '';
        
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^### (.*$)/gm, '<h6 class="mt-2 mb-1">$1</h6>')
            .replace(/^## (.*$)/gm, '<h5 class="mt-2 mb-1">$1</h5>')
            .replace(/^# (.*$)/gm, '<h4 class="mt-2 mb-1">$1</h4>')
            .replace(/^\- (.*$)/gm, '<li>$1</li>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
    }
}
