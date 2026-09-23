/* ========================================
   RAG Document QA — Showcase Website
   JavaScript: Animations, Interactions, Demo
   ======================================== */

document.addEventListener('DOMContentLoaded', () => {
  initParticleCanvas();
  initNavbar();
  initScrollAnimations();
  initPipelineAnimation();
  initMetricsCounter();
  initDemo();
});

/* ==========================================
   PARTICLE CANVAS — Hero Background
   ========================================== */
function initParticleCanvas() {
  const canvas = document.getElementById('hero-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width, height, particles, connections;
  const PARTICLE_COUNT = 80;
  const CONNECTION_DIST = 150;

  function resize() {
    width = canvas.width = canvas.parentElement.clientWidth;
    height = canvas.height = canvas.parentElement.clientHeight;
  }

  function createParticles() {
    particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1,
        opacity: Math.random() * 0.5 + 0.2,
      });
    }
  }

  function update() {
    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;
    }
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONNECTION_DIST) {
          const opacity = (1 - dist / CONNECTION_DIST) * 0.15;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(124, 58, 237, ${opacity})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    // Draw particles
    for (const p of particles) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(167, 139, 250, ${p.opacity})`;
      ctx.fill();
    }
  }

  function animate() {
    update();
    draw();
    requestAnimationFrame(animate);
  }

  resize();
  createParticles();
  animate();

  window.addEventListener('resize', () => {
    resize();
    createParticles();
  });
}

/* ==========================================
   NAVBAR — Scroll & Mobile Toggle
   ========================================== */
function initNavbar() {
  const navbar = document.getElementById('navbar');
  const toggle = document.getElementById('nav-toggle');
  const links = document.getElementById('nav-links');

  // Scroll effect
  let lastScroll = 0;
  window.addEventListener('scroll', () => {
    const scroll = window.scrollY;
    if (scroll > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
    lastScroll = scroll;
  });

  // Mobile toggle
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
      const spans = toggle.querySelectorAll('span');
      if (links.classList.contains('open')) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      }
    });

    // Close on link click
    links.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        links.classList.remove('open');
        const spans = toggle.querySelectorAll('span');
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      });
    });
  }
}

/* ==========================================
   SCROLL ANIMATIONS — Intersection Observer
   ========================================== */
function initScrollAnimations() {
  const observerOptions = {
    root: null,
    rootMargin: '0px 0px -80px 0px',
    threshold: 0.1,
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        // Don't unobserve stagger-children so they can replay if needed
        if (!entry.target.classList.contains('stagger-children')) {
          // Keep observing for one-time animations is fine
        }
      }
    });
  }, observerOptions);

  // Observe all animated elements
  document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right, .stagger-children').forEach(el => {
    observer.observe(el);
  });
}

/* ==========================================
   PIPELINE ANIMATION — Auto-highlight nodes
   ========================================== */
function initPipelineAnimation() {
  const pipeline = document.getElementById('pipeline');
  if (!pipeline) return;

  const nodes = pipeline.querySelectorAll('.pipeline-node');
  let currentStep = 0;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        startPipelineAnimation();
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  observer.observe(pipeline);

  function startPipelineAnimation() {
    setInterval(() => {
      nodes.forEach(n => n.classList.remove('active'));
      if (nodes[currentStep]) {
        nodes[currentStep].classList.add('active');
      }
      currentStep = (currentStep + 1) % nodes.length;
    }, 1200);
  }
}

/* ==========================================
   METRICS COUNTER — Animated numbers
   ========================================== */
function initMetricsCounter() {
  const metricsGrid = document.getElementById('metrics-grid');
  if (!metricsGrid) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounters();
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  observer.observe(metricsGrid);

  function animateCounters() {
    const counters = metricsGrid.querySelectorAll('.metric-value');
    counters.forEach(counter => {
      const target = parseInt(counter.dataset.target, 10);
      const prefix = counter.dataset.prefix || '';
      const suffix = counter.dataset.suffix || '';
      const duration = 1500;
      const startTime = performance.now();

      function updateCounter(timestamp) {
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(target * eased);

        counter.textContent = `${prefix}${current}${suffix}`;

        if (progress < 1) {
          requestAnimationFrame(updateCounter);
        }
      }

      requestAnimationFrame(updateCounter);
    });
  }
}

/* ==========================================
   DEMO — Simulated Chat Interface
   ========================================== */
function initDemo() {
  const messagesContainer = document.getElementById('demo-messages');
  const inputField = document.getElementById('demo-input-field');
  const sendBtn = document.getElementById('demo-send-btn');

  if (!messagesContainer || !inputField || !sendBtn) return;

  // Pre-scripted conversation flow
  const demoConversation = [
    {
      query: "What is the main purpose of this document?",
      context: "Retrieved from: research_paper.pdf (chunks 3, 7, 12)",
      answer: "Based on the retrieved context, this document presents a comprehensive analysis of machine learning model optimization techniques. It covers three primary areas: hyperparameter tuning using Bayesian methods, model architecture search, and training data augmentation strategies. The key contribution is a novel framework that combines these approaches to achieve state-of-the-art results on benchmark datasets."
    },
    {
      query: "What specific techniques are discussed?",
      context: "Retrieved from: research_paper.pdf (chunks 15, 22, 31) — reformulated with chat history",
      answer: "The document discusses several specific techniques:\n\n• **Bayesian Hyperparameter Optimization** — Using Gaussian Processes to efficiently search the hyperparameter space\n• **Neural Architecture Search (NAS)** — Automated discovery of optimal network topologies\n• **CutMix & MixUp Augmentation** — Advanced data augmentation methods that blend training samples\n• **Knowledge Distillation** — Compressing large models into smaller, faster variants while preserving accuracy"
    },
    {
      query: "What were the performance improvements?",
      context: "Retrieved from: research_paper.pdf (chunks 42, 45, 48)",
      answer: "The combined optimization framework achieved significant improvements:\n\n• **+4.2% accuracy** on ImageNet classification vs. baseline\n• **30% reduction** in training time through efficient architecture search\n• **2.1x faster** inference via knowledge distillation\n• The authors report these results are **reproducible** with the provided code repository and configuration files."
    }
  ];

  let conversationIndex = 0;
  let isTyping = false;

  // Show initial welcome message
  addMessage('assistant', "👋 Welcome! I'm the RAG Document QA assistant. I've indexed your uploaded documents and I'm ready to answer questions. Try asking something about the content!", null);

  function addMessage(role, text, context) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `demo-message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'demo-msg-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🔍';

    const bubble = document.createElement('div');
    bubble.className = 'demo-msg-bubble';

    // Convert markdown-like bold
    const formattedText = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
    bubble.innerHTML = formattedText;

    if (context) {
      const ctxDiv = document.createElement('div');
      ctxDiv.className = 'demo-context';
      ctxDiv.innerHTML = `<span class="demo-context-label">📎 Source Context</span>${context}`;
      bubble.appendChild(ctxDiv);
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function addTypingIndicator() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'demo-message assistant';
    msgDiv.id = 'typing-msg';

    const avatar = document.createElement('div');
    avatar.className = 'demo-msg-avatar';
    avatar.textContent = '🔍';

    const bubble = document.createElement('div');
    bubble.className = 'demo-msg-bubble';
    bubble.innerHTML = `
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    `;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function removeTypingIndicator() {
    const typing = document.getElementById('typing-msg');
    if (typing) typing.remove();
  }

  function processQuery(query) {
    if (isTyping) return;
    isTyping = true;

    // Add user message
    addMessage('user', query, null);
    inputField.value = '';

    // Show typing indicator
    setTimeout(() => {
      addTypingIndicator();

      // Simulate response delay
      const delay = 1200 + Math.random() * 800;
      setTimeout(() => {
        removeTypingIndicator();

        if (conversationIndex < demoConversation.length) {
          const conv = demoConversation[conversationIndex];
          addMessage('assistant', conv.answer, conv.context);
          conversationIndex++;
        } else {
          addMessage('assistant', "That's the end of this demo conversation! In the full system, I would continue searching the FAISS vector index for relevant document chunks and generating answers with the LLM. Check out the GitHub repository to run the full pipeline locally. 🚀", "Demo mode — pre-scripted responses");
          conversationIndex = 0; // Reset for replay
        }

        isTyping = false;
      }, delay);
    }, 300);
  }

  // Event listeners
  sendBtn.addEventListener('click', () => {
    const query = inputField.value.trim();
    if (query) {
      processQuery(query);
    } else if (conversationIndex < demoConversation.length) {
      // Use pre-scripted question
      processQuery(demoConversation[conversationIndex].query);
    }
  });

  inputField.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const query = inputField.value.trim();
      if (query) {
        processQuery(query);
      } else if (conversationIndex < demoConversation.length) {
        processQuery(demoConversation[conversationIndex].query);
      }
    }
  });

  // Set placeholder to hint at pre-scripted questions
  updatePlaceholder();

  function updatePlaceholder() {
    if (conversationIndex < demoConversation.length) {
      inputField.placeholder = `Try: "${demoConversation[conversationIndex].query}"`;
    } else {
      inputField.placeholder = 'Ask another question...';
    }
  }

  // Update placeholder after each interaction
  const originalAddMessage = addMessage;
  // Check placeholder periodically
  setInterval(updatePlaceholder, 500);
}
