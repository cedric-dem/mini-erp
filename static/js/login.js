const loginTab = document.getElementById('loginTab');
const createTab = document.getElementById('createTab');
const loginForm = document.getElementById('loginForm');
const createForm = document.getElementById('createForm');
const projectAction = document.getElementById('project_action');
const projectJoinField = document.getElementById('projectJoinField');
const projectCreateField = document.getElementById('projectCreateField');
const projectId = document.getElementById('project_id');
const projectName = document.getElementById('project_name');

function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
}

function showMode(mode) {
    const showLogin = mode === 'login';
    loginForm.classList.toggle('hidden', !showLogin);
    createForm.classList.toggle('hidden', showLogin);
    loginTab.classList.toggle('active', showLogin);
    createTab.classList.toggle('active', !showLogin);
}

function updateProjectRequirements() {
    const joining = projectAction.value === 'join';
    projectJoinField.classList.toggle('hidden', !joining);
    projectCreateField.classList.toggle('hidden', joining);
    projectId.required = joining;
    projectName.required = !joining;
}

loginTab.addEventListener('click', () => showMode('login'));
createTab.addEventListener('click', () => showMode('create'));
projectAction.addEventListener('change', updateProjectRequirements);

function getCookie(name) {
    const cookie = document.cookie
        .split('; ')
        .find((entry) => entry.startsWith(`${name}=`));
    return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : null;
}

applyTheme(getCookie('mini-erp-theme') === 'dark' ? 'dark' : 'light');
updateProjectRequirements();