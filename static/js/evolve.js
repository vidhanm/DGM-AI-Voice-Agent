// Evolve page JavaScript

let ws = null;
let currentGeneration = 0;
let maxGenerations = 0;

// Start evolution
async function startEvolution() {
    // Get configuration
    maxGenerations = parseInt(document.getElementById('max-generations').value);
    const successThreshold = parseFloat(document.getElementById('success-threshold').value);
    const variantsPerGen = parseInt(document.getElementById('variants-per-gen').value);

    // Hide form, show progress
    document.getElementById('config-form').classList.add('hidden');
    document.getElementById('progress-container').classList.remove('hidden');
    document.getElementById('results-container').classList.add('hidden');

    // Clear updates
    document.getElementById('live-updates').innerHTML = '';
    currentGeneration = 0;
    updateProgress(0, 'Connecting to server...');

    try {
        // Create WebSocket connection
        ws = API.createWebSocket('/ws/evolve');

        // Set up event handlers
        ws.onopen = () => {
            addUpdate('info', 'Connected to evolution server');
            // Send configuration
            ws.send(JSON.stringify({
                max_generations: maxGenerations,
                success_threshold: successThreshold,
                variants_per_generation: variantsPerGen
            }));
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleEvolutionMessage(message);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            addUpdate('error', 'Connection error occurred');
            UI.showError(new Error('WebSocket connection failed'));
        };

        ws.onclose = () => {
            addUpdate('info', 'Connection closed');
        };

    } catch (error) {
        UI.showError(error);
        document.getElementById('config-form').classList.remove('hidden');
        document.getElementById('progress-container').classList.add('hidden');
    }
}

// Handle evolution messages
function handleEvolutionMessage(message) {
    switch (message.type) {
        case 'start':
            addUpdate('success', message.message);
            break;

        case 'config':
            addUpdate('info', `Configuration: ${message.data.max_generations} generations, threshold ${message.data.threshold}`);
            addUpdate('info', `LLM: ${message.data.llm_provider} (${message.data.llm_model})`);
            break;

        case 'generation':
            currentGeneration = message.generation;
            const progress = (currentGeneration / maxGenerations) * 100;
            updateProgress(progress, `Generation ${currentGeneration}/${maxGenerations} - Score: ${message.score.toFixed(1)}`);
            addUpdate('generation', `Gen ${currentGeneration}: Best score = ${message.score.toFixed(1)}`);
            break;

        case 'info':
            addUpdate('info', message.message);
            break;

        case 'complete':
            handleEvolutionComplete(message.data);
            break;

        case 'error':
            addUpdate('error', message.message);
            UI.showError(new Error(message.message));
            // Re-show form
            setTimeout(() => {
                document.getElementById('config-form').classList.remove('hidden');
                document.getElementById('progress-container').classList.add('hidden');
            }, 2000);
            break;

        default:
            console.log('Unknown message type:', message.type);
    }
}

// Update progress bar
function updateProgress(percent, statusText) {
    UI.updateProgressBar('progress-bar', percent, `${Math.round(percent)}%`);
    document.getElementById('status-text').textContent = statusText;
}

// Add update to live updates
function addUpdate(type, message) {
    const updates = document.getElementById('live-updates');
    const timestamp = new Date().toLocaleTimeString();
    const color = {
        'info': 'var(--text-secondary)',
        'success': 'var(--success)',
        'error': 'var(--danger)',
        'generation': 'var(--primary)'
    }[type] || 'var(--text-primary)';

    const div = document.createElement('div');
    div.style.marginBottom = 'var(--spacing-sm)';
    div.style.color = color;
    div.innerHTML = `<span style="color: var(--text-secondary);">[${timestamp}]</span> ${message}`;
    updates.appendChild(div);

    // Scroll to bottom
    updates.scrollTop = updates.scrollHeight;
}

// Handle evolution complete
function handleEvolutionComplete(data) {
    addUpdate('success', 'Evolution complete!');
    updateProgress(100, 'Complete');

    // Hide progress, show results
    setTimeout(() => {
        document.getElementById('progress-container').classList.add('hidden');
        document.getElementById('results-container').classList.remove('hidden');

        // Populate results
        document.getElementById('result-generations').textContent = data.generations_run;
        document.getElementById('result-best-score').textContent = data.best_score.toFixed(1);
        document.getElementById('result-baseline-score').textContent = data.baseline_score.toFixed(1);
        document.getElementById('result-improvement').textContent = `+${data.improvement.toFixed(1)}`;
        document.getElementById('result-agent-id').textContent = data.best_agent_id;
        document.getElementById('result-reason').textContent = data.termination_reason;

        UI.showAlert('Evolution completed successfully!', 'success');
    }, 1000);

    // Close WebSocket
    if (ws) {
        ws.close();
        ws = null;
    }
}
