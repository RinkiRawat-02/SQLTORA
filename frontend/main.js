/**
 * SQLtoRA Frontend - Handles UI interactions and API communication
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const sqlInput = document.getElementById('sql-input');
const processBtn = document.getElementById('process-btn');
const clearBtn = document.getElementById('clear-btn');
const schemaBtn = document.getElementById('schema-btn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const schemaModal = document.getElementById('schema-modal');

// Stage output elements
const tokensOutput = document.getElementById('tokens-output');
const parseTreeOutput = document.getElementById('parse-tree-output');
const astOutput = document.getElementById('ast-output');
const semanticOutput = document.getElementById('semantic-output');
const raOutput = document.getElementById('ra-output');

// Stage containers
const stageTokens = document.getElementById('stage-tokens');
const stageParse = document.getElementById('stage-parse');
const stageAst = document.getElementById('stage-ast');
const stageSemantic = document.getElementById('stage-semantic');
const stageRa = document.getElementById('stage-ra');

// Event Listeners
processBtn.addEventListener('click', processQuery);
clearBtn.addEventListener('click', clearQuery);
schemaBtn.addEventListener('click', showSchema);

// Sample query buttons
document.querySelectorAll('.sample-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        sqlInput.value = btn.getAttribute('data-query');
    });
});

// Modal close
document.querySelector('.close-modal').addEventListener('click', () => {
    schemaModal.classList.add('hidden');
});

schemaModal.addEventListener('click', (e) => {
    if (e.target === schemaModal) {
        schemaModal.classList.add('hidden');
    }
});

/**
 * Process SQL query through the pipeline
 */
async function processQuery() {
    const query = sqlInput.value.trim();
    
    if (!query) {
        alert('Please enter a SQL query');
        return;
    }
    
    // Show loading, hide results
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    
    // Clear previous outputs
    clearOutputs();
    
    try {
        const response = await fetch(`${API_BASE_URL}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide loading, show results
        loading.classList.add('hidden');
        results.classList.remove('hidden');
        
        // Display results for each stage
        displayStage1(data.stages.tokenization);
        displayStage2(data.stages.parsing);
        displayStage3(data.stages.ast);
        displayStage4(data.stages.semantic);
        displayStage5(data.stages.relational_algebra);
        
        // Smooth scroll to results
        results.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (error) {
        loading.classList.add('hidden');
        alert(`Error processing query: ${error.message}`);
        console.error('Error:', error);
    }
}

/**
 * Clear query input and results
 */
function clearQuery() {
    sqlInput.value = '';
    results.classList.add('hidden');
    clearOutputs();
}

/**
 * Clear all output containers
 */
function clearOutputs() {
    tokensOutput.innerHTML = '';
    parseTreeOutput.innerHTML = '';
    astOutput.innerHTML = '';
    semanticOutput.innerHTML = '';
    raOutput.innerHTML = '';
}

/**
 * Display Stage 1: Tokenization
 */
function displayStage1(data) {
    const statusEl = stageTokens.querySelector('.stage-status');
    
    if (data.success) {
        statusEl.className = 'stage-status status-success';
        statusEl.textContent = '✅';
        
        const tokenList = document.createElement('div');
        tokenList.className = 'token-list';
        
        data.tokens.forEach(token => {
            if (token.type !== 'EOF') {
                const tokenEl = document.createElement('div');
                tokenEl.className = 'token';
                tokenEl.innerHTML = `
                    <div class="token-type">${token.type}</div>
                    <div class="token-value">${escapeHtml(token.value || '—')}</div>
                `;
                tokenList.appendChild(tokenEl);
            }
        });
        
        tokensOutput.appendChild(tokenList);
    } else {
        statusEl.className = 'stage-status status-error';
        statusEl.textContent = '❌';
        tokensOutput.innerHTML = `<div class="error-item">${escapeHtml(data.error)}</div>`;
    }
}

/**
 * Display Stage 2: Parse Tree
 */
function displayStage2(data) {
    const statusEl = stageParse.querySelector('.stage-status');
    
    if (data.success) {
        statusEl.className = 'stage-status status-success';
        statusEl.textContent = '✅';
        
        const tree = document.createElement('div');
        tree.className = 'tree';
        tree.appendChild(renderTreeNode(data.tree));
        parseTreeOutput.appendChild(tree);
    } else {
        statusEl.className = 'stage-status status-error';
        statusEl.textContent = '❌';
        parseTreeOutput.innerHTML = `<div class="error-item">${escapeHtml(data.error)}</div>`;
    }
}

/**
 * Display Stage 3: AST
 */
/**
 * Stage 3: AST
 */
function displayStage3(data) {
    const statusEl = stageAst.querySelector('.stage-status');
    if (data.success) {
        statusEl.className = 'stage-status status-success';
        statusEl.textContent = '✅';
        astOutput.appendChild(renderTreeNodee(data.tree));
    } else {
        statusEl.className = 'stage-status status-error';
        statusEl.textContent = '❌';
        astOutput.innerHTML = `<div class="error-item">${escapeHtml(data.error)}</div>`;
    }
}


/**
 * Recursively render tree nodes for AST
 */
function renderTreeNodee(node) {
    if (!node) return document.createElement('div');

    const el = document.createElement('div');
    el.className = 'tree-node';
    let html = `<span class="tree-node-type">${escapeHtml(node.type || node.constructor.name)}</span>`;
    if (node.name) html += `: <span class="tree-node-value">${escapeHtml(node.name)}</span>`;
    if (node.value !== undefined) html += `: <span class="tree-node-value">${escapeHtml(String(node.value))}</span>`;
    el.innerHTML = html;

    const children = [];
    if (node.columns) children.push(...node.columns);
    if (node.tables) children.push(...node.tables);
    if (node.joins) children.push(...node.joins);
    if (node.where) children.push(node.where);
    if (node.left) children.push(node.left);
    if (node.right) children.push(node.right);
    if (node.operands) children.push(...node.operands);

    if (children.length > 0) {
        const childContainer = document.createElement('div');
        childContainer.className = 'tree-children';
        children.forEach(child => {
            if (child) childContainer.appendChild(renderTreeNodee(child));
        });
        el.appendChild(childContainer);
    }
    return el;
}


/**
 * Display Stage 4: Semantic Analysis
 */
function displayStage4(data) {
    const statusEl = stageSemantic.querySelector('.stage-status');
    
    if (data.success) {
        const analysis = data.analysis;
        
        if (analysis.valid) {
            statusEl.className = 'stage-status status-success';
            statusEl.textContent = '✅';
            
            semanticOutput.innerHTML = `
                <div class="semantic-valid">
                    ✅ Query is semantically valid!
                </div>
                <div style="margin-top: 15px;">
                    <strong>Tables used:</strong> ${analysis.schema_used.join(', ')}
                </div>
            `;
        } else {
            statusEl.className = 'stage-status status-error';
            statusEl.textContent = '❌';
            
            let html = '<div class="semantic-invalid">❌ Semantic validation failed</div>';
            
            if (analysis.errors && analysis.errors.length > 0) {
                html += '<div class="error-list"><strong>Errors:</strong>';
                analysis.errors.forEach(error => {
                    html += `<div class="error-item">${escapeHtml(error)}</div>`;
                });
                html += '</div>';
            }
            
            if (analysis.warnings && analysis.warnings.length > 0) {
                html += '<div class="warning-list"><strong>Warnings:</strong>';
                analysis.warnings.forEach(warning => {
                    html += `<div class="warning-item">${escapeHtml(warning)}</div>`;
                });
                html += '</div>';
            }
            
            semanticOutput.innerHTML = html;
        }
    } else {
        statusEl.className = 'stage-status status-error';
        statusEl.textContent = '❌';
        semanticOutput.innerHTML = `<div class="error-item">${escapeHtml(data.error)}</div>`;
    }
}

/**
 * Display Stage 5: Relational Algebra
 */
function displayStage5(data) {
    const statusEl = stageRa.querySelector('.stage-status');
    
    if (data.success) {
        statusEl.className = 'stage-status status-success';
        statusEl.textContent = '✅';
        
        let html = `
            <div class="ra-expression">
                <strong>Relational Algebra Expression:</strong><br><br>
                <span style="font-size: 20px;">${escapeHtml(data.expression)}</span>
            </div>
            
            <div class="ra-description">
                <strong>Query Flow:</strong><br>
                ${escapeHtml(data.description)}
            </div>
            
            <div class="ra-operations">
                <strong>Operation Breakdown:</strong>
        `;
        
        data.tree.forEach((op, index) => {
            html += `
                <div class="ra-operation">
                    <div class="ra-symbol">${escapeHtml(op.symbol)}</div>
                    <div class="ra-op-details">
                        <div class="ra-op-name">${escapeHtml(op.operation)}</div>
                        <div class="ra-op-desc">${escapeHtml(op.details)}</div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        raOutput.innerHTML = html;
    } else {
        statusEl.className = 'stage-status status-error';
        statusEl.textContent = '❌';
        raOutput.innerHTML = `<div class="error-item">${escapeHtml(data.error)}</div>`;
    }
}

/**
 * Render tree node recursively for parse tree
 */
function renderTreeNode(node, depth = 0) {
    const nodeEl = document.createElement('div');
    nodeEl.className = 'tree-node';
    
    let nodeHtml = `<span class="tree-node-type">${escapeHtml(node.type)}</span>`;
    
    if (node.value !== null && node.value !== undefined) {
        nodeHtml += `<span class="tree-node-value">"${escapeHtml(String(node.value))}"</span>`;
    }
    
    nodeEl.innerHTML = nodeHtml;
    
    // Render children
    if (node.children && node.children.length > 0) {
        const childrenEl = document.createElement('div');
        childrenEl.className = 'tree-children';
        
        node.children.forEach(child => {
            childrenEl.appendChild(renderTreeNode(child, depth + 1));
        });
        
        nodeEl.appendChild(childrenEl);
    }
    
    return nodeEl;
}

/**
 * Show database schema modal
 */
async function showSchema() {
    try {
        const response = await fetch(`${API_BASE_URL}/schema`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const schemaContent = document.getElementById('schema-content');
        
        let html = '';
        for (const [tableName, columns] of Object.entries(data.schema)) {
            html += `
                <div class="schema-table">
                    <h3>${escapeHtml(tableName)}</h3>
                    <div class="schema-columns">
                        ${columns.map(col => `<span class="schema-column">${escapeHtml(col)}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        schemaContent.innerHTML = html;
        schemaModal.classList.remove('hidden');
        
    } catch (error) {
        alert(`Error fetching schema: ${error.message}`);
        console.error('Error:', error);
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
console.log('SQLtoRA Frontend initialized');
console.log(`API Base URL: ${API_BASE_URL}`);




