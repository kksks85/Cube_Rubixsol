/**
 * Resizable Dashboard System
 * Enables users to resize and rearrange dashboard tiles
 */

class ResizableDashboard {
    constructor() {
        console.log('ResizableDashboard constructor called');
        this.isEditMode = false;
        this.grid = null;
        this.localStorage = window.localStorage;
        this.storageKey = 'dashboard-layout';
        this.initialized = false;
        
        // Bind methods to ensure correct 'this' context
        this.toggleEditMode = this.toggleEditMode.bind(this);
        this.saveLayout = this.saveLayout.bind(this);
        this.resetLayout = this.resetLayout.bind(this);
        
        this.init();
    }

    init() {
        console.log('ResizableDashboard: Initializing...');
        
        // First setup basic event listeners
        this.setupBasicEventListeners();
        
        // Then try to setup GridStack
        this.setupGrid();
        
        // Load saved layout if available
        this.loadSavedLayout();
        
        // Initialize other features
        this.initializeEditMode();
        
        this.initialized = true;
        console.log('ResizableDashboard: Initialization complete');
    }

    setupBasicEventListeners() {
        console.log('Setting up basic event listeners...');
        
        // Remove any existing listeners first
        const editBtn = document.getElementById('toggle-edit-mode');
        const saveBtn = document.getElementById('save-layout');
        const resetBtn = document.getElementById('reset-layout');
        
        if (editBtn) {
            // Remove any existing listeners by cloning the element
            const newEditBtn = editBtn.cloneNode(true);
            editBtn.parentNode.replaceChild(newEditBtn, editBtn);
            
            // Add new listener
            newEditBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Edit button clicked - calling toggleEditMode');
                this.toggleEditMode();
            });
            console.log('Edit button listener attached');
        } else {
            console.error('Edit button not found: toggle-edit-mode');
        }

        if (saveBtn) {
            const newSaveBtn = saveBtn.cloneNode(true);
            saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
            
            newSaveBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Save button clicked');
                this.saveLayout();
            });
            console.log('Save button listener attached');
        }

        if (resetBtn) {
            const newResetBtn = resetBtn.cloneNode(true);
            resetBtn.parentNode.replaceChild(newResetBtn, resetBtn);
            
            newResetBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Reset button clicked');
                this.resetLayout();
            });
            console.log('Reset button listener attached');
        }

        // Add tile buttons
        const addTileBtns = document.querySelectorAll('.add-tile-btn');
        console.log(`Found ${addTileBtns.length} add tile buttons`);
        addTileBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const tileType = e.target.closest('.add-tile-btn').dataset.tileType;
                console.log('Add tile button clicked, type:', tileType);
                this.addTile(tileType);
            });
        });
    }

    setupGrid() {
        try {
            console.log('Setting up GridStack...');
            
            // Check if GridStack is available
            if (typeof GridStack === 'undefined') {
                console.warn('GridStack not available, will use basic functionality');
                return;
            }
            
            // Initialize GridStack for resizable/draggable functionality
            this.grid = GridStack.init({
                cellHeight: 80,
                margin: 10,
                resizable: {
                    handles: 'e, se, s, sw, w'
                },
                draggable: {
                    handle: '.tile-header'
                },
                acceptWidgets: true,
                removable: false,
                staticGrid: true // Start in view mode
            });

            console.log('GridStack initialized successfully');

            // Listen for changes
            this.grid.on('change', (event, items) => {
                if (this.isEditMode) {
                    this.saveLayout();
                }
            });
        } catch (error) {
            console.error('Error setting up GridStack:', error);
            this.showError('Failed to initialize the resizable grid system.');
        }
    }

    toggleEditMode() {
        console.log('toggleEditMode called, current state:', this.isEditMode);
        
        // Toggle the state
        this.isEditMode = !this.isEditMode;
        console.log('New edit mode state:', this.isEditMode);
        
        // Always update button states
        this.updateButtonStates();
        
        // If GridStack is available, enable/disable it
        if (this.grid) {
            try {
                if (this.isEditMode) {
                    console.log('Enabling GridStack edit mode');
                    this.grid.enableMove(true);
                    this.grid.enableResize(true);
                    this.showEditHints();
                    this.showNotification('Edit Mode Enabled - Drag tiles to reposition, resize using corners', 'success');
                } else {
                    console.log('Disabling GridStack edit mode');
                    this.grid.enableMove(false);
                    this.grid.enableResize(false);
                    this.hideEditHints();
                    this.showNotification('View Mode Enabled', 'info');
                }
            } catch (error) {
                console.error('Error with GridStack operations:', error);
            }
        } else {
            // Fallback functionality without GridStack
            if (this.isEditMode) {
                this.showNotification('Edit Mode Enabled (Basic Mode)', 'warning');
            } else {
                this.showNotification('View Mode Enabled', 'info');
            }
        }
    }

    updateButtonStates() {
        const editBtn = document.getElementById('toggle-edit-mode');
        const saveBtn = document.getElementById('save-layout');
        const resetBtn = document.getElementById('reset-layout');
        const gridContainer = document.querySelector('.grid-stack');

        console.log('Updating button states, edit mode:', this.isEditMode);

        if (editBtn) {
            if (this.isEditMode) {
                editBtn.innerHTML = '<i class="fas fa-eye"></i> View Mode';
                editBtn.classList.remove('btn-outline-primary');
                editBtn.classList.add('btn-success');
            } else {
                editBtn.innerHTML = '<i class="fas fa-edit"></i> Edit Layout';
                editBtn.classList.remove('btn-success');
                editBtn.classList.add('btn-outline-primary');
            }
            console.log('Edit button updated');
        }

        if (saveBtn) {
            saveBtn.style.display = this.isEditMode ? 'inline-block' : 'none';
            console.log('Save button visibility:', this.isEditMode ? 'shown' : 'hidden');
        }
        
        if (resetBtn) {
            resetBtn.style.display = this.isEditMode ? 'inline-block' : 'none';
            console.log('Reset button visibility:', this.isEditMode ? 'shown' : 'hidden');
        }
        
        if (gridContainer) {
            if (this.isEditMode) {
                gridContainer.classList.add('edit-mode');
            } else {
                gridContainer.classList.remove('edit-mode');
            }
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        errorDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
        errorDiv.innerHTML = `
            <strong>Dashboard Error:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(errorDiv);

        // Auto remove after 10 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 10000);
    }

    saveLayout() {
        const layout = [];
        this.grid.getGridItems().forEach(item => {
            const node = item.gridstackNode;
            layout.push({
                id: item.dataset.tileId,
                x: node.x,
                y: node.y,
                w: node.w,
                h: node.h,
                type: item.dataset.tileType || 'default'
            });
        });

        this.localStorage.setItem(this.storageKey, JSON.stringify(layout));
        this.showNotification('Layout saved successfully!', 'success');
    }

    loadSavedLayout() {
        const savedLayout = this.localStorage.getItem(this.storageKey);
        if (savedLayout) {
            try {
                const layout = JSON.parse(savedLayout);
                this.applyLayout(layout);
            } catch (e) {
                console.warn('Error loading saved layout:', e);
            }
        }
    }

    applyLayout(layout) {
        layout.forEach(item => {
            const element = document.querySelector(`[data-tile-id="${item.id}"]`);
            if (element) {
                this.grid.update(element, {
                    x: item.x,
                    y: item.y,
                    w: item.w,
                    h: item.h
                });
            }
        });
    }

    resetLayout() {
        if (confirm('Are you sure you want to reset the dashboard layout?')) {
            this.localStorage.removeItem(this.storageKey);
            location.reload();
        }
    }

    addTile(tileType) {
        const tileConfigs = {
            'stat': {
                w: 3, h: 2,
                content: this.createStatTile('New Statistic', '0', 'primary')
            },
            'chart': {
                w: 6, h: 4,
                content: this.createChartTile('New Chart')
            },
            'list': {
                w: 4, h: 4,
                content: this.createListTile('New List')
            },
            'quickAction': {
                w: 3, h: 2,
                content: this.createQuickActionTile('New Action')
            }
        };

        const config = tileConfigs[tileType];
        if (config) {
            const newTile = document.createElement('div');
            newTile.className = 'grid-stack-item dashboard-tile';
            newTile.dataset.tileId = 'tile-' + Date.now();
            newTile.dataset.tileType = tileType;
            newTile.innerHTML = config.content;

            this.grid.addWidget(newTile, {
                w: config.w,
                h: config.h
            });
        }
    }

    createStatTile(title, value, color) {
        return `
            <div class="grid-stack-item-content tile-content">
                <div class="tile-header">
                    <h6 class="tile-title">${title}</h6>
                    <div class="tile-actions">
                        <button class="btn btn-sm btn-outline-secondary remove-tile">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="tile-body text-center">
                    <div class="stat-value text-${color} display-4 fw-bold">${value}</div>
                    <div class="stat-label text-muted">${title}</div>
                </div>
            </div>
        `;
    }

    createChartTile(title) {
        return `
            <div class="grid-stack-item-content tile-content">
                <div class="tile-header">
                    <h6 class="tile-title">${title}</h6>
                    <div class="tile-actions">
                        <button class="btn btn-sm btn-outline-secondary remove-tile">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="tile-body">
                    <canvas class="chart-canvas" width="100%" height="200"></canvas>
                    <div class="text-center text-muted">Chart placeholder</div>
                </div>
            </div>
        `;
    }

    createListTile(title) {
        return `
            <div class="grid-stack-item-content tile-content">
                <div class="tile-header">
                    <h6 class="tile-title">${title}</h6>
                    <div class="tile-actions">
                        <button class="btn btn-sm btn-outline-secondary remove-tile">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="tile-body">
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item">Sample item 1</li>
                        <li class="list-group-item">Sample item 2</li>
                        <li class="list-group-item">Sample item 3</li>
                    </ul>
                </div>
            </div>
        `;
    }

    createQuickActionTile(title) {
        return `
            <div class="grid-stack-item-content tile-content">
                <div class="tile-header">
                    <h6 class="tile-title">${title}</h6>
                    <div class="tile-actions">
                        <button class="btn btn-sm btn-outline-secondary remove-tile">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="tile-body text-center">
                    <button class="btn btn-primary btn-lg">
                        <i class="fas fa-plus"></i>
                    </button>
                    <div class="mt-2 text-muted small">${title}</div>
                </div>
            </div>
        `;
    }

    showEditHints() {
        const hints = document.createElement('div');
        hints.id = 'edit-hints';
        hints.className = 'alert alert-info position-fixed';
        hints.style.cssText = 'top: 80px; right: 20px; z-index: 1050; max-width: 300px;';
        hints.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-info-circle me-2"></i>
                <div>
                    <strong>Edit Mode Active</strong><br>
                    <small>Drag tiles by their headers to reposition. Resize using corner handles.</small>
                </div>
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        document.body.appendChild(hints);
    }

    hideEditHints() {
        const hints = document.getElementById('edit-hints');
        if (hints) hints.remove();
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    initializeEditMode() {
        // Add remove tile functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('.remove-tile') && this.isEditMode) {
                const tile = e.target.closest('.grid-stack-item');
                if (tile && confirm('Remove this tile?')) {
                    this.grid.removeWidget(tile);
                }
            }
        });
    }
}

// Initialize when DOM is loaded or immediately if already loaded
function initializeDashboard() {
    console.log('Attempting to initialize ResizableDashboard...');
    const gridElement = document.querySelector('.grid-stack');
    console.log('Grid element found:', !!gridElement);
    
    if (gridElement) {
        console.log('Creating new ResizableDashboard instance...');
        const dashboard = new ResizableDashboard();
        window.resizableDashboard = dashboard; // Make globally accessible for debugging
        console.log('ResizableDashboard created and assigned to window.resizableDashboard');
    } else {
        console.warn('Grid element not found, dashboard not initialized');
    }
}

// Global variable to store dashboard instance
window.dashboardInstance = null;

// Initialize dashboard with multiple fallback methods
function initializeDashboard() {
    console.log('=== DASHBOARD INITIALIZATION START ===');
    console.log('DOM ready state:', document.readyState);
    console.log('GridStack available:', typeof GridStack !== 'undefined');
    
    const gridElement = document.querySelector('.grid-stack');
    console.log('Grid element found:', !!gridElement);
    
    if (!gridElement) {
        console.warn('Grid element not found, dashboard not initialized');
        return;
    }
    
    // Prevent multiple initialization
    if (window.dashboardInstance) {
        console.log('Dashboard already initialized, skipping');
        return;
    }
    
    try {
        console.log('Creating ResizableDashboard instance...');
        window.dashboardInstance = new ResizableDashboard();
        console.log('✅ Dashboard initialization successful');
        
        // Add a test button click after short delay
        setTimeout(() => {
            const editBtn = document.getElementById('toggle-edit-mode');
            if (editBtn) {
                console.log('Test: Edit button element found after initialization');
                console.log('Test: Button click listeners:', editBtn.onclick);
            }
        }, 500);
        
    } catch (error) {
        console.error('❌ Dashboard initialization failed:', error);
    }
    
    console.log('=== DASHBOARD INITIALIZATION END ===');
}

// Multiple initialization strategies
console.log('Setting up dashboard initialization...');

// Strategy 1: If DOM is already loaded
if (document.readyState === 'loading') {
    console.log('DOM is loading, waiting for DOMContentLoaded');
    document.addEventListener('DOMContentLoaded', initializeDashboard);
} else {
    console.log('DOM already loaded, initializing immediately');
    // Use setTimeout to ensure all scripts have loaded
    setTimeout(initializeDashboard, 100);
}

// Strategy 2: Backup initialization after page load
window.addEventListener('load', () => {
    if (!window.dashboardInstance) {
        console.log('Backup initialization triggered');
        initializeDashboard();
    }
});

// Strategy 3: Manual initialization function (for debugging)
window.manualInitDashboard = initializeDashboard;
