const { model, interactive, questions } = window.MentorXData;
const storageKey = 'mentorx-static-session-v1';
const topicCards = [...document.querySelectorAll('.topic-card')];
const stages = [...document.querySelectorAll('.hint-stage span')];
const hintButton = document.querySelector('#next-hint');
const hintCopy = document.querySelector('#hint-copy');
const toast = document.querySelector('#toast');
const explanationInput = document.querySelector('#explanation-input');
const explanationResult = document.querySelector('#explanation-result');
const questionBankGrid = document.querySelector('#question-bank-grid');
const questionBankFilters = document.querySelector('#question-bank-filters');
const sessionStatus = document.querySelector('.session-status');

let selectedTopic = 'All';
let session = restoreSession();

function freshSession(problemId = 'two-sum') {
  const problem = interactive[problemId] || interactive['two-sum'];
  return {
    problemId,
    startedAt: Date.now(),
    currentHintLevel: 0,
    repeatedAttempts: 0,
    hintRequests: 0,
    breakthroughs: 0,
    difficulty: problem.difficulty,
    explanation: ''
  };
}

function restoreSession() {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    return saved && interactive[saved.problemId] ? saved : freshSession();
  } catch (_error) {
    return freshSession();
  }
}

function saveSession() {
  localStorage.setItem(storageKey, JSON.stringify(session));
}

function currentProblem() {
  return interactive[session.problemId] || interactive['two-sum'];
}

function minutesStuck() {
  return Math.max(0, Math.round((Date.now() - session.startedAt) / 60000));
}

function prediction() {
  const featureValues = [
    minutesStuck(), session.repeatedAttempts, session.hintRequests,
    session.breakthroughs, session.currentHintLevel, session.difficulty
  ];
  const logit = featureValues.reduce(
    (total, value, index) => total + ((value - model.mean[index]) / model.scale[index]) * model.coefficients[index],
    model.intercept
  );
  return 1 / (1 + Math.exp(-logit));
}

function modeFor(probability) {
  if (probability >= 0.72) return ['Guided reset', 'Let’s reset with one manageable step. You are still doing the thinking.'];
  if (probability >= 0.45) return ['Gentle pause', 'Try one focused question before asking for a fuller explanation.'];
  return ['Momentum found', 'You have momentum. Explain or sketch your approach before you code.'];
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 2800);
}

function renderSession() {
  const probability = prediction();
  const [label, cue] = modeFor(probability);
  const score = Math.round(probability * 100);
  document.querySelector('#friction-score').textContent = score;
  document.querySelector('#friction-bar').style.width = `${score}%`;
  document.querySelector('#friction-label').textContent = label;
  document.querySelector('#time-signal').textContent = `${minutesStuck()}m`;
  document.querySelector('#retry-signal').textContent = session.repeatedAttempts;
  document.querySelector('#hint-signal').textContent = session.hintRequests;
  document.querySelector('#cue-title').textContent = `${model.name} recommendation`;
  document.querySelector('#cue-copy').textContent = cue;
  sessionStatus.innerHTML = `<i></i> ${model.name} active`;
  stages.forEach((stage, index) => stage.classList.toggle('active', index === Math.max(0, session.currentHintLevel - 1)));
  hintButton.innerHTML = session.currentHintLevel >= currentProblem().hints.length ? 'Reflect on the approach <span>→</span>' : 'I need another hint <span>→</span>';
  saveSession();
}

function setProblem(problemId) {
  const problem = interactive[problemId];
  if (!problem) return;
  session = freshSession(problemId);
  document.querySelector('#problem-title').textContent = problem.title;
  document.querySelector('#problem-context').textContent = problem.context;
  hintCopy.textContent = problem.hints[0];
  explanationInput.value = '';
  explanationResult.textContent = '';
  topicCards.forEach((card) => card.classList.toggle('selected', card.dataset.problemId === problemId));
  renderSession();
}

function evaluateExplanation() {
  const explanation = explanationInput.value.trim();
  if (explanation.length < 10) {
    explanationResult.textContent = 'Write at least one complete sentence about your approach first.';
    return;
  }
  const normalized = explanation.toLowerCase();
  const concepts = currentProblem().concepts;
  const matched = concepts.filter((group) => group.some((term) => normalized.includes(term)));
  const missing = concepts.filter((group) => !matched.includes(group));
  const coverage = Math.round((matched.length / concepts.length) * 65);
  const clarity = explanation.split(/\s+/).length >= 35 ? 15 : explanation.split(/\s+/).length >= 15 ? 8 : 2;
  const complexity = normalized.includes('o(') || normalized.includes('complexity') ? 10 : 0;
  const reasoning = ['because', 'therefore', 'so that', 'why'].some((word) => normalized.includes(word)) ? 10 : 0;
  const score = Math.min(100, coverage + clarity + complexity + reasoning);
  const level = score >= 75 ? 'strong' : score >= 50 ? 'developing' : 'needs reflection';
  const guidance = score >= 75
    ? 'Strong explanation. Now implement it without looking at another hint.'
    : score >= 50
      ? 'Good direction. Explain why the approach works and add the missing idea.'
      : 'Start with the main technique, then describe the decision made at each step.';
  explanationResult.textContent = `${score}/100 · ${level}. ${guidance}${missing.length ? ` Still add: ${missing.map((group) => group[0]).join(', ')}.` : ''}`;
  session.explanation = explanation;
  saveSession();
}

function renderQuestionBank() {
  const topics = ['All', ...new Set(questions.map((question) => question.topic))];
  questionBankFilters.replaceChildren(...topics.map((topic) => {
    const button = document.createElement('button');
    button.className = `filter-button${topic === selectedTopic ? ' selected' : ''}`;
    button.textContent = topic;
    button.addEventListener('click', () => { selectedTopic = topic; renderQuestionBank(); });
    return button;
  }));
  const visibleQuestions = questions.filter((question) => selectedTopic === 'All' || question.topic === selectedTopic);
  questionBankGrid.replaceChildren(...visibleQuestions.map((question) => {
    const card = document.createElement('article');
    card.className = 'practice-question';
    const title = document.createElement('strong');
    title.textContent = question.title;
    const topic = document.createElement('span');
    topic.textContent = `${question.topic} · ${question.difficulty}`;
    const actions = document.createElement('div');
    actions.className = 'question-actions';
    const link = document.createElement('a');
    link.href = question.url;
    link.target = '_blank';
    link.rel = 'noreferrer';
    link.textContent = 'Open on LeetCode';
    actions.append(link);
    if (interactive[question.slug]) {
      const practice = document.createElement('button');
      practice.textContent = 'Practice here';
      practice.addEventListener('click', () => {
        setProblem(question.slug);
        document.querySelector('#mentor-space').scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
      actions.append(practice);
    }
    card.append(title, topic, actions);
    return card;
  }));
}

function decodeJwt(token) {
  const segment = token.split('.')[1];
  return JSON.parse(decodeURIComponent(atob(segment.replace(/-/g, '+').replace(/_/g, '/')).split('').map((character) => `%${(`00${character.charCodeAt(0).toString(16)}`).slice(-2)}`).join('')));
}

function handleGoogleCredential(response) {
  try {
    const profile = decodeJwt(response.credential);
    localStorage.setItem('mentorx-google-profile', JSON.stringify({ name: profile.name, email: profile.email }));
    document.querySelector('.profile strong').textContent = profile.name || 'Google learner';
    document.querySelector('.profile small').textContent = profile.email || 'Signed in with Google';
    showToast(`Welcome, ${profile.given_name || profile.name || 'learner'}.`);
  } catch (_error) {
    showToast('Google returned a credential that could not be read.');
  }
}

function setupGoogleSignIn() {
  const container = document.querySelector('#google-signin');
  const clientId = window.MENTORX_GOOGLE_CLIENT_ID;
  if (!clientId || !clientId.endsWith('.apps.googleusercontent.com')) {
    const button = document.createElement('button');
    button.className = 'google-placeholder';
    button.textContent = 'Google sign in';
    button.addEventListener('click', () => showToast('Add a Web OAuth client ID in google-config.js to activate Google sign-in.'));
    container.replaceChildren(button);
    return;
  }
  const initialize = () => {
    if (!window.google?.accounts?.id) return window.setTimeout(initialize, 100);
    window.google.accounts.id.initialize({ client_id: clientId, callback: handleGoogleCredential, auto_select: false });
    window.google.accounts.id.renderButton(container, { theme: 'outline', size: 'medium', text: 'signin_with', shape: 'pill' });
  };
  initialize();
}

hintButton.addEventListener('click', () => {
  const problem = currentProblem();
  if (session.currentHintLevel >= problem.hints.length) return showToast('You have reached the final explanation. Try describing it in your own words.');
  session.currentHintLevel += 1;
  session.hintRequests += 1;
  hintCopy.textContent = problem.hints[session.currentHintLevel - 1];
  renderSession();
  showToast(`Hint ${session.currentHintLevel} unlocked — one step closer.`);
});

document.querySelector('#retry-button').addEventListener('click', () => { session.repeatedAttempts += 1; renderSession(); showToast('Retry recorded. MentorX will adjust its next nudge.'); });
document.querySelector('#breakthrough-button').addEventListener('click', () => { session.breakthroughs += 1; renderSession(); showToast('Momentum detected. Explain the approach before coding.'); });
document.querySelector('#understand-button').addEventListener('click', () => { document.querySelector('#explanation-input').focus(); showToast('Great. Explain your approach in your own words.'); });
document.querySelector('#evaluate-explanation').addEventListener('click', evaluateExplanation);
topicCards.forEach((card) => card.addEventListener('click', () => setProblem(card.dataset.problemId)));
document.querySelector('#library-button').addEventListener('click', () => document.querySelector('#question-bank').scrollIntoView({ behavior: 'smooth' }));
document.querySelector('#help-button').addEventListener('click', () => showToast('Choose a problem, request one hint at a time, then explain why your approach works.'));
document.querySelector('.dots').addEventListener('click', () => showToast('Your current learning session is saved in this browser.'));
document.querySelector('.menu-button').addEventListener('click', () => document.querySelector('.sidebar').classList.toggle('mobile-open'));

const savedProfile = JSON.parse(localStorage.getItem('mentorx-google-profile') || 'null');
if (savedProfile) {
  document.querySelector('.profile strong').textContent = savedProfile.name || 'Google learner';
  document.querySelector('.profile small').textContent = savedProfile.email || 'Signed in with Google';
}
setProblem(session.problemId);
renderQuestionBank();
setupGoogleSignIn();
window.setInterval(renderSession, 30_000);
