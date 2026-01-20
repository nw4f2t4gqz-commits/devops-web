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
