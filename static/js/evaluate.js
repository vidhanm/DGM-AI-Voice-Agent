// Evaluate page JavaScript

const PERSONAS = [
    { id: 'angry_anthony', name: 'Angry Anthony' },
    { id: 'evasive_emma', name: 'Evasive Emma' },
    { id: 'curious_carlos', name: 'Curious Carlos' },
    { id: 'cooperative_chloe', name: 'Cooperative Chloe' },
    { id: 'desperate_david', name: 'Desperate David' }
];

// Initialize page
async function initEvaluatePage() {
    await loadAgents();
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

// Run evaluation
async function runEvaluation() {
    // Get configuration
    const agentId = document.getElementById('agent-select').value || null;

    // Disable button
    const btn = document.getElementById('run-btn');
    btn.disabled = true;
    btn.textContent = 'Running Evaluation...';

    // Hide results, show loading
    document.getElementById('results-container').classList.add('hidden');
    UI.showLoading('loading-container');

    try {
        // Run evaluation
        const result = await API.post('/api/evaluate', {
            agent_id: agentId,
            personas: PERSONAS.map(p => p.id)
        });

        // Display results
        displayResults(result);
        UI.showAlert('Evaluation completed successfully!', 'success');

    } catch (error) {
        UI.showError(error);
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.textContent = 'Run Evaluation';
        UI.hideLoading('loading-container');
    }
}

// Display results
function displayResults(result) {
    // Show results container
    document.getElementById('results-container').classList.remove('hidden');

    // Update average scores
    document.getElementById('avg-goal').textContent =
        UI.formatScore(result.average_scores.goal_completion);
    document.getElementById('avg-quality').textContent =
        UI.formatScore(result.average_scores.conversational_quality);
    document.getElementById('avg-compliance').textContent =
        UI.formatScore(result.average_scores.compliance);
    document.getElementById('avg-composite').textContent =
        UI.formatScore(result.average_scores.composite);

    // Update pass rate
    const passPercent = (result.pass_rate * 100).toFixed(0);
    document.getElementById('pass-rate').innerHTML =
        `${result.pass_count}/${result.total_conversations} (<strong>${passPercent}%</strong>)`;

    // Populate table
    const tbody = document.querySelector('#results-table tbody');
    tbody.innerHTML = '';

    result.scores.forEach((scores, index) => {
        const row = tbody.insertRow();

        // Persona
        const personaCell = row.insertCell();
        const persona = PERSONAS[index];
        personaCell.textContent = persona ? persona.name : 'Unknown';

        // Goal Completion
        const goalCell = row.insertCell();
        goalCell.innerHTML = Format.scoreWithColor(scores.goal_completion_score);

        // Quality
        const qualityCell = row.insertCell();
        qualityCell.innerHTML = Format.scoreWithColor(scores.conversational_quality_score);

        // Compliance
        const complianceCell = row.insertCell();
        complianceCell.innerHTML = Format.scoreWithColor(scores.compliance_score);

        // Composite
        const compositeCell = row.insertCell();
        compositeCell.innerHTML = Format.scoreWithColor(scores.composite_score);

        // Status
        const statusCell = row.insertCell();
        statusCell.innerHTML = scores.passed ?
            UI.createBadge('✓ Passed', 'success') :
            UI.createBadge('✗ Failed', 'danger');
    });
}

// Initialize page on load
document.addEventListener('DOMContentLoaded', initEvaluatePage);
