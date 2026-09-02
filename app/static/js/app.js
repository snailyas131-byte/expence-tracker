document.addEventListener('DOMContentLoaded', () => {
  window.setTimeout(() => document.querySelectorAll('.toast-note').forEach((toast) => toast.remove()), 4000);
  const savedTheme = localStorage.getItem('smart-expense-theme');
  if (savedTheme) document.documentElement.dataset.theme = savedTheme;
  document.querySelectorAll('[data-theme-toggle]').forEach((button) => button.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('smart-expense-theme', theme);
  }));
  document.querySelectorAll('[data-modal-open]').forEach((button) => button.addEventListener('click', () => document.getElementById(button.dataset.modalOpen).showModal()));
  document.querySelectorAll('[data-modal-close]').forEach((button) => button.addEventListener('click', () => button.closest('dialog').close()));
});
