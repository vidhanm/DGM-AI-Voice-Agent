// Simulate page JavaScript

// Available personas
const PERSONAS = [
    { id: 'angry_anthony', name: 'Angry Anthony' },
    { id: 'evasive_emma', name: 'Evasive Emma' },
    { id: 'curious_carlos', name: 'Curious Carlos' },
    { id: 'cooperative_chloe', name: 'Cooperative Chloe' },
    { id: 'desperate_david', name: 'Desperate David' }
];

// Initialize page
async function initSimulatePage() {
    await loadAgents();
    renderPersonaCheckboxes();
}

// Load available agents
async function loadAgents() {
    try {
        const data = await API.get('/api/agents');
        const select = document.getElementById('agent-select');

        // Add agents to dropdown
        data.agents.forEach(agent => {
            const option = document.createElement('option');
            option.value = agent.id;
            option.textContent = `${agent.id} (Gen ${agent.generation}, Score: ${UI.formatScore(agent.composite_score)})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load agents:', error);
        UI.showError(error);
    }
}

// Render persona checkboxes
function renderPersonaCheckboxes() {
    const container = document.getElementById('persona-checkboxes');
    container.innerHTML = '';

    PERSONAS.forEach(persona => {
        const label = document.createElement('label');
        label.style.display = 'flex';
        label.style.alignItems = 'center';
        label.style.marginBottom = 'var(--spacing-sm)';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'form-checkbox';
        checkbox.value = persona.id;
        checkbox.checked = true;

        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(persona.name));
        container.appendChild(label);
    });
}

// Get selected personas
function getSelectedPersonas() {
    const checkboxes = document.querySelectorAll('#persona-checkboxes input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Run simulation
async function runSimulation() {
    // Get configuration
    const agentId = document.getElementById('agent-select').value || null;
    const personas = getSelectedPersonas();
    const maxTurns = parseInt(document.getElementById('max-turns').value);

    // Validate
    if (personas.length === 0) {
        UI.showAlert('Please select at least one persona', 'warning');
        return;
    }

    // Disable button
    const btn = document.getElementById('run-btn');
    btn.disabled = true;
    btn.textContent = 'Running...';

    // Hide results, show loading
    document.getElementById('results-container').classList.add('hidden');
    UI.showLoading('loading-container');

    try {
        // Run simulation
        const result = await API.post('/api/simulate', {
            agent_id: agentId,
            personas: personas,
            max_turns: maxTurns
        });

        // Display results
        displayResults(result);
        UI.showAlert('Simulation completed successfully!', 'success');

    } catch (error) {
        UI.showError(error);
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.textContent = 'Run Simulation';
        UI.hideLoading('loading-container');
    }
}

// Display results
function displayResults(result) {
    // Show results container
    document.getElementById('results-container').classList.remove('hidden');

    // Update summary
    document.getElementById('summary-total').textContent = result.summary.total;
    document.getElementById('summary-success').textContent = result.summary.success;
    document.getElementById('summary-failure').textContent = result.summary.failure;
    document.getElementById('summary-incomplete').textContent = result.summary.incomplete;

    // Populate table
    const tbody = document.querySelector('#results-table tbody');
    tbody.innerHTML = '';

    result.results.forEach(conv => {
        const row = tbody.insertRow();

        // Persona
        const personaCell = row.insertCell();
        const persona = PERSONAS.find(p => conv.persona_name === p.id);
        personaCell.textContent = persona ? persona.name : conv.persona_name;

        // Outcome
        const outcomeCell = row.insertCell();
        outcomeCell.innerHTML = Format.outcomeBadge(conv.outcome);

        // Turns
        const turnsCell = row.insertCell();
        turnsCell.textContent = conv.turn_count;

        // Goal achieved
        const goalCell = row.insertCell();
        goalCell.innerHTML = conv.goal_achieved ?
            UI.createBadge('Yes', 'success') :
            UI.createBadge('No', 'danger');

        // Actions
        const actionsCell = row.insertCell();
        const viewBtn = document.createElement('button');
        viewBtn.className = 'btn btn-secondary btn-sm';
        viewBtn.textContent = 'View';
        viewBtn.onclick = () => viewConversation(conv.conversation_id);
        actionsCell.appendChild(viewBtn);
    });
}

// View conversation details
async function viewConversation(conversationId) {
    try {
        const conversation = await API.get(`/api/conversations/${conversationId}`);
        // TODO: Show conversation in a modal or separate view
        console.log('Conversation:', conversation);
        UI.showAlert('Conversation details logged to console', 'info');
    } catch (error) {
        UI.showError(error);
    }
}

// Initialize page on load
document.addEventListener('DOMContentLoaded', initSimulatePage);
