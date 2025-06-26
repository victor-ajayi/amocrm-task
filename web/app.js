document.addEventListener("DOMContentLoaded", function () {
  const loginSection = document.getElementById("login-section");
  const dashboard = document.getElementById("dashboard");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const loginError = document.getElementById("login-error");
  const registerError = document.getElementById("register-error");
  const logoutBtn = document.getElementById("logout-btn");
  const incidentsTableBody = document.querySelector("#incidents-table tbody");
  const tabBtns = document.querySelectorAll(".tab-btn");

  let pollInterval = null;
  const API_BASE = "http://localhost:8000";

  function showDashboard() {
    loginSection.style.display = "none";
    dashboard.style.display = "block";
    startPolling();
  }

  function showLogin() {
    loginSection.style.display = "block";
    dashboard.style.display = "none";
    stopPolling();
  }

  function startPolling() {
    fetchIncidents();
    pollInterval = setInterval(fetchIncidents, 5000);
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }

  async function fetchIncidents() {
    try {
      console.log("Fetching incidents...");
      incidentsTableBody.innerHTML =
        '<tr><td colspan="7" class="loading">Loading incidents...</td></tr>';
      const response = await fetch(`${API_BASE}/api/incidents/`);
      console.log("Incidents response status:", response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const incidents = await response.json();
      console.log("Incidents fetched:", incidents.length);
      renderIncidents(incidents);
    } catch (err) {
      console.error("Failed to fetch incidents:", err);
      incidentsTableBody.innerHTML =
        '<tr><td colspan="7" class="loading">Error loading incidents. Please try again.</td></tr>';
    }
  }

  function formatDate(dateString) {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleString();
  }

  function getStatusBadge(endTime) {
    if (!endTime) {
      return '<span class="status-active">Active</span>';
    } else {
      return '<span class="status-resolved">Resolved</span>';
    }
  }

  function renderIncidents(incidents) {
    incidentsTableBody.innerHTML = "";

    if (incidents.length === 0) {
      incidentsTableBody.innerHTML =
        '<tr><td colspan="7" class="no-incidents">No incidents found</td></tr>';
      return;
    }

    incidents.forEach((incident) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${incident.id}</td>
        <td>${incident.machine}</td>
        <td>${incident.type}</td>
        <td>${incident.value}%</td>
        <td>${formatDate(incident.start_time)}</td>
        <td>${formatDate(incident.end_time)}</td>
        <td>${getStatusBadge(incident.end_time)}</td>
      `;
      incidentsTableBody.appendChild(tr);
    });
  }

  // Tab switching functionality
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const tab = this.dataset.tab;

      // Update active tab
      tabBtns.forEach((b) => b.classList.remove("active"));
      this.classList.add("active");

      // Show/hide forms
      if (tab === "login") {
        loginForm.style.display = "flex";
        registerForm.style.display = "none";
        loginError.textContent = "";
        loginError.style.display = "none";
        registerError.textContent = "";
        registerError.style.display = "none";
      } else {
        loginForm.style.display = "none";
        registerForm.style.display = "flex";
        loginError.textContent = "";
        loginError.style.display = "none";
        registerError.textContent = "";
        registerError.style.display = "none";
      }
    });
  });

  // Login form handler
  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    try {
      const response = await fetch(`${API_BASE}/api/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "include",
      });

      if (response.ok) {
        loginError.textContent = "";
        loginError.style.display = "none";
        showDashboard();
      } else {
        const data = await response.json();
        loginError.textContent = data.error || "Login failed";
        loginError.style.display = "block";
      }
    } catch (err) {
      console.error("Login error:", err);
      loginError.textContent = `Error: ${err.message}`;
      loginError.style.display = "block";
    }
  });

  // Register form handler
  registerForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById(
      "register-confirm-password"
    ).value;

    // Client-side validation
    if (password !== confirmPassword) {
      registerError.textContent = "Passwords do not match";
      registerError.style.display = "block";
      return;
    }

    if (password.length < 6) {
      registerError.textContent = "Password must be at least 6 characters";
      registerError.style.display = "block";
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "include",
      });

      if (response.ok) {
        registerError.textContent = "";
        registerError.style.display = "none";
        showDashboard();
      } else {
        const data = await response.json();
        registerError.textContent = data.error || "Registration failed";
        registerError.style.display = "block";
      }
    } catch (err) {
      console.error("Registration error:", err);
      registerError.textContent = `Error: ${err.message}`;
      registerError.style.display = "block";
    }
  });

  logoutBtn.addEventListener("click", async function () {
    try {
      await fetch(`${API_BASE}/api/logout/`, {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Logout error:", err);
    }
    showLogin();
  });

  // Start with login form
  showLogin();
});
