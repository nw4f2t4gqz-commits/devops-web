// GitHub Actions Live Status
(function() {
    let refreshInterval;
    
    function getStatusIcon(status, conclusion) {
        if (status === 'in_progress' || status === 'queued') {
            return `<svg class="animate-spin h-5 w-5 text-yellow-400" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>`;
        }
        if (conclusion === 'success') {
            return `<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>`;
        }
        if (conclusion === 'failure') {
            return `<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
            </svg>`;
        }
        return `<svg class="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clip-rule="evenodd"></path>
        </svg>`;
    }

    function getStatusBadge(status, conclusion) {
        if (status === 'in_progress') return '<span class="px-2 py-1 bg-yellow-500/20 text-yellow-300 text-xs rounded-full border border-yellow-500/30">⏳ In Progress</span>';
        if (status === 'queued') return '<span class="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full border border-blue-500/30">⏱️ Queued</span>';
        if (conclusion === 'success') return '<span class="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full border border-green-500/30">✓ Success</span>';
        if (conclusion === 'failure') return '<span class="px-2 py-1 bg-red-500/20 text-red-300 text-xs rounded-full border border-red-500/30">✗ Failed</span>';
        if (conclusion === 'cancelled') return '<span class="px-2 py-1 bg-gray-500/20 text-gray-300 text-xs rounded-full border border-gray-500/30">⊘ Cancelled</span>';
        return '<span class="px-2 py-1 bg-slate-600/20 text-slate-300 text-xs rounded-full border border-slate-600/30">○ Unknown</span>';
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000);
        
        if (diff < 60) return `${diff}s ago`;
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return `${Math.floor(diff / 86400)}d ago`;
    }

    async function fetchGitHubActions() {
        try {
            const response = await fetch('/api/github-actions/status');
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to fetch');
            }
            
            renderActions(data.runs);
        } catch (error) {
            console.error('Error fetching GitHub Actions:', error);
            document.getElementById('github-actions-container').innerHTML = `
                <div class="text-center py-6 text-red-400">
                    <svg class="h-8 w-8 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                    </svg>
                    Error loading GitHub Actions: ${error.message}
                </div>
            `;
        }
    }

    function renderActions(runs) {
        const container = document.getElementById('github-actions-container');
        
        if (!runs || runs.length === 0) {
            container.innerHTML = '<div class="text-center py-6 text-slate-400">No workflow runs found</div>';
            return;
        }

        container.innerHTML = runs.map(run => `
            <div class="p-4 bg-slate-900/50 border border-slate-700 rounded-lg hover:border-blue-500/30 transition">
                <div class="flex items-start gap-3">
                    <div class="mt-1">${getStatusIcon(run.status, run.conclusion)}</div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-start justify-between gap-2">
                            <div>
                                <a href="${run.html_url}" target="_blank" class="font-semibold text-slate-100 hover:text-blue-400 transition">
                                    ${run.name} #${run.id.toString().slice(-4)}
                                </a>
                                <div class="text-xs text-slate-400 mt-1">
                                    ${run.head_commit ? run.head_commit.message : 'No commit message'}
                                </div>
                            </div>
                            ${getStatusBadge(run.status, run.conclusion)}
                        </div>
                        <div class="flex items-center gap-3 mt-2 text-xs text-slate-500">
                            <span>${run.head_commit ? run.head_commit.author : 'Unknown'}</span>
                            <span>•</span>
                            <span>${formatDate(run.updated_at)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Initial fetch
    fetchGitHubActions();

    // Refresh button
    document.getElementById('refresh-actions').addEventListener('click', () => {
        fetchGitHubActions();
    });

    // Auto-refresh every 30 seconds
    refreshInterval = setInterval(fetchGitHubActions, 30000);

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        clearInterval(refreshInterval);
    });
})();

// Lightweight deployment simulator using anime.js
// Controls: Play, Pause, Speed

(function () {
    const steps = [
        { id: 'checkout', title: 'Checkout', detail: 'git clone ...', duration: 900 },
        { id: 'deps', title: 'Install dependencies', detail: 'pip install -r requirements.txt', duration: 1100 },
        { id: 'tests', title: 'Run tests', detail: 'pytest -q', duration: 1600 },
        { id: 'build', title: 'Build image', detail: 'docker build -t devops-web:latest .', duration: 1200 },
        { id: 'push', title: 'Push image', detail: 'docker push registry.example/your-image:tag', duration: 900 },
        { id: 'deploy', title: 'Deploy', detail: 'docker-compose up -d', duration: 1400 },
        { id: 'verify', title: 'Verify', detail: 'health checks & smoke tests', duration: 800 }
    ];

    const container = document.getElementById('sim-steps');
    const terminal = document.getElementById('sim-terminal');
    const progress = document.getElementById('sim-progress');
    const btnPlay = document.getElementById('deploy-play');
    const btnPause = document.getElementById('deploy-pause');
    const selSpeed = document.getElementById('deploy-speed');

    // build DOM
    steps.forEach((s, i) => {
        const el = document.createElement('div');
        el.className = 'flex items-center gap-4 p-3 bg-slate-900/30 border border-slate-800 rounded';
        el.id = `step-${s.id}`;
        el.innerHTML = `
      <div class="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-sm font-bold text-slate-400" aria-hidden="true">${i + 1}</div>
      <div class="flex-1">
        <div class="flex justify-between items-center">
          <div class="font-semibold text-slate-100">${s.title}</div>
          <div class="text-xs text-slate-400" id="status-${s.id}">pending</div>
        </div>
        <div class="text-xs text-slate-400 mt-1">${s.detail}</div>
      </div>
    `;
        container.appendChild(el);
    });

    // typewriter helper
    function typeLine(text, speed = 30) {
        return new Promise(resolve => {
            let i = 0;
            terminal.textContent = '';
            function step() {
                terminal.textContent += text.charAt(i);
                i++;
                terminal.scrollTop = terminal.scrollHeight;
                if (i < text.length) setTimeout(step, speed);
                else resolve();
            }
            step();
        });
    }

    // create timeline with anime.js
    let tl = anime.timeline({ autoplay: false, easing: 'linear' });

    let totalDur = steps.reduce((a, b) => a + b.duration, 0);
    let acc = 0;
    steps.forEach((s, idx) => {
        // At start of step: set running
        tl.add({
            targets: {},
            duration: s.duration,
            begin: function () {
                document.getElementById(`status-${s.id}`).textContent = 'running';
                const num = document.querySelector(`#step-${s.id} > div:first-child`);
                if (num) num.classList.remove('text-slate-400'), num.classList.add('text-blue-400');
                // type step command in terminal (non-blocking)
                typeLine(`# ${s.detail}`);
            },
            update: function (anim) {
                // update global progress
                acc = acc + anim.delta || 0; // not reliable; instead compute from timeline progress
            }
        });

        // At end of step: mark done (use a short add)
        tl.add({
            targets: {},
            duration: 120,
            complete: function () {
                document.getElementById(`status-${s.id}`).textContent = 'done';
                const num = document.querySelector(`#step-${s.id} > div:first-child`);
                if (num) num.classList.remove('bg-slate-800'), num.classList.add('bg-blue-500');
            }
        });
    });

    // update progress via a frame loop tied to timeline
    function updateProgress() {
        const prog = tl.progress / 100; // 0..1
        progress.style.width = Math.round(prog * 100) + '%';
        if (tl.paused) return; // stop updating animation frames when paused
        requestAnimationFrame(updateProgress);
    }

    // Hook controls
    btnPlay.addEventListener('click', function () {
        if (tl.completed) {
            tl.restart();
        } else {
            tl.play();
        }
        requestAnimationFrame(updateProgress);
    });

    btnPause.addEventListener('click', function () {
        tl.pause();
    });

    selSpeed.addEventListener('change', function (e) {
        const v = parseFloat(e.target.value) || 1;
        tl.timeScale = v;
    });

    // expose for debugging
    window.__deploy_tl = tl;
})();
