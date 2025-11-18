// Results page JavaScript

// Initialize page
async function initResultsPage() {
    await loadAgents();
}

// Load all agents
async function loadAgents() {
    UI.showLoading('loading-container');

    try {
        const data = await API.get('/api/agents');
        displayAgents(data.agents);
    } catch (error) {
        console.error('Failed to load agents:', error);
        UI.showError(error);
    } finally {
        UI.hideLoading('loading-container');
    }
}

// Display agents in table
function displayAgents(agents) {
    const tbody = document.querySelector('#agents-table tbody');
    tbody.innerHTML = '';

    if (agents.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 6;
        cell.style.textAlign = 'center';
        cell.style.color = 'var(--text-secondary)';
        cell.textContent = 'No agents found. Run an evolution to create agents.';
        return;
    }

    agents.forEach(agent => {
        const row = tbody.insertRow();

        // Agent ID
        const idCell = row.insertCell();
        idCell.innerHTML = `<code style="font-size: 0.875rem;">${agent.id}</code>`;

        // Generation
        const genCell = row.insertCell();
        genCell.textContent = agent.generation;

        // Score
        const scoreCell = row.insertCell();
        scoreCell.innerHTML = Format.scoreWithColor(agent.composite_score);

        // Parent
        const parentCell = row.insertCell();
        if (agent.parent_id) {
            parentCell.innerHTML = `<code style="font-size: 0.75rem;">${agent.parent_id.substring(0, 8)}...</code>`;
        } else {
            parentCell.textContent = '-';
        }

        // Created
        const createdCell = row.insertCell();
        if (agent.created_at) {
            createdCell.textContent = UI.formatTimestamp(agent.created_at);
            createdCell.style.fontSize = '0.875rem';
        } else {
            createdCell.textContent = '-';
        }

        // Actions
        const actionsCell = row.insertCell();
        const viewBtn = document.createElement('button');
        viewBtn.className = 'btn btn-secondary';
        viewBtn.style.fontSize = '0.875rem';
        viewBtn.style.padding = 'var(--spacing-xs) var(--spacing-sm)';
        viewBtn.textContent = 'View';
        viewBtn.onclick = () => viewAgent(agent.id);
        actionsCell.appendChild(viewBtn);
    });
}

// View agent details
async function viewAgent(agentId) {
    try {
        UI.showLoading('modal-content');
        document.getElementById('agent-modal').classList.remove('hidden');

        const agent = await API.get(`/api/agents/${agentId}`);

        // Populate modal
        document.getElementById('modal-title').textContent = `Agent: ${agentId}`;

        const content = document.getElementById('modal-content');
        content.innerHTML = `
            <div class="grid grid-2 mb-lg">
                <div>
                    <strong>ID:</strong><br>
                    <code>${agent.id}</code>
                </div>
                <div>
                    <strong>Generation:</strong><br>
                    ${agent.generation}
                </div>
                <div>
                    <strong>Composite Score:</strong><br>
                    ${Format.scoreWithColor(agent.composite_score)}
                </div>
                <div>
                    <strong>Parent ID:</strong><br>
                    ${agent.parent_id ? `<code>${agent.parent_id}</code>` : 'None (baseline)'}
                </div>
            </div>

            ${agent.mutation_strategy ? `
            <div class="mb-lg">
                <strong>Mutation Strategy:</strong><br>
                <span class="badge badge-info">${agent.mutation_strategy}</span>
            </div>
            ` : ''}

            ${agent.change_rationale ? `
            <div class="mb-lg">
                <strong>Change Rationale:</strong><br>
                <p style="background: var(--bg-secondary); padding: var(--spacing-md); border-radius: var(--radius-md); font-size: 0.875rem;">
                    ${agent.change_rationale}
                </p>
            </div>
            ` : ''}

            <div class="mb-lg">
                <strong>System Prompt:</strong><br>
                <pre style="background: var(--bg-secondary); padding: var(--spacing-md); border-radius: var(--radius-md); overflow-x: auto; font-size: 0.75rem; max-height: 300px;">${agent.prompt}</pre>
            </div>

            <div style="display: flex; gap: var(--spacing-sm); margin-top: var(--spacing-lg);">
                <a href="/static/evaluate.html" class="btn btn-primary">Evaluate This Agent</a>
                <a href="/static/simulate.html" class="btn btn-secondary">Test in Simulation</a>
            </div>
        `;

    } catch (error) {
        UI.showError(error);
        closeModal();
    }
}

// Close modal
function closeModal() {
    document.getElementById('agent-modal').classList.add('hidden');
}

// Close modal on background click
document.getElementById('agent-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'agent-modal') {
        closeModal();
    }
});

// Initialize page on load
document.addEventListener('DOMContentLoaded', initResultsPage);
