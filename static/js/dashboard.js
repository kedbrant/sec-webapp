// SEC Trading Analyzer - Dashboard JavaScript

class SECDashboard {
    constructor() {
        this.apiBase = '';  // Same origin
        this.currentOpportunities = [];
        this.currentSectors = [];
        this.currentFilings = [];
        
        this.init();
    }

    async init() {
        console.log('Initializing SEC Dashboard...');
        
        // Check API connection
        await this.checkApiStatus();
        
        // Load initial data
        await this.loadDashboardData();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Auto-refresh every 5 minutes
        setInterval(() => this.loadDashboardData(), 5 * 60 * 1000);
    }

    async checkApiStatus() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateStatusIndicator(true, 'Connected - API Online');
                console.log('API Status:', data);
            } else {
                throw new Error('API not responding');
            }
        } catch (error) {
            console.error('API connection failed:', error);
            this.updateStatusIndicator(false, 'Connection Failed');
        }
    }

    updateStatusIndicator(connected, message) {
        const statusDot = document.getElementById('api-status');
        const statusText = document.getElementById('status-text');
        
        if (connected) {
            statusDot.classList.add('connected');
            statusText.textContent = message;
        } else {
            statusDot.classList.remove('connected');
            statusText.textContent = message;
        }
    }

    async loadDashboardData() {
        console.log('Loading dashboard data...');
        
        try {
            // Load all data in parallel
            await Promise.all([
                this.loadTradingOpportunities(),
                this.loadSectorActivity(),
                this.loadRecentFilings(),
                this.updateStats()
            ]);
            
            console.log('Dashboard data loaded successfully');
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadTradingOpportunities() {
        try {
            const minOwnership = document.getElementById('ownership-filter').value || '5.0';
            const response = await fetch(`${this.apiBase}/api/v1/filings/trading-opportunities?min_ownership=${minOwnership}&days_back=60`);
            const data = await response.json();
            
            this.currentOpportunities = data.opportunities || [];
            this.renderTradingOpportunities(this.currentOpportunities);
            
        } catch (error) {
            console.error('Error loading trading opportunities:', error);
            this.showError('opportunities-container', 'Failed to load trading opportunities');
        }
    }

    async loadSectorActivity() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/analytics/sector-activity?days_back=30`);
            const data = await response.json();
            
            this.currentSectors = data.sector_activity || [];
            this.renderSectorActivity(this.currentSectors);
            
        } catch (error) {
            console.error('Error loading sector activity:', error);
            this.showError('sector-container', 'Failed to load sector data');
        }
    }

    async loadRecentFilings() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/filings/?days_back=14&limit=10&sort_by=filing_date&order=desc`);
            const data = await response.json();
            
            this.currentFilings = data.filings || [];
            this.renderRecentFilings(this.currentFilings);
            
        } catch (error) {
            console.error('Error loading recent filings:', error);
            this.showError('filings-container', 'Failed to load recent filings');
        }
    }

    async updateStats() {
        try {
            // Get basic stats
            const [companiesResp, filingsResp] = await Promise.all([
                fetch(`${this.apiBase}/api/v1/companies/?limit=1`),
                fetch(`${this.apiBase}/api/v1/filings/?limit=1`)
            ]);
            
            const companiesData = await companiesResp.json();
            const filingsData = await filingsResp.json();
            
            // Update stat cards
            document.getElementById('total-opportunities').textContent = this.currentOpportunities.length;
            document.getElementById('total-companies').textContent = companiesData.total || 0;
            document.getElementById('total-filings').textContent = filingsData.total || 0;
            
            // Calculate total position value
            const totalValue = this.currentOpportunities.reduce((sum, opp) => {
                return sum + (opp.analysis?.estimated_position_value || 0);
            }, 0);
            
            document.getElementById('total-value').textContent = this.formatCurrency(totalValue);
            
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    renderTradingOpportunities(opportunities) {
        const container = document.getElementById('opportunities-container');
        
        if (!opportunities || opportunities.length === 0) {
            container.innerHTML = '<div class="loading">No trading opportunities found</div>';
            return;
        }

        const html = opportunities.map(opp => {
            const filing = opp.filing;
            const company = opp.company;
            const analysis = opp.analysis;
            
            return `
                <div class="opportunity-card">
                    <div class="opportunity-header">
                        <div class="company-info">
                            <h3>${company.name}</h3>
                            <div class="ticker">${company.ticker} | ${company.sector}</div>
                        </div>
                        <div class="signal-badge signal-${analysis.signal_strength.toLowerCase()}">
                            ${analysis.signal_strength}
                        </div>
                    </div>
                    
                    <div class="opportunity-details">
                        <div class="detail-item">
                            <div class="label">Owner</div>
                            <div class="value">${filing.owner_name}</div>
                        </div>
                        <div class="detail-item">
                            <div class="label">Ownership</div>
                            <div class="value">${filing.ownership_percent}%</div>
                        </div>
                        <div class="detail-item">
                            <div class="label">Shares</div>
                            <div class="value">${this.formatNumber(filing.shares_owned)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="label">Est. Value</div>
                            <div class="value">${this.formatCurrency(analysis.estimated_position_value)}</div>
                        </div>
                    </div>
                    
                    <div class="opportunity-meta">
                        <span class="form-type ${analysis.is_activist_form ? 'activist' : ''}">${filing.form_type}</span>
                        <span class="filing-age">${analysis.days_since_filing} days ago</span>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
    }

    renderSectorActivity(sectors) {
        const container = document.getElementById('sector-container');
        
        if (!sectors || sectors.length === 0) {
            container.innerHTML = '<div class="loading">No sector data available</div>';
            return;
        }

        const html = sectors.map(sector => `
            <div class="sector-card">
                <h3>${sector.sector}</h3>
                <div class="sector-stats">
                    <div class="sector-stat">
                        <span class="label">Filings</span>
                        <span class="value">${sector.filing_count}</span>
                    </div>
                    <div class="sector-stat">
                        <span class="label">Total Shares</span>
                        <span class="value">${this.formatNumber(sector.total_shares_tracked)}</span>
                    </div>
                    <div class="sector-stat">
                        <span class="label">Avg Ownership</span>
                        <span class="value">${sector.average_ownership}%</span>
                    </div>
                    <div class="sector-stat">
                        <span class="label">Activity Score</span>
                        <span class="value">${sector.activity_score.toFixed(1)}</span>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }

    renderRecentFilings(filings) {
        const container = document.getElementById('filings-container');
        
        if (!filings || filings.length === 0) {
            container.innerHTML = '<div class="loading">No recent filings found</div>';
            return;
        }

        const html = filings.map(filing => `
            <div class="filing-item">
                <div class="filing-header">
                    <div>
                        <div class="filing-company">Company ID: ${filing.company_id}</div>
                        <div class="filing-owner">${filing.owner_name}</div>
                    </div>
                    <div class="filing-date">${this.formatDate(filing.filing_date)}</div>
                </div>
                
                <div class="filing-stats">
                    <div class="detail-item">
                        <div class="label">Form Type</div>
                        <div class="value">
                            <span class="form-type ${filing.form_type === '13D' ? 'activist' : ''}">${filing.form_type}</span>
                        </div>
                    </div>
                    <div class="detail-item">
                        <div class="label">Ownership</div>
                        <div class="value">${filing.ownership_percent}%</div>
                    </div>
                    <div class="detail-item">
                        <div class="label">Shares</div>
                        <div class="value">${this.formatNumber(filing.shares_owned)}</div>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }

    setupEventListeners() {
        // Refresh button
        document.getElementById('refresh-data').addEventListener('click', () => {
            this.loadDashboardData();
        });

        // Ownership filter
        document.getElementById('ownership-filter').addEventListener('change', () => {
            this.loadTradingOpportunities();
        });

        // Form type filters
        document.querySelectorAll('.form-filter').forEach(button => {
            button.addEventListener('click', (e) => {
                // Update active state
                document.querySelectorAll('.form-filter').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
                
                const formType = e.target.dataset.form;
                this.filterFilings(formType);
            });
        });
    }

    async filterFilings(formType) {
        try {
            let url = `${this.apiBase}/api/v1/filings/?days_back=14&limit=10&sort_by=filing_date&order=desc`;
            
            if (formType && formType !== 'all') {
                url += `&form_type=${formType}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            this.renderRecentFilings(data.filings || []);
            
        } catch (error) {
            console.error('Error filtering filings:', error);
        }
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <div class="loading" style="color: #e74c3c;">
                <i class="fas fa-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }

    // Utility functions
    formatNumber(num) {
        if (!num) return '0';
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
        return num.toString();
    }

    formatCurrency(amount) {
        if (!amount) return '$0';
        if (amount >= 1e9) return '$' + (amount / 1e9).toFixed(1) + 'B';
        if (amount >= 1e6) return '$' + (amount / 1e6).toFixed(1) + 'M';
        if (amount >= 1e3) return '$' + (amount / 1e3).toFixed(1) + 'K';
        return '$' + amount.toString();
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SECDashboard();
});

// Add some debugging helpers
window.debugDashboard = () => {
    console.log('Current Opportunities:', window.dashboard?.currentOpportunities);
    console.log('Current Sectors:', window.dashboard?.currentSectors);
    console.log('Current Filings:', window.dashboard?.currentFilings);
};